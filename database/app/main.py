import uvicorn
from fastapi import FastAPI
from app.routes.user_routes import router as user_router
from app.routes.conv_routes import router as conv_router
from app.routes.log_routes import router as log_router

app = FastAPI()
app.include_router(user_router)
app.include_router(log_router)
app.include_router(conv_router)


@app.get("/")
async def root():
    return {"message": "API is running"}


if __name__ == "__main__":
    uvicorn.run("main:app", reload=True)