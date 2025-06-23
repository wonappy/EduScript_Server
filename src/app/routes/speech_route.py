# [routes/speech_route.py]
# speech 작업 엔드포인트
from fastapi import APIRouter, WebSocket
from src.app.services.speech_service import websocket_translation_service

router = APIRouter(prefix="/speech-translation")

# [1] WebSocket 연결
@router.websocket("/connect")
async def websocket_endpoint(websocket: WebSocket):
    await websocket_translation_service(websocket)