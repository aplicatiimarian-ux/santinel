## Integration with Backend

```python
# backend/vector_db_integration.py

import pinecone
from openai import OpenAI

class VectorDBManager:
    def __init__(self, pinecone_api_key, openai_api_key):
        pinecone.init(api_key=pinecone_api_key)
        self.index = pinecone.Index("coaching-patterns")
        self.openai = OpenAI(api_key=openai_api_key)
    
    def store_pattern(self, coaching_text, metadata):
        """Store high-rated coaching pattern"""
        embedding = self.openai.Embedding.create(
            input=coaching_text,
            model="text-embedding-3-small"
        )["data"][0]["embedding"]
        
        self.index.upsert(
            vectors=[(
                metadata["pattern_id"],
                embedding,
                metadata
            )]
        )
    
    def find_similar_patterns(self, situation_text, situation_type, limit=5):
        """Find similar past coaching for current situation"""
        embedding = self.openai.Embedding.create(
            input=situation_text,
            model="text-embedding-3-small"
        )["data"][0]["embedding"]
        
        results = self.index.query(
            vector=embedding,
            filter={"situation_type": {"$eq": situation_type}},
            top_k=limit,
            include_metadata=True
        )
        
        return results
```

## Next Steps (Phase 2)

1. ✅ Design schema (THIS DOCUMENT)
2. Setup Pinecone integration
3. Build fine-tuning pipeline
4. Implement A/B testing
5. Auto-improvement loop
6. Performance monitoring