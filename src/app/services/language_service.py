# [serivces/language_service.py]
# LLM 작업 로직 처리 
from fastapi import HTTPException
import logging
from src.app.modules.llm.openai_llm import OpenAILLM
from src.app.dto.refinement_dto import SpeechRefineRequest, SpeechSummarizeRequest, KeyPointsExtractRequest, SpeechRefineResponse, SpeechSummarizeResponse, KeyPointsExtractResponse
from src.app.prompts.refining_prompt import refine_speech_prompt
from src.app.prompts.summarizing_prompt import summarize_speech_prompt
from src.app.prompts.keypoints_prompt import extract_keypoints_prompt

# [0] LLM 모듈 
llm_module = OpenAILLM() 

# [1] 발화 정제
async def refine_speech_service(request: SpeechRefineRequest) -> SpeechRefineResponse:
    try:
        # 🔴 디버깅
        print(f"=== [SERVICE DEBUG 1] refine_speech_service ===") 
        print(f"[SERVICE] full_speech: {request.full_speech if hasattr(request, 'full_speech') else 'None'}")
        
        # 1) 프롬프트 설계
        messages = [
            { "role": "system", "content": refine_speech_prompt() },
            { "role": "user", "content": f" 다음 발화를 정제해주세요 : {request.full_speech}" } 
         ]        
        # 2) LLM 모듈 호출 
        refined_text = await llm_module.select_gpt_model(messages=messages)        
        # 3) 응답 DTO 
        return SpeechRefineResponse(refined_speech=refined_text)
    except HTTPException as e:
        logging.error(f"[SERVICE ERROR] 발화 정제 HTTP 에러 발생 - [{e.status_code}: {e.detail}]")
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"[SERVICE ERROR] 발화 정제 실패 - {str(e)}")

# [2] 발화 요약
async def summarize_speech_service(request: SpeechSummarizeRequest) -> SpeechSummarizeResponse:
    try:
        # 🔴 디버깅
        print(f"=== [SERVICE DEBUG 2] summarize_speech_service ===") 
        print(f"[SERVICE] refined_speech: {request.refined_speech if hasattr(request, 'refined_speech') else 'None'}")
        
        # 1) 프롬프트 설계
        messages = [
            { "role": "system", "content": summarize_speech_prompt() },
            { "role": "user", "content": f"다음 발화를 요약해주세요 : {request.refined_speech}" }
        ]
        # 2) LLM 모듈 호출 
        summarized_text = await llm_module.select_gpt_model(messages=messages)
        # 3) 응답 DTO
        return SpeechSummarizeResponse(summarized_speech=summarized_text)
    except HTTPException as e:
        logging.error(f"[SERVICE ERROR] 발화 요약 HTTP 에러 발생 - [{e.status_code}: {e.detail}]")
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"[SERIVCE ERROR] 발화 요약 처리 실패 - {str(e)}")

# [3] 중요 내용 추출
async def extract_keypoints_service(request: KeyPointsExtractRequest) -> KeyPointsExtractResponse:
    try:
        # 🔴 디버깅
        print(f"=== [SERVICE DEBUG 3] extract_keypoints_service ===") 
        print(f"[SERVICE] refined_speech: {request.refined_speech if hasattr(request, 'refined_speech') else 'None'}")

        # 1) 프롬프트 설계
        messages = [
            { "role": "system", "content": extract_keypoints_prompt() },
            { "role": "user", "content": f"다음 발화를 요약해주세요 : {request.refined_speech}" }
        ]
        # 2) LLM 모듈 호출 
        extracted_text = await llm_module.select_gpt_model(messages=messages)
        # 3) 응답 DTO
        return KeyPointsExtractResponse(extracted_keypoints=extracted_text)
    except HTTPException as e:
        logging.error(f"[SERVICE ERROR] 발화 요약 HTTP 에러 발생 - [{e.status_code}: {e.detail}]")
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"[SERIVCE ERROR] 발화 요약 처리 실패 - {str(e)}")