# services/pdf_service.py
from src.app.modules.llm.openai_llm import OpenAILLM
from src.app.modules.file.file_data import FileData
from src.app.dto.refinement_dto import SpeechRefineRequest, SpeechRefineResponse
from src.app.prompts.refining_prompt import refine_speech_prompt
from src.app.prompts.summarizing_prompt import summarize_speech_prompt
from src.app.prompts.keypoints_prompt import extract_keypoints_prompt
from src.app.utils.pdf_generator import create_pdf_from_text

# LLM 모듈
llm_module = OpenAILLM()

async def refine_text_to_pdf_service(request: SpeechRefineRequest) -> SpeechRefineResponse:
    """발화 정제 후 PDF 파일로 생성하는 서비스"""
    try:
        print("=== [PDF SERVICE DEBUG] ===")
        print(">> PDF 생성 서비스 시작")
        print(f"[PDF SERVICE] full_text: {request.full_text}")
        print(f"[PDF SERVICE] enable_refine: {request.enable_refine}")
        print(f"[PDF SERVICE] enable_summarize: {request.enable_summarize}")
        print(f"[PDF SERVICE] enable_keypoints: {request.enable_keypoints}")
        
        # 1) 정제 프롬프트 설계
        messages = [
            {"role": "system", "content": refine_speech_prompt()},
            {"role": "user", "content": f"{request.full_text}"}
        ]
        
        # 저장 변수 선언
        refined_result = None
        summarized_result = None
        keypoints_result = None
        
        # 2) LLM 모듈 호출 - 정제 처리
        print(f"[PDF DEBUG] API 호출 1 - 정제 시작")
        temp_refined_text = await llm_module.select_gpt_model(messages=messages)
        print(f"[PDF DEBUG] API 호출 1 완료")
        
        # 3) 정제 PDF 파일 생성
        if request.enable_refine:
            refined_result = create_pdf_from_text(
                text=temp_refined_text,
                filename="refined_speech.pdf"
            )
            print(f"[PDF SERVICE] 정제 PDF 파일 생성 완료 - 크기: {refined_result.file_size} bytes")
        
        # 4) 요약 처리
        if request.enable_summarize:
            print(f"[PDF DEBUG] API 호출 2 - 요약 시작")
            summarized_text = await summarize_text_pdf(temp_refined_text)
            print(f"[PDF SERVICE] 요약 완료")
            summarized_result = create_pdf_from_text(
                text=summarized_text,
                filename="speech_summary.pdf"
            )
            print(f"[PDF SERVICE] 요약 PDF 파일 생성 완료 - 크기: {summarized_result.file_size} bytes")
        
        # 5) 중요 내용 추출 처리
        if request.enable_keypoints:
            keypoints_text = await extract_keypoints_pdf(temp_refined_text)
            print(f"[PDF SERVICE] 중요 내용 추출 완료")
            keypoints_result = create_pdf_from_text(
                text=keypoints_text,
                filename="key_points.pdf"
            )
            print(f"[PDF SERVICE] 핵심포인트 PDF 파일 생성 완료 - 크기: {keypoints_result.file_size} bytes")
        
        # 6) 응답 결과 생성
        total_files = sum(1 for result in [refined_result, summarized_result, keypoints_result] if result is not None)
        
        response = SpeechRefineResponse(
            refined_result=refined_result,
            summarized_result=summarized_result,
            keypoints_result=keypoints_result,
            total_files=total_files,
            message=f"총 {total_files}개 PDF 파일이 생성되었습니다." if total_files > 0 else "PDF 파일 생성에 실패했습니다."
        )
        
        print(f"[PDF SERVICE] 처리 완료 - 생성된 PDF: {total_files}개")
        return response
        
    except Exception as e:
        raise Exception(f"[PDF SERVICE ERROR] PDF 생성 실패 - {str(e)}")

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