import pytest
from blockchain import Blockchain

def test_genesis_block():
    bc = Blockchain()
    assert len(bc.chain) == 1
    assert bc.chain[0]['index'] == 1
    assert bc.chain[0]['previous_hash'] == "0000000000000000000000000000000000000000000000000000000000000000"

def test_issue_certificate():
    bc = Blockchain()
    payload = {"student": "Alice", "grade": "A"}
    cert_hash = Blockchain.hash_payload(payload)
    
    success, msg = bc.issue_certificate(cert_hash, "STU-1", "0xIssuer")
    assert success
    
    verify = bc.verify_certificate(cert_hash)
    assert verify['isFound'] is True
    assert verify['isValid'] is True
    
    assert len(bc.chain) == 2
    assert bc.chain[-1]['transactions'][0]['cert_hash'] == cert_hash

def test_tamper_detection():
    bc = Blockchain()
    payload1 = {"student": "Alice", "grade": "A"}
    payload2 = {"student": "Alice", "grade": "A+"}
    
    hash1 = Blockchain.hash_payload(payload1)
    hash2 = Blockchain.hash_payload(payload2)
    
    assert hash1 != hash2
    
    bc.issue_certificate(hash1, "STU-1", "0xIssuer")
    
    verify_tampered = bc.verify_certificate(hash2)
    assert verify_tampered['isFound'] is False

def test_revoke_certificate():
    bc = Blockchain()
    payload = {"student": "Bob", "grade": "B"}
    cert_hash = Blockchain.hash_payload(payload)
    
    bc.issue_certificate(cert_hash, "STU-2", "0xIssuer")
    
    success, msg = bc.revoke_certificate(cert_hash, "Fraud detected", "0xIssuer")
    assert success
    
    verify = bc.verify_certificate(cert_hash)
    assert verify['isFound'] is True
    assert verify['isValid'] is False
    assert verify['isRevoked'] is True
    assert verify['revokeReason'] == "Fraud detected"
