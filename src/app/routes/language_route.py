# [routes/language_route.py]
# LLM 작업 엔드포인트
from fastapi import APIRouter, status, HTTPException
import logging
from src.app.dto.refinement_dto import SpeechRefineRequest, SpeechRefineResponse
from src.app.services.language_service import refine_text_service

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
        response = await refine_text_service(request)
    
        return response
    except HTTPException as httpE:
        logging.error(f"[ROUTER ERROR] 발화 정제 HTTP 에러 발생 - [{httpE.status_code}: {httpE.detail}]")
        raise
    except Exception as e:
        logging.error(f"[ROUTER ERROR] 발화 정제 실패 - {str(e)}")
        raise HTTPException(status_code=500, detail="발화 정제 처리 중 오류 발생")
    
# # [2] 발화 요약
# @router.post(
#     "/summarize",
#     tags=["LLM"],
#     status_code=status.HTTP_200_OK,
#     summary="발화 요약",
#     description="정제된 발화를 입력 받아 내용을 요약한다.",
# )
# async def summarize_speech(request: SpeechSummarizeRequest) -> SpeechSummarizeResponse:
#     try:
#         # 🔴 디버깅
#         print(f"=== [ROUTER DEBUG 2] summarize_speech ===") 
#         if not request.refined_speech or not request.refined_speech.strip():
#             raise HTTPException(status_code=400, detail="[ROUTER ERROR] 정제된 발화가 비어있습니다.")
#         # 서비스 호출
#         return await summarize_speech_service(request)
#     except HTTPException as httpE:
#         logging.error(f"[ROUTER ERROR] 발화 요약 HTTP 에러 발생 - [{httpE.status_code}: {httpE.detail}]")
#         raise
#     except Exception as e:
#         logging.error(f"[ROUTER ERROR] 발화 요약 실패 - {str(e)}")
#         raise HTTPException(status_code=500, detail="발화 요약 처리 중 오류 발생")
    
# # [3] 중요 내용 추출
# @router.post(
#     "/keypoints",
#     tags=["LLM"],
#     status_code=status.HTTP_200_OK,
#     summary="중요 내용 추출",
#     description="정제된 발화를 입력 받아 중요한 내용을 추출한다.",
# )
# async def extract_keypoints(request: KeyPointsExtractRequest) -> KeyPointsExtractResponse:
#     try:
#         # 🔴 디버깅
#         print(f"=== [ROUTER DEBUG 3] extract_keypoints ===") 
#         if not request.refined_speech or not request.refined_speech.strip():
#             raise HTTPException(status_code=400, detail="[ROUTER ERROR] 정제된 발화가 비어있습니다.")
#         # 서비스 호출
#         return await extract_keypoints_service(request)
#     except HTTPException as httpE:
#         logging.error(f"[ROUTER ERROR] 중요 내용 추출 HTTP 에러 발생 - [{httpE.status_code}: {httpE.detail}]")
#         raise
#     except Exception as e:
#         logging.error(f"[ROUTER ERROR] 중요 내용 추출 실패 - {str(e)}")
#         raise HTTPException(status_code=500, detail="중요 내용 추출 중 오류 발생")