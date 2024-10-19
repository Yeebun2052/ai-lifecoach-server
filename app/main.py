from fastapi import FastAPI
from dotenv import load_dotenv
import os

load_dotenv()  # 加载 .env 文件中的环境变量

app = FastAPI(title="AI Life Coach API")

@app.get("/")
async def root():
    return {"message": "Welcome to AI Life Coach API"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, debug=os.getenv("DEBUG", "False").lower() == "true")