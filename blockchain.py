import hashlib
import json
import time
from typing import List, Dict, Any, Tuple

class Blockchain:
    def __init__(self):
        self.chain: List[Dict[str, Any]] = []
        self.pending_transactions: List[Dict[str, Any]] = []
        # Smart Contract State Emulation
        self.certificates: Dict[str, Dict[str, Any]] = {}
        self.certificate_hashes: List[str] = []
        self.owner = "0xSystemOwner"
        
        # Create genesis block
        self.create_block(previous_hash="0000000000000000000000000000000000000000000000000000000000000000", nonce=100)

    @staticmethod
    def hash_payload(payload: Dict[str, Any]) -> str:
        """
        Canonical serialization: alphabetically sorted keys, stripped whitespace
        """
        canonical_string = json.dumps(payload, sort_keys=True, separators=(',', ':'))
        return hashlib.sha256(canonical_string.encode()).hexdigest()

    def create_block(self, previous_hash: str, nonce: int) -> Dict[str, Any]:
        block = {
            'index': len(self.chain) + 1,
            'timestamp': int(time.time()),
            'transactions': self.pending_transactions,
            'previous_hash': previous_hash,
            'nonce': nonce,
        }
        # Compute block hash
        block['hash'] = self.hash_payload(block)
        
        self.pending_transactions = []
        self.chain.append(block)
        return block

    def get_last_block(self) -> Dict[str, Any]:
        return self.chain[-1]

    def mine_pending_transactions(self, miner_address: str):
        last_block = self.get_last_block()
        previous_hash = last_block['hash']
        # Simplified proof of work
        nonce = self.proof_of_work(previous_hash)
        
        return self.create_block(previous_hash, nonce)

    def proof_of_work(self, previous_hash: str) -> int:
        nonce = 0
        while not self.valid_proof(self.pending_transactions, previous_hash, nonce):
            nonce += 1
        return nonce

    def valid_proof(self, transactions: List[Dict[str, Any]], previous_hash: str, nonce: int) -> bool:
        guess = f'{transactions}{previous_hash}{nonce}'.encode()
        guess_hash = hashlib.sha256(guess).hexdigest()
        return guess_hash[:3] == "000"  # Adjusted difficulty for speed in demo

    # --- Smart Contract Methods (Emulated) ---
    
    def issue_certificate(self, cert_hash: str, student_id: str, issuer: str, metadata_uri: str = "") -> Tuple[bool, str]:
        if cert_hash in self.certificates:
            return False, "Certificate hash already registered"

        timestamp = int(time.time())
        self.certificates[cert_hash] = {
            "certHash": cert_hash,
            "studentId": student_id,
            "metadataUri": metadata_uri,
            "issueTimestamp": timestamp,
            "issuer": issuer,
            "isValid": True,
            "isRevoked": False,
            "revokeReason": ""
        }
        self.certificate_hashes.append(cert_hash)
        
        tx = {
            "tx_hash": hashlib.sha256(f"{cert_hash}{timestamp}".encode()).hexdigest(),
            "cert_hash": cert_hash,
            "student_id": student_id,
            "issuer": issuer,
            "status": "ISSUED"
        }
        self.pending_transactions.append(tx)
        
        self.mine_pending_transactions(issuer)
        return True, "Certificate Issued"

    def verify_certificate(self, cert_hash: str) -> Dict[str, Any]:
        if cert_hash not in self.certificates:
            return {
                "isFound": False,
                "isValid": False,
                "studentId": "",
                "issueTimestamp": 0,
                "issuer": None,
                "isRevoked": False,
                "revokeReason": ""
            }
            
        cert = self.certificates[cert_hash]
        is_valid = cert["isValid"] and not cert["isRevoked"]
        return {
            "isFound": True,
            "isValid": is_valid,
            "studentId": cert["studentId"],
            "issueTimestamp": cert["issueTimestamp"],
            "issuer": cert["issuer"],
            "isRevoked": cert["isRevoked"],
            "revokeReason": cert["revokeReason"]
        }

    def revoke_certificate(self, cert_hash: str, reason: str, revoker: str) -> Tuple[bool, str]:
        if cert_hash not in self.certificates:
            return False, "Certificate not found"
        if self.certificates[cert_hash]["isRevoked"]:
            return False, "Certificate already revoked"
            
        self.certificates[cert_hash]["isRevoked"] = True
        self.certificates[cert_hash]["isValid"] = False
        self.certificates[cert_hash]["revokeReason"] = reason
        
        timestamp = int(time.time())
        tx = {
            "tx_hash": hashlib.sha256(f"revoke_{cert_hash}{timestamp}".encode()).hexdigest(),
            "cert_hash": cert_hash,
            "status": "REVOKED",
            "reason": reason
        }
        self.pending_transactions.append(tx)
        self.mine_pending_transactions(revoker)
        return True, "Certificate Revoked"
