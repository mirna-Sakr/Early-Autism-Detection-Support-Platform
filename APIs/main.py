from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from core import auth
from routers import children, sessions, notifications

app = FastAPI(
    title="Autism Screening API",
    description="Backend API for Early Autism Detection System",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router,          prefix="/auth",    tags=["Auth"])
app.include_router(children.router,      prefix="",         tags=["Children"])
app.include_router(sessions.router,      prefix="",         tags=["Sessions"])
app.include_router(notifications.router, prefix="",         tags=["Notifications"])


@app.get("/", tags=["Health"])
def health_check():
    return {"status": "ok", "message": "Autism Screening API is running"}
