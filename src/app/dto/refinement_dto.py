# [dto/refinement_dto.py] 
# 발화 정제 요청 & 응답 클래스 
from src.app.modules.file.file_data import FileData
from pydantic import BaseModel
from typing import Optional, List

# [1] 발화 정제
# Request
class SpeechRefineRequest(BaseModel):
    full_text: str
    fileName : str = "speech"  # 기본 파일 이름
    fileFormat: str = "txt"  # 기본 파일 형식은 txt
    enable_refine: bool = True
    enable_summarize: bool = False
    enable_keypoints: bool = False 

# Response
class SpeechRefineResponse(BaseModel):
    refined_result: Optional[FileData] = None
    summarized_result: Optional[FileData] = None
    keypoints_result: Optional[FileData] = None

    def get_available_files(self) -> List[FileData]:
        """실제로 생성된 파일들만 반환"""
        files = []
        if self.refined_result:
            files.append(self.refined_result)
        if self.summarized_result:
            files.append(self.summarized_result)
        if self.keypoints_result:
            files.append(self.keypoints_result)
        return files

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