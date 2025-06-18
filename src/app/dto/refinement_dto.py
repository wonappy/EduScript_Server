# [dto/refinement_dto.py] 
# 발화 정제 요청 & 응답 클래스 
from pydantic import BaseModel

# [1] 발화 정제
# Request
class SpeechRefineRequest(BaseModel):
    full_speech: str    

# Response
class SpeechRefineResponse(BaseModel):
    refined_speech: str

# [2] 발화 요약 
# Request
class SpeechSummarizeRequest(BaseModel):
    refined_speech: str

# Response
class SpeechSummarizeResponse(BaseModel):
    summarized_speech: str

# [3] 중요 내용 추출 
# Request
class KeyPointsExtractRequest(BaseModel):
    refined_speech: str

# Response
class KeyPointsExtractResponse(BaseModel):
    extracted_keypoints: str