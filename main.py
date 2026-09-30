from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from schemas import CertificatePayload, RevokePayload
import qrcode
import base64
import io
import os

from blockchain import Blockchain

app = FastAPI(title="EduChain Authenticator API")
blockchain = Blockchain()

# Mount static files and templates
os.makedirs("static", exist_ok=True)
os.makedirs("templates", exist_ok=True)

try:
    app.mount("/static", StaticFiles(directory="static"), name="static")
except RuntimeError:
    pass

templates = Jinja2Templates(directory="templates")



@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/api/issue")
async def issue_certificate(payload: CertificatePayload):
    payload_dict = payload.model_dump() if hasattr(payload, 'model_dump') else payload.dict()
    cert_hash = Blockchain.hash_payload(payload_dict)
    
    issuer = "0xGlobalTechUniv1234567890abcdef"
    success, msg = blockchain.issue_certificate(
        cert_hash=cert_hash,
        student_id=payload.student_id,
        issuer=issuer
    )
    if not success:
        raise HTTPException(status_code=400, detail=msg)
        
    # Generate QR Code
    verification_url = f"http://localhost:8000/?hash={cert_hash}"
    qr = qrcode.QRCode(version=1, box_size=10, border=4)
    qr.add_data(verification_url)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    
    buffered = io.BytesIO()
    img.save(buffered, format="PNG")
    qr_base64 = base64.b64encode(buffered.getvalue()).decode("utf-8")
        
    last_block = blockchain.get_last_block()
    return {
        "status": "success",
        "message": msg,
        "cert_hash": cert_hash,
        "qr_code_base64": qr_base64,
        "transaction": last_block['transactions'][-1] if last_block['transactions'] else None
    }

@app.get("/api/verify/{cert_hash}")
async def verify_certificate(cert_hash: str):
    return blockchain.verify_certificate(cert_hash)

@app.post("/api/revoke")
async def revoke_certificate(payload: RevokePayload):
    success, msg = blockchain.revoke_certificate(payload.cert_hash, payload.reason, payload.issuer)
    if not success:
        raise HTTPException(status_code=400, detail=msg)
    return {"status": "success", "message": msg}

@app.get("/api/ledger")
async def get_ledger():
    return {"chain": blockchain.chain, "length": len(blockchain.chain)}

@app.post("/api/tamper")
async def tamper_certificate(payload: CertificatePayload):
    payload_dict = payload.model_dump() if hasattr(payload, 'model_dump') else payload.dict()
    tampered_hash = Blockchain.hash_payload(payload_dict)
    result = blockchain.verify_certificate(tampered_hash)
    
    return {
        "tampered_hash": tampered_hash,
        "verification_result": result,
        "tampered": not result["isFound"]
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
