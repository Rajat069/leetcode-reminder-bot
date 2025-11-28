from fastapi import FastAPI, HTTPException, Header, BackgroundTasks
from pydantic import BaseModel
from typing import Optional
import os
from . import core_logic, config

app = FastAPI()

class ReminderRequest(BaseModel):
    username: str
    email: str

@app.post("/trigger-check")
async def trigger_check(request: ReminderRequest, x_api_key: Optional[str] = Header(None)):
    if x_api_key != os.getenv("USER_SERVICE_API_KEY"): 
        raise HTTPException(status_code=403, detail="Invalid API Key")

    print(f"⚡ Manual trigger received for {request.username}")

    try:
        result = core_logic.check_single_user_on_demand(request.username, request.email)
        
        return {
            "status": "success", 
            "message": result.get("message", "Check complete"),
            "data": result
        }
    except Exception as e:
        print(f"EROOR in manual check: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
def health_check():
    return {"status": "running"}