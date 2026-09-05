from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends
from app.database import ensure_schema
from app.routers import books,users, auth
from fastapi.middleware.cors import CORSMiddleware
from app import models


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    ensure_schema()
    yield

app = FastAPI(
    title="Library Management System",
    description="A simple library management system API",
    lifespan=lifespan,
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173", "http://localhost:8000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router)
app.include_router(users.router)
app.include_router(books.router)


@app.get("/")
def check():
    return {"message": "Library Management System API is running."}

@app.get("/health")
def health_check():
    return {"status":"healthy"}
