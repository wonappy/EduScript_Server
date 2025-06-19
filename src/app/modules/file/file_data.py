# file_data.py
# 파일 데이터 모델 정의

from pydantic import BaseModel
import base64
from datetime import datetime


class FileData(BaseModel):
    filename: str
    content_type: str = "text/plain"
    data: str  # Base64 인코딩된 파일 데이터
    file_size: int
    created_at: datetime
    
    @classmethod
    def from_text(cls, text: str, filename: str, content_type: str = "text/plain"):
        encoded_data = base64.b64encode(text.encode('utf-8')).decode('utf-8')
        return cls(
            filename=filename,
            content_type=content_type,
            data=encoded_data,
            file_size=len(text.encode('utf-8')),
            created_at=datetime.now()
        )
    
    def to_text(self) -> str:
        """Base64 데이터를 텍스트로 디코딩"""
        return base64.b64decode(self.data).decode('utf-8')
    
    def save_to_file(self, filepath: str):
        """파일로 저장"""
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(self.to_text())