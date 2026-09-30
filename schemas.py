from pydantic import BaseModel

class CertificatePayload(BaseModel):
    certificate_id: str
    student_id: str
    student_name: str
    degree: str
    major: str
    institution: str
    graduation_date: str
    grade: str
    issue_date: str

class RevokePayload(BaseModel):
    cert_hash: str
    reason: str
    issuer: str
