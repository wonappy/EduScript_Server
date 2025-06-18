from fastapi import APIRouter
from src.app.routes.speech_route import router as speeh_router
from src.app.routes.language_route import router as language_router

router = APIRouter(prefix= "api/routes")
router.include_router(speeh_router)
router.include_router(language_router)
