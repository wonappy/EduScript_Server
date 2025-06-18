# [dto/refinement_dto.py] 
# 발화 정제 요청 & 응답 클래스 
from pydantic import BaseModel
from typing import Optional

# [1] 발화 정제
# Request
class SpeechRefineRequest(BaseModel):
    full_text: str    
    enable_refine: bool = True
    enable_summarize: bool = False
    enable_keypoints: bool = False 

# Response
class SpeechRefineResponse(BaseModel):
    refined_result: Optional[str] = None
    summarized_result: Optional[str] = None
    keypoints_result: Optional[str] = None

# 🔴 나중에 삭제
# # [2] 발화 요약 
# # Request
# class SpeechSummarizeRequest(BaseModel):
#     refined_result: str

# # Response
# class SpeechSummarizeResponse(BaseModel):
#     summary_result: str

# # [3] 중요 내용 추출 
# # Request
# class KeyPointsExtractRequest(BaseModel):
#     refined_result: str

# # Response
# class KeyPointsExtractResponse(BaseModel):
#     keypoints_result: str