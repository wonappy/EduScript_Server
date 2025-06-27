# utils/docx_generator.py
from docx import Document
from docx.shared import Inches, Pt
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.style import WD_STYLE_TYPE
from io import BytesIO
from src.app.modules.file.file_data import FileData

def create_docx_from_text(text: str, filename: str, user_filename: str) -> FileData:
    """텍스트를 DOCX로 변환하여 FileData 객체 생성"""
    try:
        print(f"[DOCX DEBUG] DOCX 생성 시작 - 파일명: {filename}")
        print(f"[DOCX DEBUG] 사용자 파일명: {user_filename}")
        print(f"[DOCX DEBUG] 텍스트 길이: {len(text)} 문자")
        
        # Document 객체 생성
        doc = Document()
        
        # 문서 여백 설정 (선택사항)
        sections = doc.sections
        for section in sections:
            section.top_margin = Inches(1)
            section.bottom_margin = Inches(1)
            section.left_margin = Inches(1)
            section.right_margin = Inches(1)
        
        # 파일명에서 문서 타입 추출
        document_type = ""
        if "refined" in filename:
            document_type = " - 정제된 내용"
        elif "summary" in filename:
            document_type = " - 요약"
        elif "key_points" in filename:
            document_type = " - 핵심 포인트"
        
        # 제목 생성 및 추가
        title = user_filename + document_type
        print(f"[DOCX DEBUG] 제목: '{title}'")
        
        # 제목 스타일 추가
        title_paragraph = doc.add_heading(title, 0)  # 0 = 가장 큰 제목
        title_paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER
        
        # 빈 줄 추가
        doc.add_paragraph()
        
        print(f"[DOCX DEBUG] 텍스트 처리 시작")
        
        # 본문 처리
        paragraphs = text.split('\n')
        total_paragraphs = 0
        
        for para_idx, paragraph in enumerate(paragraphs):
            if not paragraph.strip():
                # 빈 줄 처리
                doc.add_paragraph()
                continue
            
            # 문단 추가
            p = doc.add_paragraph()
            run = p.add_run(paragraph)
            
            # 폰트 설정 (선택사항)
            run.font.size = Pt(12)  # 12pt 폰트
            
            total_paragraphs += 1
            
            if para_idx < 5:  # 처음 5개 문단만 로그 출력
                print(f"[DOCX DEBUG] 문단 {para_idx+1}: '{paragraph[:30]}...'")
        
        print(f"[DOCX DEBUG] 텍스트 처리 완료 - 총 {total_paragraphs}개 문단")
        
        # BytesIO에 저장
        buffer = BytesIO()
        doc.save(buffer)
        
        docx_bytes = buffer.getvalue()
        buffer.close()
        
        print(f"[DOCX DEBUG] DOCX 크기: {len(docx_bytes)} bytes")
        
        # DOCX 헤더 확인 (ZIP 파일 형태)
        if not docx_bytes.startswith(b'PK'):
            raise Exception("생성된 DOCX에 올바른 헤더가 없습니다")
        
        print(f"[DOCX DEBUG] DOCX 헤더 검증 완료")
        
        # FileData 객체 생성
        file_data = FileData.from_bytes(
            data=docx_bytes,
            filename=filename,
            content_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        )
        
        print(f"[DOCX DEBUG] FileData 생성 완료 - 파일크기: {file_data.file_size}")
        return file_data
        
    except Exception as e:
        print(f"[DOCX ERROR] DOCX 생성 실패: {str(e)}")
        import traceback
        traceback.print_exc()
        raise Exception(f"DOCX 생성 실패: {str(e)}")

# # 고급 버전 (더 많은 서식 지원)
# def create_advanced_docx_from_text(text: str, filename: str, user_filename: str) -> FileData:
#     """고급 서식이 적용된 DOCX 생성"""
#     try:
#         print(f"[ADVANCED DOCX] 고급 DOCX 생성 시작")
        
#         doc = Document()
        
#         # 문서 타입별 스타일 설정
#         document_type = ""
#         if "refined" in filename:
#             document_type = "정제된 내용"
#             header_color = "0066CC"  # 파란색
#         elif "summary" in filename:
#             document_type = "요약"
#             header_color = "009900"  # 녹색
#         elif "key_points" in filename:
#             document_type = "핵심 포인트"
#             header_color = "CC6600"  # 주황색
#         else:
#             document_type = "문서"
#             header_color = "000000"  # 검은색
        
#         # 메인 제목
#         title = doc.add_heading(user_filename, 0)
#         title.alignment = WD_ALIGN_PARAGRAPH.CENTER
        
#         # 부제목
#         if document_type:
#             subtitle = doc.add_heading(document_type, 1)
#             subtitle.alignment = WD_ALIGN_PARAGRAPH.CENTER
        
#         # 구분선
#         doc.add_paragraph("─" * 50).alignment = WD_ALIGN_PARAGRAPH.CENTER
#         doc.add_paragraph()
        
#         # 본문 처리 (문단별로 스타일 적용)
#         paragraphs = text.split('\n\n')  # 빈 줄 기준으로 문단 분리
        
#         for para_idx, paragraph in enumerate(paragraphs):
#             if not paragraph.strip():
#                 continue
            
#             # 문단 추가
#             p = doc.add_paragraph()
            
#             # 첫 번째 문단은 들여쓰기 없음
#             if para_idx > 0:
#                 p.paragraph_format.first_line_indent = Inches(0.25)
            
#             # 줄 간격 설정
#             p.paragraph_format.line_spacing = 1.2
#             p.paragraph_format.space_after = Pt(6)
            
#             # 텍스트 추가
#             run = p.add_run(paragraph.strip())
#             run.font.size = Pt(12)
        
#         # 푸터 추가
#         doc.add_paragraph()
#         footer = doc.add_paragraph("─" * 50)
#         footer.alignment = WD_ALIGN_PARAGRAPH.CENTER
        
#         # 생성 정보
#         from datetime import datetime
#         timestamp = datetime.now().strftime("%Y년 %m월 %d일 %H:%M")
#         info = doc.add_paragraph(f"생성일시: {timestamp}")
#         info.alignment = WD_ALIGN_PARAGRAPH.RIGHT
        
#         # 저장
#         buffer = BytesIO()
#         doc.save(buffer)
        
#         docx_bytes = buffer.getvalue()
#         buffer.close()
        
#         return FileData.from_bytes(
#             data=docx_bytes,
#             filename=filename,
#             content_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
#         )
        
#     except Exception as e:
#         print(f"[ADVANCED DOCX ERROR] {str(e)}")
#         # 실패하면 기본 버전으로 fallback
#         return create_docx_from_text(text, filename, user_filename)