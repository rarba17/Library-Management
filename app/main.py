from fastapi import FastAPI
from fastapi.concurrency import asynccontextmanager
from app.database import engine, Base
from app.routers import books,users
from app import models


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    Base.metadata.create_all(bind=engine)
    yield

app = FastAPI(
    title="Library Management System",
    description="A simple library management system API",
)

#app.include_router(books.routers )
#app.include_router(users.routers)


@app.get("/")
def check():
    return {"message": "Library Management System API is running."}

@app.get("/health")
def health_check():
    return {"status":"healthy"}


