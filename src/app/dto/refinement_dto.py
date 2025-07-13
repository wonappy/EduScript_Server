# [dto/refinement_dto.py] 
# 발화 정제 요청 & 응답 클래스 
import json
from src.app.modules.file.file_data import FileData
from pydantic import BaseModel
from typing import Optional, List

# [1] 발화 정제
# Request
class SpeechRefineRequest(BaseModel):
    full_text: str
    fileName : str = "speech"  # 기본 파일 이름
    fileFormat: str = "txt"  # 기본 파일 형식은 txt

    # 언어 설정
    language_list: List[str] = ["ko"]

    # 문서 타입 설정
    enable_refine: bool = True
    enable_summarize: bool = False
    enable_keypoints: bool = False
    
    processing_mode: str = "lecture"

# Response
class SpeechRefineResponse(BaseModel):
    # 단일 파일 (기존 구조 호환)
    refined_result: Optional[FileData] = None
    summarized_result: Optional[FileData] = None
    keypoints_result: Optional[FileData] = None

    # 다국어 지원용 멀티 파일 리스트
    refined_results: List[FileData] = []
    summarized_results: List[FileData] = []
    keypoints_results: List[FileData] = []

    total_files: int = 0
    message: str = ""

    def get_available_files(self) -> List[FileData]:
        """실제로 생성된 모든 파일 반환 (단일 + 다국어 파일 포함)"""
        return (
            [f for f in [self.refined_result, self.summarized_result, self.keypoints_result] if f]
            + self.refined_results
            + self.summarized_results
            + self.keypoints_results
        )

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