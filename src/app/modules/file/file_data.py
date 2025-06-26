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
    
    @classmethod
    def from_bytes(cls, data: bytes, filename: str, content_type: str):
        """바이트 데이터에서 FileData 생성 (PDF용)"""
        encoded_data = base64.b64encode(data).decode('utf-8')
        return cls(
            filename=filename,
            content_type=content_type,
            data=encoded_data,
            file_size=len(data),
            created_at=datetime.now()
        )
    
    def to_text(self) -> str:
        """Base64 데이터를 텍스트로 디코딩"""
        return base64.b64decode(self.data).decode('utf-8')
    
    def to_bytes(self) -> bytes:
        """Base64 데이터를 바이트로 디코딩 (PDF, 이미지 등)"""
        return base64.b64decode(self.data)
    
    def save_to_file(self, filepath: str):
        """파일로 저장 (자동으로 텍스트/바이너리 구분)"""
        if self.content_type.startswith('text/'):
            # 텍스트 파일
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(self.to_text())
        else:
            # 바이너리 파일 (PDF, 이미지 등)
            with open(filepath, 'wb') as f:
                f.write(self.to_bytes())

    @property
    def is_text_file(self) -> bool:
        """텍스트 파일인지 확인"""
        return self.content_type.startswith('text/')
    
    @property
    def is_pdf_file(self) -> bool:
        """PDF 파일인지 확인"""
        return self.content_type == "application/pdf"