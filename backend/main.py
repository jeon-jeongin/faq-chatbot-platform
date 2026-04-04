from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from config import settings
from features.housing import router as housing_chat_router


def create_app() -> FastAPI:
    app = FastAPI(
        title="FAQ Chatbot Platform",
        debug=settings.debug,
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.get("/")
    async def root():
        return {"message": "FAQ Chatbot Platform API"}

    @app.get("/health")
    async def health():
        return {"status": "ok", "service": "api"}

    app.include_router(housing_chat_router, prefix="/api")
    return app


app = create_app()