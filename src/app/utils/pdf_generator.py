# utils/pdf_generator.py (안전한 버전)
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from io import BytesIO
import os
import platform
from src.app.modules.file.file_data import FileData

def get_korean_font():
    """시스템에 따라 한글 폰트 경로 반환"""
    system = platform.system()
    
    if system == "Windows":
        fonts = [
            "C:/Windows/Fonts/malgun.ttf",
            "C:/Windows/Fonts/batang.ttc",
            "C:/Windows/Fonts/gulim.ttc",
        ]
    elif system == "Darwin":  # macOS
        fonts = [
            "/System/Library/Fonts/AppleSDGothicNeo.ttc",
            "/Library/Fonts/Arial Unicode MS.ttf",
        ]
    else:  # Linux
        fonts = [
            "/usr/share/fonts/truetype/nanum/NanumGothic.ttf",
            "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        ]
    
    for font_path in fonts:
        if os.path.exists(font_path):
            return font_path
    return None

def safe_wrap_text(text, max_chars=60):
    """안전한 문자 수 기반 줄바꿈"""
    if not text.strip():
        return ['']
    
    # 긴 줄을 적절히 분할
    lines = []
    current_line = ''
    
    # 공백 기준으로 단어 분리
    words = text.split(' ')
    
    for word in words:
        # 단어가 너무 길면 강제로 자르기
        while len(word) > max_chars:
            if current_line:
                lines.append(current_line)
                current_line = ''
            lines.append(word[:max_chars])
            word = word[max_chars:]
        
        # 현재 줄에 단어 추가 가능한지 확인
        test_line = current_line + (' ' if current_line else '') + word
        if len(test_line) <= max_chars:
            current_line = test_line
        else:
            if current_line:
                lines.append(current_line)
            current_line = word
    
    # 마지막 줄 추가
    if current_line:
        lines.append(current_line)
    
    return lines if lines else ['']

def util_pdf_from_text(text: str, filename: str, user_filename: str) -> FileData:
    """안전한 PDF 생성 함수"""
    try:   
        buffer = BytesIO()

        print(f"[PDF DEBUG] PDF 생성 시작 - 파일명: {filename}")
        print(f"[PDF DEBUG] 사용자 파일명: {user_filename}")
        print(f"[PDF DEBUG] 텍스트 길이: {len(text)} 문자")

        # 파일명에서 문서 타입 추출
        document_type = ""
        if "refined" in filename:
            document_type = " - 정제된 내용"
        elif "summary" in filename:
            document_type = " - 요약"
        elif "key_points" in filename:
            document_type = " - 핵심 포인트"
        
        # 제목 생성
        title = user_filename + document_type
        print(f"[PDF DEBUG] 최종 제목: '{title}'")

        # PDF 캔버스 생성
        c = canvas.Canvas(buffer, pagesize=A4)
        width, height = A4

        # 여백 설정
        left_margin = 50
        right_margin = 50
        top_margin = 50
        bottom_margin = 50

        print(f"[PDF DEBUG] 캔버스 생성 완료")

        # 폰트 설정 (안전하게)
        font_name = 'Helvetica'  # 기본 폰트로 시작
        
        korean_font_path = get_korean_font()
        if korean_font_path:
            try:
                pdfmetrics.registerFont(TTFont('KoreanFont', korean_font_path))
                font_name = 'KoreanFont'
                print(f"[PDF DEBUG] 한글 폰트 등록 성공: {korean_font_path}")
            except Exception as e:
                print(f"[PDF DEBUG] 한글 폰트 등록 실패, 기본 폰트 사용: {e}")
                font_name = 'Helvetica'
        else:
            print(f"[PDF DEBUG] 한글 폰트 없음, 기본 폰트 사용")

        # 제목 추가
        title_font_size = 16
        try:
            c.setFont(font_name, title_font_size)
            c.drawString(left_margin, height - top_margin, title)
            print(f"[PDF DEBUG] 제목 추가 성공")
        except Exception as e:
            print(f"[PDF DEBUG] 제목 추가 실패, 기본 폰트로 재시도: {e}")
            c.setFont('Helvetica', title_font_size)
            # 한글이 깨질 수 있지만 ASCII 문자로 대체
            safe_title = ''.join(char if ord(char) < 128 else '?' for char in title)
            c.drawString(left_margin, height - top_margin, safe_title)
        
        # 본문 시작 위치
        y_position = height - top_margin - 40
        body_font_size = 12
        line_height = 18
        
        print(f"[PDF DEBUG] 텍스트 처리 시작")
        
        # 문단별로 처리 (안전하게)
        paragraphs = text.split('\n')
        total_lines = 0
        
        for para_idx, paragraph in enumerate(paragraphs):
            if not paragraph.strip():
                # 빈 줄 처리
                y_position -= line_height
                if y_position < bottom_margin + line_height:
                    c.showPage()
                    y_position = height - top_margin
                continue
            
            # 안전한 줄바꿈
            wrapped_lines = safe_wrap_text(paragraph, 80)
            total_lines += len(wrapped_lines)
            
            print(f"[PDF DEBUG] 문단 {para_idx+1}: {len(wrapped_lines)}줄")
            
            for line in wrapped_lines:
                # 페이지 끝 체크
                if y_position < bottom_margin + line_height:
                    c.showPage()
                    y_position = height - top_margin
                    print(f"[PDF DEBUG] 새 페이지 생성")
                
                # 텍스트 그리기 (안전하게)
                try:
                    c.setFont(font_name, body_font_size)
                    c.drawString(left_margin, y_position, line)
                except Exception as e:
                    print(f"[PDF DEBUG] 텍스트 그리기 오류, 안전 모드: {e}")
                    # 문제가 있는 문자는 '?'로 대체
                    safe_line = ''.join(char if ord(char) < 128 else '?' for char in line)
                    c.setFont('Helvetica', body_font_size)
                    c.drawString(left_margin, y_position, safe_line)
                
                y_position -= line_height
        
        print(f"[PDF DEBUG] 텍스트 처리 완료 - 총 {total_lines}줄")
        
        # PDF 저장
        c.save()
        print(f"[PDF DEBUG] PDF 저장 완료")

        # 바이트 데이터 가져오기
        pdf_bytes = buffer.getvalue()
        buffer.close()
        
        print(f"[PDF DEBUG] PDF 크기: {len(pdf_bytes)} bytes")
        print(f"[PDF DEBUG] PDF 헤더: {pdf_bytes[:20]}")
        
        # PDF 헤더 검증
        if not pdf_bytes.startswith(b'%PDF-'):
            raise Exception("생성된 PDF에 올바른 헤더가 없습니다")
        
        print(f"[PDF DEBUG] PDF 헤더 검증 완료")
        
        # FileData 객체 생성
        file_data = FileData.from_bytes(
            data=pdf_bytes,
            filename=filename,
            content_type="application/pdf"
        )

        print(f"[PDF DEBUG] FileData 생성 완료 - 파일크기: {file_data.file_size}")
        return file_data
        
    except Exception as e:
        print(f"[PDF ERROR] PDF 생성 실패: {str(e)}")
        import traceback
        traceback.print_exc()
        raise Exception(f"PDF 생성 실패: {str(e)}")

