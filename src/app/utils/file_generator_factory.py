# src/app/utils/file_generator_factory.py
import json
from src.app.modules.file.file_data import FileData
from src.app.utils.pdf_generator import create_pdf_from_text
from src.app.utils.docx_generator import create_docx_from_text, create_meeting_minutes_docx  # 기존 함수 사용

def create_file_by_format(content: str, filename: str, file_format: str) -> FileData:
    """형식별 파일 생성"""
    if file_format.lower() == "pdf":
        return create_pdf_from_text(
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

def create_document_by_mode_and_format(mode: str, file_format: str, content: str, filename: str) -> FileData:
    """모드와 형식에 따른 문서 생성"""
    try:
        if file_format.lower() == "docx":
            if mode == "conference":
                return create_meeting_minutes_docx(
                    json_data=content,
                    filename=f"{filename}.docx",
                    user_filename=filename
                )
            else:  # lecture
                return create_docx_from_text(  #일반적인
                    text=content,
                    filename=f"{filename}.docx",
                    user_filename=filename
                )
        
        elif file_format.lower() == "pdf":
            if mode == "conference":
                return create_meeting_pdf(content, filename)
            else:  # lecture
                return create_pdf_from_text(
                    text=content,
                    filename=f"{filename}.pdf",
                    user_filename=filename
                )
        
        else:  # txt - 구조화된 JSON을 그대로 텍스트로
            return FileData.from_text(
                text=content,
                filename=f"{filename}.txt"
            )
    
    except Exception as e:
        print(f"[FILE FACTORY ERROR] 문서 생성 실패: {str(e)}")
        # 실패 시 기본 텍스트 파일로 폴백
        return FileData.from_text(
            text=content,
            filename=f"{filename}.txt"
        )

def create_meeting_pdf(json_content: str, filename: str) -> FileData:
    """회의록 PDF 생성"""
    # JSON을 텍스트로 변환 후 PDF 생성
    try:
        data = json.loads(json_content)
        formatted_text = format_meeting_for_pdf(data)
    except:
        formatted_text = json_content
    
    return create_pdf_from_text(
        text=formatted_text,
        filename=f"{filename}.pdf",
        user_filename=filename
    )

def format_meeting_for_pdf(data: dict) -> str:
    """회의 데이터를 PDF용 텍스트로 포맷팅"""
    lines = []
    
    if data.get('회의안건'):
        lines.append("=== 회의안건 ===")
        for i, agenda in enumerate(data['회의안건'], 1):
            lines.append(f"{i}. {agenda}")
        lines.append("")
    
    if data.get('회의내용'):
        lines.append("=== 회의내용 ===")
        for item in data['회의내용']:
            lines.append(f"• {item.get('내용', '')}")
            if item.get('비고'):
                lines.append(f"  비고: {item['비고']}")
        lines.append("")
    
    if data.get('결정사항'):
        lines.append("=== 결정사항 ===")
        for item in data['결정사항']:
            lines.append(f"• {item.get('내용', '')}")
            if item.get('진행일정'):
                lines.append(f"  일정: {item['진행일정']}")
        lines.append("")
    
    if data.get('특이사항'):
        lines.append("=== 특이사항 ===")
        lines.append(data['특이사항'])
    
    return "\n".join(lines)