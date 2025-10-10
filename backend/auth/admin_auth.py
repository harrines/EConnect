from fastapi import FastAPI, Depends
from .auth_bearer import JWTBearer
from .auth_handler import signJWT

app = FastAPI()
admin_jwt_bearer = JWTBearer(role="admin")

@app.get("/attendance")
async def admin_only_route(token: str = Depends(admin_jwt_bearer)):
    return {"message": "This is an admin-only route"}

@app.get("/user_leave_requests")
async def admin_only_route(token: str = Depends(admin_jwt_bearer)):
    return {"message": "This is an admin-only route"}

@app.get("/remote_work_requests")
async def admin_only_route(token: str = Depends(admin_jwt_bearer)):
    return {"message": "This is an admin-only route"}

@app.get("/updated_user_leave_requests")
async def admin_only_route(token: str = Depends(admin_jwt_bearer)):
    return {"message": "This is an admin-only route"}

@app.get("updated_remote_work_requests")
async def admin_only_route(token: str = Depends(admin_jwt_bearer)):
    return {"message": "This is an admin-only route"}