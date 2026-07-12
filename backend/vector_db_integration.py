"""
SANTINEL Phase 2 — Vector DB Integration
Pinecone for storing + retrieving high-quality coaching patterns
Auto-improvement loop for LLM fine-tuning
"""

import os
import json
from typing import List, Dict, Optional
from datetime import datetime
import uuid

try:
    import pinecone
except ImportError:
    print("Warning: Pinecone not installed. Install: pip install pinecone-client")
    pinecone = None

try:
    from openai import OpenAI
except ImportError:
    print("Warning: OpenAI not installed. Install: pip install openai")
    OpenAI = None

class VectorDBManager:
    """
    Manages vector database operations for coaching patterns
    Stores high-rated coaching advice for retrieval + fine-tuning
    """
    
    def __init__(self, pinecone_api_key: str, openai_api_key: str, index_name: str = "coaching-patterns"):
        """Initialize Pinecone + OpenAI clients"""
        
        self.pinecone_api_key = pinecone_api_key
        self.openai_api_key = openai_api_key
        self.index_name = index_name
        self.initialized = False
        
        try:
            if pinecone:
                pinecone.init(api_key=pinecone_api_key)
                self.index = pinecone.Index(index_name)
                print(f"✅ Pinecone index '{index_name}' initialized")
            
            if OpenAI:
                self.openai_client = OpenAI(api_key=openai_api_key)
                print("✅ OpenAI client initialized")
            
            self.initialized = True
        except Exception as e:
            print(f"⚠️ Vector DB initialization error: {e}")
            print("Continuing without vector DB (will use fallback)")
            self.initialized = False
    
    def create_embedding(self, text: str) -> Optional[List[float]]:
        """Generate embedding for text using OpenAI"""
        
        if not self.initialized or not OpenAI:
            return None
        
        try:
            response = self.openai_client.embeddings.create(
                input=text,
                model="text-embedding-3-small"
            )
            return response.data[0].embedding
        except Exception as e:
            print(f"Error creating embedding: {e}")
            return None
    
    def store_coaching_pattern(self, 
                               coaching_text: str,
                               situation_type: str,
                               frameworks_used: List[str],
                               rating: int,
                               quality_score: float,
                               session_id: str,
                               success_outcome: bool,
                               negotiation_type: str = "general",
                               metadata: Dict = None) -> bool:
        """
        Store high-quality coaching pattern in vector DB
        Called after user rates coaching 4-5 stars
        """
        
        if not self.initialized:
            print("⚠️ Vector DB not initialized")
            return False
        
        try:
            # Generate embedding
            embedding = self.create_embedding(coaching_text)
            if not embedding:
                return False
            
            # Create pattern ID
            pattern_id = f"pat_{uuid.uuid4().hex[:12]}"
            
            # Build metadata
            pattern_metadata = {
                "pattern_id": pattern_id,
                "coaching_text": coaching_text,
                "situation_type": situation_type,
                "frameworks_used": frameworks_used,
                "rating": rating,
                "quality_score": quality_score,
                "session_id": session_id,
                "success_outcome": success_outcome,
                "negotiation_type": negotiation_type,
                "timestamp": datetime.now().isoformat(),
                **(metadata or {})
            }
            
            # Upsert to Pinecone
            self.index.upsert(
                vectors=[(
                    pattern_id,
                    embedding,
                    pattern_metadata
                )]
            )
            
            print(f"✅ Pattern stored: {pattern_id} (rating: {rating})")
            return True
        
        except Exception as e:
            print(f"❌ Error storing pattern: {e}")
            return False
    
    def find_similar_patterns(self, 
                             situation_text: str,
                             situation_type: str,
                             limit: int = 5) -> List[Dict]:
        """
        Find similar past coaching patterns for current situation
        Used to enhance current coaching with proven patterns
        """
        
        if not self.initialized:
            print("⚠️ Vector DB not initialized")
            return []
        
        try:
            # Generate embedding for current situation
            embedding = self.create_embedding(situation_text)
            if not embedding:
                return []
            
            # Query similar patterns
            results = self.index.query(
                vector=embedding,
                filter={"situation_type": {"$eq": situation_type}},
                top_k=limit,
                include_metadata=True
            )
            
            # Format results
            patterns = []
            for match in results.get("matches", []):
                patterns.append({
                    "pattern_id": match["metadata"]["pattern_id"],
                    "coaching_text": match["metadata"]["coaching_text"],
                    "rating": match["metadata"]["rating"],
                    "similarity": match["score"],
                    "frameworks": match["metadata"]["frameworks_used"],
                    "success_outcome": match["metadata"]["success_outcome"]
                })
            
            print(f"✅ Found {len(patterns)} similar patterns")
            return patterns
        
        except Exception as e:
            print(f"❌ Error finding patterns: {e}")
            return []
    
    def get_framework_performance(self, situation_type: str) -> Dict:
        """
        Get effectiveness scores for each framework on situation type
        Returns frameworks ranked by effectiveness
        """
        
        if not self.initialized:
            return {}
        
        try:
            # Query for all patterns of this situation type
            results = self.index.query(
                vector=[0.0] * 1536,  # Dummy vector (ignored with filter)
                filter={"situation_type": {"$eq": situation_type}},
                top_k=1000,
                include_metadata=True
            )
            
            # Aggregate framework performance
            framework_stats = {}
            
            for match in results.get("matches", []):
                metadata = match["metadata"]
                frameworks = metadata.get("frameworks_used", [])
                rating = metadata.get("rating", 0)
                success = metadata.get("success_outcome", False)
                
                for fw in frameworks:
                    if fw not in framework_stats:
                        framework_stats[fw] = {
                            "ratings": [],
                            "successes": 0,
                            "count": 0
                        }
                    
                    framework_stats[fw]["ratings"].append(rating)
                    if success:
                        framework_stats[fw]["successes"] += 1
                    framework_stats[fw]["count"] += 1
            
            # Calculate effectiveness scores
            framework_performance = {}
            for fw, stats in framework_stats.items():
                avg_rating = sum(stats["ratings"]) / len(stats["ratings"]) if stats["ratings"] else 0
                success_rate = (stats["successes"] / stats["count"] * 100) if stats["count"] > 0 else 0
                effectiveness = (avg_rating / 5 * 60) + (success_rate / 100 * 40)  # 60% rating, 40% success
                
                framework_performance[fw] = {
                    "avg_rating": round(avg_rating, 2),
                    "success_rate": round(success_rate, 1),
                    "usage_count": stats["count"],
                    "effectiveness_score": round(effectiveness, 1)
                }
            
            # Sort by effectiveness
            sorted_fw = dict(sorted(
                framework_performance.items(),
                key=lambda x: x[1]["effectiveness_score"],
                reverse=True
            ))
            
            print(f"✅ Framework performance calculated: {list(sorted_fw.keys())}")
            return sorted_fw
        
        except Exception as e:
            print(f"❌ Error calculating framework performance: {e}")
            return {}
    
    def export_for_finetuning(self, min_rating: int = 4, limit: int = 100) -> Dict:
        """
        Export high-quality patterns for LLM fine-tuning
        Only patterns with rating >= min_rating
        """
        
        if not self.initialized:
            return {}
        
        try:
            # Query high-rated patterns
            results = self.index.query(
                vector=[0.0] * 1536,  # Dummy vector
                filter={"rating": {"$gte": min_rating}},
                top_k=limit,
                include_metadata=True
            )
            
            # Extract training examples
            training_examples = []
            situation_type_counts = {}
            framework_usage = {}
            
            for match in results.get("matches", []):
                metadata = match["metadata"]
                
                example = {
                    "situation": metadata.get("coaching_text", ""),
                    "frameworks": metadata.get("frameworks_used", []),
                    "rating": metadata.get("rating", 0),
                    "success_outcome": metadata.get("success_outcome", False),
                    "quality_score": metadata.get("quality_score", 0)
                }
                training_examples.append(example)
                
                # Track stats
                sit_type = metadata.get("situation_type", "custom")
                situation_type_counts[sit_type] = situation_type_counts.get(sit_type, 0) + 1
                
                for fw in metadata.get("frameworks_used", []):
                    framework_usage[fw] = framework_usage.get(fw, 0) + 1
            
            # Calculate weights
            total = len(training_examples)
            situation_weights = {
                k: round(v / total, 2) for k, v in situation_type_counts.items()
            }
            
            total_fw_usage = sum(framework_usage.values())
            framework_weights = {
                k: round(v / total_fw_usage, 2) for k, v in framework_usage.items()
            }
            
            export_data = {
                "metadata": {
                    "export_date": datetime.now().isoformat(),
                    "total_patterns": len(training_examples),
                    "min_rating_threshold": min_rating
                },
                "training_examples": training_examples,
                "situation_type_weights": situation_weights,
                "framework_weights": framework_weights,
                "recommendations": {
                    "primary_frameworks": list(sorted(framework_weights.items(), 
                                                      key=lambda x: x[1], reverse=True)[:3]),
                    "strong_situation_types": list(sorted(situation_weights.items(),
                                                          key=lambda x: x[1], reverse=True)[:3])
                }
            }
            
            print(f"✅ Exported {len(training_examples)} patterns for fine-tuning")
            return export_data
        
        except Exception as e:
            print(f"❌ Error exporting for fine-tuning: {e}")
            return {}
    
    def get_stats(self) -> Dict:
        """Get vector DB statistics"""
        
        if not self.initialized:
            return {"status": "Not initialized"}
        
        try:
            stats = self.index.describe_index_stats()
            return {
                "status": "✅ Ready",
                "total_vectors": stats.get("total_vector_count", 0),
                "index_name": self.index_name,
                "dimension": stats.get("dimension", 1536)
            }
        except Exception as e:
            print(f"Error getting stats: {e}")
            return {"status": f"Error: {e}"}


