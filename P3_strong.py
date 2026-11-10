import os
import re
import subprocess
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import APIKeyHeader
from pydantic import BaseModel, Field

app = FastAPI(title="Admin Host Status Service", version="1.0.0")

# Authentication: Load admin key from environment variable (never hardcoded)
ADMIN_KEY_NAME = "X-Admin-Key"
api_key_header = APIKeyHeader(name=ADMIN_KEY_NAME, auto_error=True)

def verify_admin_key(api_key: str = Depends(api_key_header)) -> str:
    expected_key = os.environ.get("ADMIN_API_KEY")
    if not expected_key or api_key != expected_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing admin API key",
        )
    return api_key

# Request and Response Schemas
class PingRequest(BaseModel):
    host: str = Field(..., description="Target hostname or IP address to check", examples=["8.8.8.8"])

class PingResponse(BaseModel):
    host: str
    reachable: bool

# Strict regex matching valid domain names, IPv4, and IPv6 addresses
# Prevents shell injection characters, spaces, and command flags (e.g., starting with '-')
HOST_REGEX = re.compile(
    r"^(?:[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?\.)+[a-zA-Z]{2,}$|"
    r"^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$|"
    r"^(([0-9a-fA-F]{1,4}:){7,7}[0-9a-fA-F]{1,4}|([0-9a-fA-F]{1,4}:){1,7}:|([0-9a-fA-F]{1,4}:){1,6}:[0-9a-fA-F]{1,4}|([0-9a-fA-F]{1,4}:){1,5}(:[0-9a-fA-F]{1,4}){1,2}|([0-9a-fA-F]{1,4}:){1,4}(:[0-9a-fA-F]{1,4}){1,3}|([0-9a-fA-F]{1,4}:){1,3}(:[0-9a-fA-F]{1,4}){1,4}|([0-9a-fA-F]{1,4}:){1,2}(:[0-9a-fA-F]{1,4}){1,5}|[0-9a-fA-F]{1,4}:((:[0-9a-fA-F]{1,4}){1,6})|:((:[0-9a-fA-F]{1,4}){1,7}|:))$"
)

@app.post("/admin/ping", response_model=PingResponse, status_code=status.HTTP_200_OK)
def admin_ping(payload: PingRequest, admin: str = Depends(verify_admin_key)):
    target = payload.host.strip()
    
    # Defense-in-depth: Validate input against safe host patterns
    if not HOST_REGEX.match(target):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid host format supplied."
        )
    
    # Construct command list safely (shell=False by default)
    # This prevents CWE-78 entirely because arguments are passed as a distinct vector list.
    ping_cmd = ["ping", "-c", "1", "-W", "2", target]
    
    try:
        # Execute subprocess without capturing or returning raw stdout/stderr
        result = subprocess.run(
            ping_cmd,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            text=True,
            timeout=5
        )
        reachable = (result.returncode == 0)
    except (subprocess.TimeoutExpired, Exception):
        reachable = False
        
    # Return structured status response only (no raw command output)
    return PingResponse(host=target, reachable=reachable)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)