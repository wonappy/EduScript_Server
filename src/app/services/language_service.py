# [serivces/language_service.py]
# LLM 작업 로직 처리
import asyncio 
from typing import Dict
from src.app.modules.llm.openai_llm import OpenAILLM
from src.app.modules.file.file_data import FileData
from src.app.dto.refinement_dto import SpeechRefineRequest, SpeechRefineResponse
from src.app.prompts.refining_prompt import refine_lecture_prompt, refine_meeting_prompt
from src.app.prompts.summarizing_prompt import summarize_lecture_prompt, summarize_meeting_prompt
from src.app.prompts.keypoints_prompt import extract_keypoints_prompt
from src.app.utils.file_generator_factory import create_file_by_format
from src.app.interfaces.single_speech_translation_interface import SingleSpeechTranslationInterface
from src.app.interfaces.multiple_speech_translation_interface import MultipleSpeechTranslationInterface

api_call_count = 0  # API 호출 횟수 카운트

# LLM 모듈 
llm_module = OpenAILLM() 

# =============================================================================
# 메인 서비스 함수
# =============================================================================

async def build_text_service(request: SpeechRefineRequest) -> SpeechRefineResponse:
    """발화 정제 통합 서비스 - 모드별/파일형식별 처리"""
    try:
        print("=== [SERVICE] 발화 정제 시작 ===")
        print(f"모드: {request.processing_mode}")
        print(f"파일형식: {request.fileFormat}")
        print(f"파일명: {request.fileName}")
        print(f"정제: {request.enable_refine}, 요약: {request.enable_summarize}, 핵심: {request.enable_keypoints}")

        def normalize_language_code(code: str) -> str:
            return code.lower().split('-')[0].split('_')[0]
        
        request.language_list = list(set(normalize_language_code(lang) for lang in request.language_list))
        print(f"정규화된 언어 리스트: {request.language_list}")

        # 1단계: 모드별 기본 정제
        refined_text = await _refine_by_mode(request.full_text, request.processing_mode, request.language_list)
        print(f"기본 정제 완료")

        # 2단계: 파일 생성
        if request.processing_mode == "lecture":
            return await _process_lecture_mode(request, refined_text)
        elif request.processing_mode == "conference":
            return await _process_conference_mode(request, refined_text)
        else:
            raise Exception(f"지원하지 않는 모드: {request.processing_mode}")
    
    except Exception as e:
        print(f"서비스 오류: {str(e)}")
        raise Exception(f"[SERVICE ERROR] 발화 정제 실패 - {str(e)}")

# =============================================================================
# 모드별 처리 함수
# =============================================================================

async def _process_lecture_mode(request: SpeechRefineRequest, refined_texts: dict[str, str]) -> SpeechRefineResponse:
    print("강의 모드 처리 시작")
    
    refined_results = []
    summarized_results = []
    keypoints_results = []

    for lang, text in refined_texts.items():
        if request.enable_refine:
            refined_results.append(create_file_by_format(
                content=text,
                filename=f"{request.fileName}_{lang}_정제된내용",
                file_format=request.fileFormat,
            ))

        if request.enable_summarize:
            summarized = await _summarize_lecture_text(text, lang)
            summarized_results.append(create_file_by_format(
                content=summarized,
                filename=f"{request.fileName}_{lang}_요약",
                file_format=request.fileFormat,
            ))

        if request.enable_keypoints:
            keypoints = await _extract_lecture_keypoints(text, lang)
            keypoints_results.append(create_file_by_format(
                content=keypoints,
                filename=f"{request.fileName}_{lang}_핵심포인트",
                file_format=request.fileFormat,
            ))

    return _create_response_multi(refined_results, summarized_results, keypoints_results)


async def _process_conference_mode(request: SpeechRefineRequest, refined_texts: dict[str, str]) -> SpeechRefineResponse:
    print("회의 모드 처리 시작")
    
    refined_results = []
    summarized_results = []

    for lang, text in refined_texts.items():
        if request.enable_refine:
            refined_results.append(create_file_by_format(
                content=text,
                filename=f"{request.fileName}_{lang}_정제된내용",
                file_format=request.fileFormat,
            ))

        if request.enable_summarize:
            summarized = await _summarize_meeting_text(text,lang)
            summarized_results.append(create_file_by_format(
                content=summarized,
                filename=f"{request.fileName}_{lang}_요약",
                file_format=request.fileFormat,
            ))

    return _create_response_multi(refined_results, summarized_results)


# =============================================================================
# LLM 처리 함수들
# =============================================================================

#강의/회의별 정제 프롬프트 구분 -> llm 정제 처리
async def _refine_by_mode(text: str, mode: str, target_languages: list[str]) -> dict[str, str]:
    results = {}

    for lang in target_languages:
        if mode == "conference":
            prompt = refine_meeting_prompt(lang)
            print(f"회의용 정제 프롬프트 사용 - {lang}")
        else:
            prompt = refine_lecture_prompt(lang)
            print(f"강의용 정제 프롬프트 사용 - {lang}")

        messages = [
            {"role": "system", "content": prompt},
            {"role": "user", "content": text}
        ]
        
        try:
            refined_text = await llm_module.select_gpt_model(messages=messages)
            results[lang] = refined_text
        except Exception as e:
            results[lang] = f"[ERROR] {e}"

    return results


async def _summarize_lecture_text(text: str, language: str) -> str:
    """텍스트 요약"""
    print("텍스트 요약 중...")
    
    messages = [
        {"role": "system", "content": summarize_lecture_prompt(language)},
        {"role": "user", "content": text}
    ]
    
    return await llm_module.select_gpt_model(messages=messages)

async def _summarize_meeting_text(text: str, language: str) -> str:
    """텍스트 요약"""
    print("텍스트 요약 중...")
    
    messages = [
        {"role": "system", "content": summarize_meeting_prompt(language)},
        {"role": "user", "content": text}
    ]
    
    return await llm_module.select_gpt_model(messages=messages)

async def _extract_lecture_keypoints(text: str, language: str) -> str:
    """핵심 포인트 추출"""
    print("핵심 포인트 추출 중...")
    
    messages = [
        {"role": "system", "content": extract_keypoints_prompt(language)},
        {"role": "user", "content": text}
    ]
    
    return await llm_module.select_gpt_model(messages=messages)

def _create_response_multi(refined: list[FileData], summarized: list[FileData], keypoints: list[FileData] = None) -> SpeechRefineResponse:
    all_files = (refined or []) + (summarized or []) + (keypoints or [])
    total_files = len(all_files)

    return SpeechRefineResponse(
        refined_result=refined[0] if refined else None,
        summarized_result=summarized[0] if summarized else None,
        keypoints_result=keypoints[0] if keypoints else None,
        refined_results=refined,
        summarized_results=summarized,
        keypoints_results=keypoints or [],
        total_files=total_files,
        message=f"총 {total_files}개 파일이 생성되었습니다." if total_files > 0 else "파일 생성에 실패했습니다."
    )
