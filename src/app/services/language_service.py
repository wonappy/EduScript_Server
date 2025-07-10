# [serivces/language_service.py]
# LLM 작업 로직 처리
import asyncio 
from src.app.modules.llm.openai_llm import OpenAILLM
from src.app.modules.file.file_data import FileData
from src.app.dto.refinement_dto import SpeechRefineRequest, SpeechRefineResponse
from src.app.prompts.refining_prompt import refine_lecture_prompt, refine_meeting_prompt
from src.app.prompts.summarizing_prompt import summarize_lecture_prompt, summarize_meeting_prompt
from src.app.prompts.keypoints_prompt import extract_keypoints_prompt
from src.app.utils.file_generator_factory import create_file_by_format

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

        # 1단계: 모드별 기본 정제
        refined_text = await _refine_by_mode(request.full_text, request.processing_mode)
        print(f"✅ 기본 정제 완료")

        # 2단계: 파일 생성
        if request.processing_mode == "lecture":
            return await _process_lecture_mode(request, refined_text)
        elif request.processing_mode == "conference":
            return await _process_conference_mode(request, refined_text)
        else:
            raise Exception(f"지원하지 않는 모드: {request.processing_mode}")
    
    except Exception as e:
        print(f"❌ 서비스 오류: {str(e)}")
        raise Exception(f"[SERVICE ERROR] 발화 정제 실패 - {str(e)}")

# =============================================================================
# 모드별 처리 함수
# =============================================================================

async def _process_lecture_mode(request: SpeechRefineRequest, refined_text: str) -> SpeechRefineResponse:
    """강의 모드 처리: 정제 + 요약 + 핵심포인트"""
    print("📚 강의 모드 처리 시작")
    
    refined_result = None
    summarized_result = None
    keypoints_result = None

    # 정제된 파일
    if request.enable_refine:
        refined_result = create_file_by_format(
            content=refined_text,
            filename=f"{request.fileName}_정제된내용",
            file_format=request.fileFormat,
        )
        print("✅ 정제 파일 생성 완료")

    # 요약 파일
    if request.enable_summarize:
        summarized_text = await _summarize_lecture_text(refined_text)
        summarized_result = create_file_by_format(
            content=summarized_text,
            filename=f"{request.fileName}_요약",
            file_format=request.fileFormat,
        )
        print("✅ 요약 파일 생성 완료")

    # 핵심포인트 파일
    if request.enable_keypoints:
        keypoints_text = await _extract_lecture_keypoints(refined_text)
        keypoints_result = create_file_by_format(
            content=keypoints_text,
            filename=f"{request.fileName}_핵심포인트",
            file_format=request.fileFormat,
        )
        print("✅ 핵심포인트 파일 생성 완료")

    return _create_response(refined_result, summarized_result, keypoints_result)

async def _process_conference_mode(request: SpeechRefineRequest, refined_text: str) -> SpeechRefineResponse:
    """회의 모드 처리: 회의록 구조화"""
    print("🤝 회의 모드 처리 시작")
    print(f"파일 형식 : {request.fileFormat}")
    
    refined_result = None
    summarized_result = None

    # 정제된 파일
    if request.enable_refine:
        refined_result = create_file_by_format(
            content=refined_text,
            filename=f"{request.fileName}_정제된내용",
            file_format=request.fileFormat,
        )
        print("✅ 정제 파일 생성 완료")

        # 요약 파일
    if request.enable_summarize:
        summarized_text = await _summarize_meeting_text(refined_text)
        summarized_result = create_file_by_format(
            content=summarized_text,
            filename=f"{request.fileName}_요약",
            file_format=request.fileFormat,
        )
        print("✅ 요약 파일 생성 완료")

    return _create_response(refined_result, summarized_result, None)

# =============================================================================
# LLM 처리 함수들
# =============================================================================

#강의/회의별 정제 프롬프트 구분 -> llm 정제 처리
async def _refine_by_mode(text: str, mode: str) -> str:
    """모드별 기본 정제"""
    if mode == "conference":
        prompt = refine_meeting_prompt()
        print("🤝 회의용 정제 프롬프트 사용")
    else:  # lecture
        prompt = refine_lecture_prompt()
        print("📚 강의용 정제 프롬프트 사용")
    
    messages = [
        {"role": "system", "content": prompt},
        {"role": "user", "content": text}
    ]
    
    return await llm_module.select_gpt_model(messages=messages)

async def _summarize_lecture_text(text: str) -> str:
    """텍스트 요약"""
    print("📝 텍스트 요약 중...")
    
    messages = [
        {"role": "system", "content": summarize_lecture_prompt()},
        {"role": "user", "content": text}
    ]
    
    return await llm_module.select_gpt_model(messages=messages)

async def _summarize_meeting_text(text: str) -> str:
    """텍스트 요약"""
    print("📝 텍스트 요약 중...")
    
    messages = [
        {"role": "system", "content": summarize_meeting_prompt()},
        {"role": "user", "content": text}
    ]
    
    return await llm_module.select_gpt_model(messages=messages)

async def _extract_lecture_keypoints(text: str) -> str:
    """핵심 포인트 추출"""
    print("🎯 핵심 포인트 추출 중...")
    
    messages = [
        {"role": "system", "content": extract_keypoints_prompt()},
        {"role": "user", "content": text}
    ]
    
    return await llm_module.select_gpt_model(messages=messages)

def _create_response(refined_result: FileData = None, 
                    summarized_result: FileData = None, 
                    keypoints_result: FileData = None) -> SpeechRefineResponse:
    """응답 객체 생성"""
    total_files = sum(1 for result in [refined_result, summarized_result, keypoints_result] if result is not None)
    
    response = SpeechRefineResponse(
        refined_result=refined_result,
        summarized_result=summarized_result,
        keypoints_result=keypoints_result,
        total_files=total_files,
        message=f"✅ 총 {total_files}개 파일이 생성되었습니다." if total_files > 0 else "❌ 파일 생성에 실패했습니다."
    )
    print(f"처리 완료 - 생성된 파일: {total_files}개")
    return response