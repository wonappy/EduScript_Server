# [serivces/language_service.py]
# LLM 작업 로직 처리 
from src.app.modules.llm.openai_llm import OpenAILLM
from src.app.modules.file.file_data import FileData
from src.app.dto.refinement_dto import SpeechRefineRequest, SpeechRefineResponse
from src.app.prompts.refining_prompt import refine_speech_prompt
from src.app.prompts.summarizing_prompt import summarize_speech_prompt
from src.app.prompts.keypoints_prompt import extract_keypoints_prompt

# [0] LLM 모듈 
llm_module = OpenAILLM() 

# [1] 발화 정제
async def refine_text_service(self, request: SpeechRefineRequest) -> SpeechRefineResponse:
    try:        
        # [0] 디버깅 코드
        print("=== [SERVICE DEBUG] ===")
        print(">> Refine")
        print(f"[SERVICE] full_text: {request.full_text}")
        print(f"[SERIVCE] enable_refine: {request.enable_refine}")
        print(f"[SERIVCE] enable_summarize: {request.enable_summarize}")
        print(f"[SERIVCE] enable_keypoints: {request.enable_keypoints}")
                
        # 1) 정제 프롬프트 설계
        messages = [
            { "role": "system", "content": refine_speech_prompt() },
            { "role": "user", "content": f"{request.full_text}" } 
         ] 
        
        # 저장 변수 선언 
        refined_text = None
        summarized_text = None
        keypoints_text = None  

        # # 2) LLM 모듈 호출 (API) -> 정제 처리     
        temp_refined_text = await llm_module.select_gpt_model(messages=messages)  
        
        # 정제 파일 생성 여부
        if request.enable_refine == True:
                refined_result = FileData.from_text(
                    text=temp_refined_text,
                    filename="refined_speech.txt"
                )
                print(f"[SERVICE] 정제 파일 생성 완료 - 크기: {refined_result.file_size} bytes")
        # 3) 요약 처리    
        if request.enable_summarize == True:
                summarized_text = await self.summarize_text(temp_refined_text)
                summarized_result = FileData.from_text(
                    text=summarized_text,
                    filename="speech_summary.txt"
                )
                print(f"[SERVICE] 요약 파일 생성 완료 - 크기: {summarized_result.file_size} bytes")
        # 4) 중요 내용 추출 처리
        if request.enable_keypoints == True:
                keypoints_text = await self.extract_keypoints(temp_refined_text)
                keypoints_result = FileData.from_text(
                    text=keypoints_text,
                    filename="key_points.txt"
                )
                print(f"[SERVICE] 핵심포인트 파일 생성 완료 - 크기: {keypoints_result.file_size} bytes")

        # 5) 응답 결과 DTO (정제, 요약, 추출)
        total_files = sum(1 for result in [refined_result, summarized_result, keypoints_result] if result is not None)
        
        response = SpeechRefineResponse(
            refined_result=refined_result,
            summarized_result=summarized_result,
            keypoints_result=keypoints_result,
            total_files=total_files,
            message=f"총 {total_files}개 파일이 생성되었습니다." if total_files > 0 else "파일 생성에 실패했습니다."
        )

        print(f"[SERVICE] 처리 완료 - 생성된 파일: {total_files}개")
        return response
    
    except Exception as e:
        raise Exception(f"[SERVICE ERROR] 발화 정제 실패 - {str(e)}")

# [2] 발화 요약
async def summarize_text(temp_refined_text: str) -> str:
    try:        
        # [0] 디버깅 코드
        print(">> Summarize")
        print(f"[SERVICE] refined_text: {temp_refined_text}")
        
        # 1) 내용 요약 프롬프트 설계
        messages = [
            { "role": "system", "content": summarize_speech_prompt() },
            { "role": "user", "content": f"{temp_refined_text}" }
        ]
        # 2) LLM API 호출 (MODULE) -> 내용 요약 처리
        summarized_text = await llm_module.select_gpt_model(messages=messages)
        # 3) 요약 결과 문자열 
        return summarized_text
    except Exception as e:
        raise Exception(f"[SERIVCE ERROR] 발화 요약 처리 실패 - {str(e)}")

# [3] 중요 내용 추출
async def extract_keypoints(temp_refined_text: str) -> str:
    try:        
        # [0] 디버깅 코드
        print(">> Extract Keypoints") 
        print(f"[SERVICE] refined_text: {temp_refined_text}")

        # 1) 중요 내용 추출 프롬프트 설계
        messages = [
            { "role": "system", "content": extract_keypoints_prompt() },
            { "role": "user", "content": f"{temp_refined_text}" }
        ]

        # 2) LLM API 호출 (MODULE) -> 중요 내용 추출 처리
        keypoints_text = await llm_module.select_gpt_model(messages=messages)

        # 3) 추출 결과 반환 
        return keypoints_text
    except Exception as e:
        raise Exception(f"[SERIVCE ERROR] 중요 내용 추출 실패 - {str(e)}")