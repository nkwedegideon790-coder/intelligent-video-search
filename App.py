import fastapi as FASTAPI
from Routers.upload import router as upload_router

app = FASTAPI()
app.include_router(upload_router)

@app.get("/")
async def root():
    return {"message": "Welcome to the FastAPI application!"}
