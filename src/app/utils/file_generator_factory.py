# src/app/utils/file_generator_factory.py
import json
from src.app.modules.file.file_data import FileData
from src.app.utils.pdf_generator import util_pdf_from_text
from src.app.utils.docx_generator import create_docx_from_text, create_meeting_minutes_docx  # 기존 함수 사용

def create_file_by_format(content: str, filename: str, file_format: str) -> FileData:
    """형식별 파일 생성"""
    if file_format.lower() == "pdf":
        return util_pdf_from_text(
            text=content,
            filename=f"{filename}.pdf",
            user_filename=filename
        )
    elif file_format.lower() == "docx":
        return create_docx_from_text(
            text=content,
            filename=f"{filename}.docx",
            user_filename=filename
        )
    else:  # txt
        return FileData.from_text(
            text=content,
            filename=f"{filename}.txt"
        )

# def create_document_by_mode_and_format(mode: str, file_format: str, content: str, filename: str) -> FileData:
#     """모드와 형식에 따른 문서 생성"""
#     try:
#         if file_format.lower() == "docx":
#             if mode == "conference":
#                 return create_meeting_minutes_docx(
#                     json_data=content,
#                     filename=f"{filename}.docx",
#                     user_filename=filename
#                 )
#             else:  # lecture
#                 return create_docx_from_text(  #일반적인
#                     text=content,
#                     filename=f"{filename}.docx",
#                     user_filename=filename
#                 )
        
#         elif file_format.lower() == "pdf":
#             if mode == "conference":
#                 return create_meeting_pdf(content, filename)
#             else:  # lecture
#                 return create_pdf_from_text(
#                     text=content,
#                     filename=f"{filename}.pdf",
#                     user_filename=filename
#                 )
        
#         else:  # txt - 구조화된 JSON을 그대로 텍스트로
#             return FileData.from_text(
#                 text=content,
#                 filename=f"{filename}.txt"
#             )
    
#     except Exception as e:
#         print(f"[FILE FACTORY ERROR] 문서 생성 실패: {str(e)}")
#         # 실패 시 기본 텍스트 파일로 폴백
#         return FileData.from_text(
#             text=content,
#             filename=f"{filename}.txt"
#         )