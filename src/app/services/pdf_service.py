# services/pdf_service.py
from src.app.modules.llm.openai_llm import OpenAILLM
from src.app.modules.file.file_data import FileData
from src.app.dto.refinement_dto import SpeechRefineRequest, SpeechRefineResponse
from src.app.prompts.keypoints_prompt import extract_keypoints_prompt
from src.app.services.language_service import _process_lecture_mode

# LLM 모듈
llm_module = OpenAILLM()

# async def refine_text_to_pdf_service(request: SpeechRefineRequest) -> SpeechRefineResponse:
#     """발화 정제 후 PDF 파일로 생성하는 통합 서비스"""
#     try:
#         print("=== [PDF SERVICE DEBUG] ===")
#         print(">> PDF 생성 서비스 시작")
#         print(f"[PDF SERVICE] full_text: {request.full_text}")
#         print(f"[PDF SERVICE] enable_refine: {request.enable_refine}")
#         print(f"[PDF SERVICE] enable_summarize: {request.enable_summarize}")
#         print(f"[PDF SERVICE] enable_keypoints: {request.enable_keypoints}")
        
#         # 1) 정제 프롬프트 설계 및 LLM 호출
#         messages = [
#             {"role": "system", "content": refine_speech_prompt()},
#             {"role": "user", "content": f"{request.full_text}"}
#         ]
        
#         print(f"[PDF DEBUG] API 호출 1 - 정제 시작")
#         temp_refined_text = await llm_module.select_gpt_model(messages=messages)
#         print(f"[PDF DEBUG] API 호출 1 완료")
        
#         # 2) 강의 모드 처리 함수 호출
#         return await _process_lecture_mode(request, temp_refined_text)
        
#     except Exception as e:
#         raise Exception(f"[PDF SERVICE ERROR] PDF 생성 실패 - {str(e)}")

async def summarize_text_pdf(temp_refined_text: str) -> str:
    """요약 텍스트 생성 (PDF용)"""
    try:
        messages = [
            {"role": "system", "content": summarize_speech_prompt()},
            {"role": "user", "content": f"{temp_refined_text}"}
        ]
        return await llm_module.select_gpt_model(messages=messages)
    except Exception as e:
        raise Exception(f"[PDF SERVICE ERROR] 요약 처리 실패 - {str(e)}")

async def extract_keypoints_pdf(temp_refined_text: str) -> str:
    """중요 내용 추출 (PDF용)"""
    try:
        messages = [
            {"role": "system", "content": extract_keypoints_prompt()},
            {"role": "user", "content": f"{temp_refined_text}"}
        ]
        return await llm_module.select_gpt_model(messages=messages)
    except Exception as e:
        raise Exception(f"[PDF SERVICE ERROR] 중요 내용 추출 실패 - {str(e)}")