# ============== MOCK VERSION (for testing without Pinecone) ==============

class MockVectorDBManager:
    """
    Mock Vector DB for testing
    Stores patterns in memory (not persistent)
    """
    
    def __init__(self):
        self.patterns = []
        self.initialized = True
        print("✅ Mock Vector DB initialized (no Pinecone required)")
    
    def store_coaching_pattern(self, **kwargs) -> bool:
        """Mock store"""
        pattern = {
            "pattern_id": f"pat_{len(self.patterns)}",
            **kwargs
        }
        self.patterns.append(pattern)
        print(f"✅ Mock pattern stored: {pattern['pattern_id']}")
        return True
    
    def find_similar_patterns(self, situation_text: str, situation_type: str, limit: int = 5) -> List[Dict]:
        """Mock find"""
        similar = [
            {
                "pattern_id": p["pattern_id"],
                "coaching_text": p.get("coaching_text", "")[:50] + "...",
                "rating": p.get("rating", 0),
                "similarity": 0.85,
                "success_outcome": p.get("success_outcome", False)
            }
            for p in self.patterns[:limit]
            if p.get("situation_type") == situation_type
        ]
        print(f"✅ Mock found {len(similar)} patterns")
        return similar
    
    def get_framework_performance(self, situation_type: str) -> Dict:
        """Mock performance"""
        return {
            "CBT": {"effectiveness_score": 92.5, "usage_count": 42},
            "NLP": {"effectiveness_score": 88.0, "usage_count": 38},
            "TA": {"effectiveness_score": 85.5, "usage_count": 35}
        }
    
    def export_for_finetuning(self, min_rating: int = 4, limit: int = 100) -> Dict:
        """Mock export"""
        high_quality = [p for p in self.patterns if p.get("rating", 0) >= min_rating][:limit]
        return {
            "metadata": {"total_patterns": len(high_quality)},
            "training_examples": high_quality,
            "situation_type_weights": {"price": 0.4, "timeline": 0.3, "conflict": 0.3}
        }
    
    def get_stats(self) -> Dict:
        """Mock stats"""
        return {
            "status": "✅ Mock Ready",
            "total_patterns": len(self.patterns),
            "mode": "Mock (no Pinecone)"
        }


# ============== INITIALIZATION ==============

def get_vector_db_manager(use_mock: bool = False) -> object:
    """
    Get Vector DB Manager (Pinecone or Mock)
    """
    
    if use_mock:
        return MockVectorDBManager()
    
    pinecone_key = os.getenv("PINECONE_API_KEY")
    openai_key = os.getenv("OPENAI_API_KEY")
    
    if not pinecone_key or not openai_key:
        print("⚠️ Missing API keys, using Mock Vector DB")
        return MockVectorDBManager()
    
    return VectorDBManager(pinecone_key, openai_key)