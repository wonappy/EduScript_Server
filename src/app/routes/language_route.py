# [routes/language_route.py]
# LLM 작업 엔드포인트
from fastapi import APIRouter, status, HTTPException
import logging
from src.app.dto.refinement_dto import SpeechRefineRequest, SpeechRefineResponse
from src.app.services.language_service import build_text_service

router = APIRouter(prefix="/language")

# [1] 발화 정제
@router.post(
    "/refinement",
    tags=["LLM"],
    status_code=status.HTTP_200_OK,
    response_model = SpeechRefineResponse,
    summary="발화 정제",
    description="정제되지 않은 강연자의 발화 내용을 입력 받아 발화를 정제한다.",
)
async def refine_text_route(request: SpeechRefineRequest) -> SpeechRefineResponse:
    try:
        # [0] 디버깅 코드
        print(f"=== [ROUTER DEBUG] ===") 
        if not request.full_text or not request.full_text.strip():
            raise HTTPException(status_code=400, detail="[ROUTER ERROR] 발화 내용이 비어있습니다.")
        
        # [1] 서비스 호출

        # if request.fileFormat.lower() == "pdf":
        #     return await refine_text_to_pdf_service(request)
        # elif request.fileFormat.lower() == "docx":
        #     return await refine_text_to_docx_service(request, mode = request.processing_mode)
        # else:
        response = await build_text_service(request)
        return response
    except HTTPException as httpE:
        logging.error(f"[ROUTER ERROR] 발화 정제 HTTP 에러 발생 - [{httpE.status_code}: {httpE.detail}]")
        raise
    except Exception as e:
        logging.error(f"[ROUTER ERROR] 발화 정제 실패 - {str(e)}")
        raise HTTPException(status_code=500, detail="발화 정제 처리 중 오류 발생")