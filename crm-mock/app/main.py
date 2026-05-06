from fastapi import FastAPI

from app.routes import router


app = FastAPI(title="Whagent CRM Mock")
app.include_router(router)
