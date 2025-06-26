# utils/pdf_generator.py
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from io import BytesIO
from src.app.modules.file.file_data import FileData

def create_pdf_from_text(text: str, filename: str) -> FileData:
    """텍스트를 PDF로 변환하여 FileData 객체 생성"""
    try:
        buffer = BytesIO()
        
        # PDF 문서 생성
        doc = SimpleDocTemplate(buffer, pagesize=A4, 
                              leftMargin=50, rightMargin=50,
                              topMargin=50, bottomMargin=50)
        
        # 스타일 설정
        styles = getSampleStyleSheet()
        
        # 한글 지원을 위한 스타일 (시스템에 한글 폰트가 있다면)
        try:
            # 한글 폰트 경로는 시스템에 맞게 수정 필요
            pdfmetrics.registerFont(TTFont('NanumGothic', '/usr/share/fonts/truetype/nanum/NanumGothic.ttf'))
            korean_style = ParagraphStyle(
                'Korean',
                parent=styles['Normal'],
                fontName='NanumGothic',
                fontSize=12,
                leading=18,
                spaceAfter=12,
            )
        except:
            # 한글 폰트 없으면 기본 폰트 사용
            korean_style = ParagraphStyle(
                'Korean',
                parent=styles['Normal'],
                fontSize=12,
                leading=18,
                spaceAfter=12,
            )
        
        # 제목 스타일
        title_style = ParagraphStyle(
            'Title',
            parent=korean_style,
            fontSize=16,
            leading=24,
            spaceAfter=20,
            alignment=1,  # 가운데 정렬
        )
        
        # 문서 내용 구성
        story = []
        
        # 제목 추가 (파일명에서 확장자 제거)
        title = filename.replace('.pdf', '').replace('_', ' ').title()
        story.append(Paragraph(title, title_style))
        story.append(Spacer(1, 20))
        
        # 텍스트 내용을 줄바꿈으로 분할하여 추가
        paragraphs = text.split('\n')
        for para in paragraphs:
            if para.strip():  # 빈 줄이 아닌 경우만
                story.append(Paragraph(para.strip(), korean_style))
            else:
                story.append(Spacer(1, 12))  # 빈 줄 공간
        
        # PDF 생성
        doc.build(story)
        
        # BytesIO에서 데이터 가져오기
        pdf_data = buffer.getvalue()
        buffer.close()
        
        # FileData 객체 생성
        return FileData.from_bytes(
            data=pdf_data,
            filename=filename,
            content_type="application/pdf"
        )
        
    except Exception as e:
        raise Exception(f"PDF 생성 실패: {str(e)}")