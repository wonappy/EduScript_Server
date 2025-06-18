# [routes/speech_route.py]
# speech 작업 엔드포인트
from fastapi import APIRouter, status, HTTPException
from src.app.services.speech_service import websocket_translation_service
from fastapi import WebSocket

router = APIRouter(prefix="/speech-translation")

# [1] WebSocket 연결
@router.websocket(
    "/connect",
    tags=["speech-translation"],
    summary="실시간 음성 번역",
    description="음성을 실시간으로 인식하고 설정된 언어로 번역한다.",
)
async def websocket_endpoint(websocket: WebSocket):
    await websocket_translation_service(websocket)