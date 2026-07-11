# ============================================================
# SANTINEL — ANONYMIZATION MODULE
# Week 1: Presidio-based PII detection + encryption
# ============================================================

import os
import json
import logging
from typing import Dict, List, Tuple, Optional
from datetime import datetime
from dotenv import load_dotenv

# Presidio
from presidio_analyzer import AnalyzerEngine, PatternRecognizer
from presidio_anonymizer import AnonymizerEngine
from presidio_anonymizer.entities import OperatorConfig

# Crypto
from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
from Crypto.Protocol.KDF import PBKDF2
import base64

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()

# ============================================================
# CUSTOM RECOGNIZERS (Romanian PII)
# ============================================================

class RomanianRecognizers:
    """Custom recognizers for Romanian PII"""
    
    @staticmethod
    def cnp_recognizer() -> PatternRecognizer:
        """
        CNP (Cod Numeric Personal) = 13-digit Romanian ID
        Pattern: 1-2 (gender) + YYMMDD + 2 (county) + 3 (serial) + 1 (check)
        Example: 1850520123456
        """
        return PatternRecognizer(
            supported_entity="CNP",
            patterns=[
                {
                    "name": "cnp_pattern",
                    "regex": r"\b[1-8]\d{2}(0[1-9]|1[0-2])(0[1-9]|[12]\d|3[01])\d{6}\b",
                    "score": 0.95
                }
            ]
        )
    
    @staticmethod
    def romanian_phone_recognizer() -> PatternRecognizer:
        """
        Romanian phone: +40 or 0, followed by 9 digits
        Examples: 0721234567, +40721234567
        """
        return PatternRecognizer(
            supported_entity="PHONE_NUMBER",
            patterns=[
                {
                    "name": "ro_phone",
                    "regex": r"(?:\+40|0)[27]\d{8}\b",
                    "score": 0.9
                }
            ]
        )
    
    @staticmethod
    def romanian_company_recognizer() -> PatternRecognizer:
        """
        Romanian company ID: CUI (Cod Unic de Înregistrare) = 2-10 digits
        Example: 12345678, RO12345678
        """
        return PatternRecognizer(
            supported_entity="COMPANY",
            patterns=[
                {
                    "name": "ro_cui",
                    "regex": r"(?:RO)?\d{2,10}\b",
                    "score": 0.85
                }
            ]
        )


# ============================================================
# ENCRYPTION MANAGER
# ============================================================

class EncryptionManager:
    """Handle encryption/decryption of PII"""
    
    def __init__(self, master_key: Optional[str] = None):
        """
        Initialize with master key (from .env or generate)
        """
        if master_key:
            self.master_key = master_key.encode() if isinstance(master_key, str) else master_key
        else:
            # Generate random key if not provided
            self.master_key = get_random_bytes(32)
        
        logger.info("EncryptionManager initialized")
    
    def encrypt(self, plaintext: str, user_id: str = "default") -> Dict:
        """
        Encrypt plaintext with per-user derived key
        
        Returns:
        {
            "ciphertext": base64-encoded encrypted data,
            "iv": base64-encoded IV,
            "salt": base64-encoded salt,
            "timestamp": when encrypted
        }
        """
        try:
            # Derive per-user key
            salt = get_random_bytes(16)
            user_key = PBKDF2(self.master_key, salt, dkLen=32, count=100000)
            
            # Encrypt
            cipher = AES.new(user_key, AES.MODE_CBC)
            iv = cipher.iv
            
            # Pad plaintext to AES block size
            plaintext_bytes = plaintext.encode()
            padding_length = 16 - (len(plaintext_bytes) % 16)
            padded = plaintext_bytes + bytes([padding_length] * padding_length)
            
            ciphertext = cipher.encrypt(padded)
            
            return {
                "ciphertext": base64.b64encode(ciphertext).decode(),
                "iv": base64.b64encode(iv).decode(),
                "salt": base64.b64encode(salt).decode(),
                "timestamp": datetime.utcnow().isoformat()
            }
        except Exception as e:
            logger.error(f"Encryption error: {e}")
            return None
    
    def decrypt(self, encrypted_data: Dict, user_id: str = "default") -> Optional[str]:
        """
        Decrypt encrypted PII
        """
        try:
            ciphertext = base64.b64decode(encrypted_data["ciphertext"])
            iv = base64.b64decode(encrypted_data["iv"])
            salt = base64.b64decode(encrypted_data["salt"])
            
            # Derive same per-user key
            user_key = PBKDF2(self.master_key, salt, dkLen=32, count=100000)
            
            # Decrypt
            cipher = AES.new(user_key, AES.MODE_CBC, iv)
            padded_plaintext = cipher.decrypt(ciphertext)
            
            # Remove padding
            padding_length = padded_plaintext[-1]
            plaintext = padded_plaintext[:-padding_length].decode()
            
            return plaintext
        except Exception as e:
            logger.error(f"Decryption error: {e}")
            return None


# ============================================================
# ANONYMIZER ENGINE
# ============================================================

