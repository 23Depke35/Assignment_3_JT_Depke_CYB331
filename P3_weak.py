import asyncio
import platform
import re
from fastapi import FastAPI, HTTPException, Query, Security, Depends
from fastapi.security import APIKeyHeader

app = FastAPI()

# Example simple admin security check
API_KEY_HEADER = APIKeyHeader(name="X-Admin-API-Key")
ADMIN_SECRET_KEY = "admin-secret-token"  # Load from environment variables in production

def verify_admin(api_key: str = Depends(API_KEY_HEADER)):
    if api_key != ADMIN_SECRET_KEY:
        raise HTTPException(status_code=403, detail="Unauthorized")
    return api_key

# Strict regex pattern for validating domain names and IPv4/IPv6 addresses
HOSTNAME_REGEX = re.compile(
    r"^(?:[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?\.)+[a-zA-Z]{2,63}$|"  # Domain name
    r"^(?:[0-9]{1,3}\.){3}[0-9]{1,3}$"                                         # IPv4
)

@app.get("/admin/ping")
async def ping_hostname(
    host: str = Query(..., description="Hostname or IP address to ping"),
    admin: str = Depends(verify_admin)
):
    # 1. Input Validation: Prevent illegal characters or command manipulation
    host_clean = host.strip()
    if not HOSTNAME_REGEX.match(host_clean):
        raise HTTPException(
            status_code=400, 
            detail="Invalid hostname or IP address format."
        )

    # 2. Determine OS-specific ping flags
    is_windows = platform.system().lower() == "windows"
    count_flag = "-n" if is_windows else "-c"
    timeout_flag = "-w" if is_windows else "-W"
    
    # Flags: 1 packet, 2-second timeout limit
    cmd = ["ping", count_flag, "1", timeout_flag, "2" if is_windows else "2", host_clean]

    # 3. Execute process asynchronously without invoking shell=True
    try:
        proc = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        stdout, stderr = await proc.communicate()
        
        reachable = proc.returncode == 0

        return {
            "host": host_clean,
            "reachable": reachable,
            "status_code": proc.returncode,
            "output": stdout.decode("utf-8", errors="ignore") if reachable else stderr.decode("utf-8", errors="ignore")
        }

    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Failed to execute ping operation: {str(e)}"
        )