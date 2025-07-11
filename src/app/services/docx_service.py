# services/docx_service.py
from src.app.modules.llm.openai_llm import OpenAILLM
from src.app.modules.file.file_data import FileData
from src.app.dto.refinement_dto import SpeechRefineRequest, SpeechRefineResponse
from src.app.prompts.keypoints_prompt import extract_keypoints_prompt
from src.app.utils.docx_generator import create_docx_from_text

# LLM 모듈
llm_module = OpenAILLM()

# async def refine_text_to_docx_service(request: SpeechRefineRequest) -> SpeechRefineResponse:
#     """발화 정제 후 DOCX 파일로 생성하는 서비스"""
#     try:
#         print("=== [DOCX SERVICE DEBUG] ===")
#         print(">> DOCX 생성 서비스 시작")
        
#         # 1) 정제 프롬프트 설계
#         messages = [
#             {"role": "system", "content": refine_speech_prompt()},
#             {"role": "user", "content": f"{request.full_text}"}
#         ]
        
#         # 저장 변수 선언
#         refined_result = None
#         summarized_result = None
#         keypoints_result = None
        
#         # 2) LLM 모듈 호출 - 정제 처리
#         print(f"[DOCX DEBUG] API 호출 1 - 정제 시작")
#         temp_refined_text = await llm_module.select_gpt_model(messages=messages)
#         print(f"[DOCX DEBUG] API 호출 1 완료")
        
#         # 3) 정제 DOCX 파일 생성
#         if request.enable_refine:
#             refined_result = create_docx_from_text(
#                 text=temp_refined_text,
#                 filename=f"{request.fileName}_refined_speech.docx",
#                 user_filename=request.fileName
#             )
#             print(f"[DOCX SERVICE] 정제 DOCX 파일 생성 완료 - 크기: {refined_result.file_size} bytes")
        
#         # 4) 요약 처리
#         if request.enable_summarize:
#             print(f"[DOCX DEBUG] API 호출 2 - 요약 시작")
#             summarized_text = await summarize_text_docx(temp_refined_text)
#             print(f"[DOCX SERVICE] 요약 완료")
#             summarized_result = create_docx_from_text(
#                 text=summarized_text,
#                 filename=f"{request.fileName}_speech_summary.docx",
#                 user_filename=request.fileName
#             )
#             print(f"[DOCX SERVICE] 요약 DOCX 파일 생성 완료 - 크기: {summarized_result.file_size} bytes")
        
#         # 5) 중요 내용 추출 처리
#         if request.enable_keypoints:
#             keypoints_text = await extract_keypoints_docx(temp_refined_text)
#             print(f"[DOCX SERVICE] 중요 내용 추출 완료")
#             keypoints_result = create_docx_from_text(
#                 text=keypoints_text,
#                 filename=f"{request.fileName}_key_points.docx",
#                 user_filename=request.fileName
#             )
#             print(f"[DOCX SERVICE] 핵심포인트 DOCX 파일 생성 완료 - 크기: {keypoints_result.file_size} bytes")
        
#         # 6) 응답 결과 생성
#         total_files = sum(1 for result in [refined_result, summarized_result, keypoints_result] if result is not None)
        
#         response = SpeechRefineResponse(
#             refined_result=refined_result,
#             summarized_result=summarized_result,
#             keypoints_result=keypoints_result,
#             total_files=total_files,
#             message=f"총 {total_files}개 DOCX 파일이 생성되었습니다." if total_files > 0 else "DOCX 파일 생성에 실패했습니다."
#         )
        
#         print(f"[DOCX SERVICE] 처리 완료 - 생성된 DOCX: {total_files}개")
#         return response
        
#     except Exception as e:
#         raise Exception(f"[DOCX SERVICE ERROR] DOCX 생성 실패 - {str(e)}")

async def summarize_text_docx(temp_refined_text: str) -> str:
    """요약 텍스트 생성 (DOCX용)"""
    try:
        messages = [
            {"role": "system", "content": summarize_speech_prompt()},
            {"role": "user", "content": f"{temp_refined_text}"}
        ]
        return await llm_module.select_gpt_model(messages=messages)
    except Exception as e:
        raise Exception(f"[DOCX SERVICE ERROR] 요약 처리 실패 - {str(e)}")

async def extract_keypoints_docx(temp_refined_text: str) -> str:
    """중요 내용 추출 (DOCX용)"""
    try:
        messages = [
            {"role": "system", "content": extract_keypoints_prompt()},
            {"role": "user", "content": f"{temp_refined_text}"}
        ]
        return await llm_module.select_gpt_model(messages=messages)
    except Exception as e:
        raise Exception(f"[DOCX SERVICE ERROR] 중요 내용 추출 실패 - {str(e)}")