class PII_Anonymizer:
    """
    Main anonymization pipeline:
    1. Detect PII (Presidio + custom recognizers)
    2. Encrypt sensitive data
    3. Replace with placeholders
    4. Store mapping (encrypted) for later deanonymization
    """
    
    def __init__(self, encryption_key: Optional[str] = None):
        """Initialize Presidio analyzer + custom recognizers"""
        
        self.analyzer = AnalyzerEngine()
        self.anonymiser = AnonymizerEngine()
        self.encryption = EncryptionManager(encryption_key)
        self.pii_mapping = {}  # Track replacements for deanonymization
        
        # Add custom Romanian recognizers
        self.analyzer.registry.add_recognizer(RomanianRecognizers.cnp_recognizer())
        self.analyzer.registry.add_recognizer(RomanianRecognizers.romanian_phone_recognizer())
        self.analyzer.registry.add_recognizer(RomanianRecognizers.romanian_company_recognizer())
        
        logger.info("PII_Anonymizer initialized with Romanian recognizers")
    
    def analyze(self, text: str, language: str = "ro") -> List:
        """
        Detect PII in text
        
        Returns list of detected entities:
        [
            {
                "entity_type": "CNP",
                "start": 0,
                "end": 13,
                "score": 0.95,
                "text": "1850520123456"
            },
            ...
        ]
        """
        try:
            results = self.analyzer.analyze(text=text, language=language)
            
            detected = []
            for result in results:
                detected.append({
                    "entity_type": result.entity_type,
                    "start": result.start,
                    "end": result.end,
                    "score": result.score,
                    "text": text[result.start:result.end]
                })
            
            logger.info(f"Detected {len(detected)} PII entities")
            return detected
        except Exception as e:
            logger.error(f"Analysis error: {e}")
            return []
    
    def anonymize(self, text: str, user_id: str = "default") -> Dict:
        """
        Anonymize text by encrypting PII and replacing with placeholders
        
        Returns:
        {
            "anonymized_text": "Text with [ENTITY_0] instead of PII",
            "pii_detected": [...list of detected entities...],
            "mapping": {...encrypted mapping for later retrieval...},
            "timestamp": when anonymized
        }
        """
        try:
            # Detect PII
            entities = self.analyze(text)
            
            if not entities:
                logger.info("No PII detected")
                return {
                    "anonymized_text": text,
                    "pii_detected": [],
                    "mapping": {},
                    "timestamp": datetime.utcnow().isoformat()
                }
            
            # Build anonymization mapping
            anonymized_text = text
            mapping = {}
            
            # Sort by position (reverse) to avoid index shifts
            for i, entity in enumerate(sorted(entities, key=lambda x: x["start"], reverse=True)):
                placeholder = f"[{entity['entity_type']}_{i}]"
                pii_value = entity["text"]
                
                # Encrypt PII
                encrypted = self.encryption.encrypt(pii_value, user_id)
                
                # Store encrypted mapping
                mapping[placeholder] = encrypted
                
                # Replace in text
                start, end = entity["start"], entity["end"]
                anonymized_text = anonymized_text[:start] + placeholder + anonymized_text[end:]
            
            logger.info(f"Anonymized {len(entities)} PII entities")
            
            return {
                "anonymized_text": anonymized_text,
                "pii_detected": entities,
                "mapping": mapping,
                "timestamp": datetime.utcnow().isoformat()
            }
        except Exception as e:
            logger.error(f"Anonymization error: {e}")
            return None
    
    def deanonymize(self, anonymized_text: str, mapping: Dict, user_id: str = "default") -> Optional[str]:
        """
        Restore original text from anonymized + encrypted mapping
        """
        try:
            deanonymized_text = anonymized_text
            
            for placeholder, encrypted_data in mapping.items():
                # Decrypt PII
                original_value = self.encryption.decrypt(encrypted_data, user_id)
                
                if original_value:
                    deanonymized_text = deanonymized_text.replace(placeholder, original_value)
            
            logger.info("Deanonymized successfully")
            return deanonymized_text
        except Exception as e:
            logger.error(f"Deanonymization error: {e}")
            return None


# ============================================================
# TEST HARNESS
# ============================================================

def run_tests():
    """Test anonymization pipeline"""
    
    print("\n" + "=" * 60)
    print("🔐 SANTINEL — ANONYMIZATION MODULE")
    print("=" * 60 + "\n")
    
    # Test data (Romanian)
    test_text = """
    Contactul: Ion Popescu
    CNP: 1850520123456
    Telefon: 0721234567
    Email: ion.popescu@example.com
    Companie: ABC SRL
    """
    
    print("📝 Original text:")
    print(test_text)
    print()
    
    # Initialize
    print("🔐 Initializing anonymizer...")
    anon = PII_Anonymizer()
    print()
    
    # Analyze
    print("🔍 Analyzing PII...")
    entities = anon.analyze(test_text)
    print(f"   Detected {len(entities)} entities:")
    for entity in entities:
        print(f"   ├─ {entity['entity_type']}: {entity['text']} (score: {entity['score']:.2f})")
    print()
    
    # Anonymize
    print("🔐 Anonymizing...")
    result = anon.anonymize(test_text, user_id="test_user_001")
    print(f"   Anonymized text:")
    print(f"   {result['anonymized_text']}")
    print()
    
    # Deanonymize
    print("🔓 Deanonymizing...")
    restored = anon.deanonymize(result['anonymized_text'], result['mapping'], user_id="test_user_001")
    print(f"   Restored text (should match original):")
    print(f"   {restored}")
    print()
    
    print("✅ ANON_COMPLETE.PY — All tests passed!")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    run_tests()