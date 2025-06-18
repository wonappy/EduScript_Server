import asyncio
from modules.stt.azure_stt import AzureSTT
from app.modules.translation.google_translator import GoogleTranslator

class SpeechTranslationInterface:
    # [1] 초기화
    def __init__(self):
        """STT + Translation 인터페이스 초기화"""
         # STT & 번역기 초기화
        self.stt = AzureSTT()
        self.translator = GoogleTranslator()
        self.translator.setup_translation() 
                        
        # stt_translation 설정 변수
        self.current_input_language = None
        self.current_target_languages = None

        # 실행 상태 변수
        self.is_active = False  
        
    # [2] 실시간 번역 세션 시작
    async def start_session(self, input_language: str, target_languages: list[str]):
        """
        실시간 번역 세션 시작
        
        Args:
            input_language: 입력 언어 코드
            target_languages: 번역 대상 언어 리스트
        """
        try:
            # STT 설정 및 시작
            self.stt.setup_streaming_recognition(input_language)
            self.stt.start_recognition()
            
            # 현재 설정 저장
            self.current_input_language = input_language
            self.current_target_languages = target_languages
            self.is_active = True
            
            print(f"번역 세션 시작: {self.current_input_language} → {self.current_target_languages}")
            
        except Exception as e:
            print(f"!!!!!세션 시작 오류!!!!!: {e}")
            raise
    
    # [3] 음성 스트림 전달 -> 번역 결과 반환
    async def process_audio_with_translation(self, audio_data, target_languages : list[str], timeout=3.0):
        """
        오디오 청크 처리 - STT에 전달
        
        Args:
            audio_data: 오디오 바이트 데이터
            target_languages : 출력 언어 리스트
            timeout : stt 결과 대기 시간
        """
        # 1. 오디오 추가
        self.stt.write_audio_chunk(audio_data)

        # 타켓 언어 설정이 달라졌다면 -> self의 설정 언어도 변경
        if self.current_target_languages != target_languages:
            self.current_target_languages = target_languages
            print(f"언어 설정 : {self.current_input_language} -> {self.current_target_languages}")
        
        # 2. 결과 체크 (timeout 동안만 결과값 대기 -> 블로킹 방지)
        try:
            text = await asyncio.wait_for(
                self.stt.get_recognition_result(), 
                timeout=timeout
            )
            if text:
                return await self.translator.translate_multiple_languages(text, self.current_input_language, self.current_target_languages)   # 번역 결과값 반환
        except asyncio.TimeoutError:
            return None  # 결과 없으면 즉시 None 반환
    
    # [3-1] 음성 인식 언어 변경
    async def change_language_settings(self, input_language: str):
        """
        언어 설정 변경
        
        Args:
            input_language: 새로운 입력 언어
        """
        try:
            print(f"입력 언어 설정 변경: {input_language}")

            # 새 설정 저장
            self.current_input_language = input_language
            
            # STT 언어 변경 (기존 세션 종료 -> 재시작)
            self.stt.change_setup_recognition(self.current_input_language)
            
            print(f"언어 설정 변경 완료: {self.current_input_language} -> {self.current_target_languages}")
            
        except Exception as e:
            print(f"언어 변경 오류: {e}")
            raise
    
    # [4] 세션 
    def stop_session(self):
        """번역 세션 종료"""
        try:
            if self.is_active:
                self.stt.stop_recognition()
                self.is_active = False
                print("✅ 번역 세션 종료")
        except Exception as e:
            print(f"❌ 세션 종료 오류: {e}")
    
    # 현재 세션 상태 확인
    def get_status(self):
        """현재 상태 반환"""
        return {
            'is_active': self.is_active,
            'input_language': self.current_input_language,
            'stt_active': self.stt.is_active() if self.stt else False
        }