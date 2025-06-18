from fastapi import APIRouter
from src.app.routes.speech_route import router as speech_router
from src.app.routes.language_route import router as language_router

api_router = APIRouter(prefix= "/api/routes")
api_router.include_router(speech_router)
api_router.include_router(language_router)
