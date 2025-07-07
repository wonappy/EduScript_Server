# [routes/speech_route.py]
# speech 작업 엔드포인트
from fastapi import APIRouter, WebSocket
from src.app.services.speech_service import websocket_speech_service

router = APIRouter(prefix="/speech-translation")

# [1] Single WebSocket 연결
@router.websocket("/connect/single-mode")
async def websocket_endpoint(websocket: WebSocket):
    """
        강의 모드 :
        입력 언어가 1개인 경우에 활용할 수 있는 기능입니다.
    """
    await websocket_speech_service(websocket, "single")

# [2] Multiple WebSocket 연결
@router.websocket("/connect/multiple-mode")
async def websocket_endpoint(websocket: WebSocket):
    """
        회의 모드 :
        입력 언어가 1~10개인 경우에 활용할 수 있는 기능입니다.
    """
    await websocket_speech_service(websocket, "multiple")