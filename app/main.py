from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import os
from app.api.v1.endpoints import auth, users
from app.core.config import Settings

load_dotenv()  # 加载 .env 文件中的环境变量

app = FastAPI(title="AI Life Coach API")

# CORS middleware configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# Include routers
app.include_router(auth.router, prefix=f"{Settings.API_V1_STR}/auth", tags=["auth"])

app.include_router(users.router, prefix="/api/v1/users", tags=["users"])

@app.get("/")
async def root():
    return {"message": "Welcome to AI Life Coach API 2024"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, debug=os.getenv("DEBUG", "False").lower() == "true")