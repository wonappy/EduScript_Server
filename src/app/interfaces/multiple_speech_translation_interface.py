# [interfaces/multiple_speech_translation_interface.py]
# 실시간 번역 인터페이스 (AI 모듈 조합)
import asyncio
from src.app.modules.stt.azure_stt_multiple import AzureSTTMultiple
from src.app.modules.translation.google_translator import GoogleTranslator

class MultipleSpeechTranslationInterface:
    # [1] 초기화
    def __init__(self):
        """STT + Translation 인터페이스 초기화"""
         # STT &번역기 초기화
        self.stt = AzureSTTMultiple()
        self.translator = GoogleTranslator()
        self.translator.setup_translation() 
                        
        # stt 설정 변수
        self.current_input_languages = None
        self.current_target_languages = None

        # 실행 상태 변수
        self.is_active = False  

        # 번역 결과 저장 큐
        self.translation_result_queue = asyncio.Queue()

         # 백그라운드 태스크 관리
        self.background_tasks = []
        
    # [2] 실시간 번역 세션 시작
    async def start_session(self, input_languages: list[str], target_languages: list[str]):
        """
        실시간 번역 세션 시작
        
        Args:
            input_language: 입력 언어 코드
            target_languages: 번역 대상 언어 리스트
        """
        try:
            # STT 설정 및 시작
            print("STT 세션 시작 시도 중...")
            self.stt.setup_streaming_recognition(input_languages)
            self.stt.start_recognition()
            
            # 현재 설정 저장
            self.current_input_languages = input_languages
            self.current_target_languages = target_languages
            self.is_active = True

            # STT 결과를 지속적으로 처리하는 백그라운드 태스크 시작
            task = asyncio.create_task(self._process_stt_results())
            self.background_tasks.append(task)
            
            print(f"번역 세션 시작: {self.current_input_languages} → {self.current_target_languages}")
            
        except Exception as e:
            print(f"!!!!!세션 시작 오류!!!!!: {e}")
            raise

    # [] STT 결과 번역
    async def _process_stt_results(self):
        """STT 결과를 지속적으로 처리하고 번역하는 백그라운드 태스크"""
        print("STT 결과 처리 태스크 시작")
        
        while self.is_active:
            try:
                # STT에서 결과 가져오기 (논블로킹)
                stt_result = await self.stt.get_recognition_result()
                
                if stt_result and isinstance(stt_result, dict) and stt_result.get('text', '').strip():
                    print(f"STT 결과 받음: {stt_result['language']} - \"{stt_result['text']}\" (최종: {stt_result.get('is_final')})")
                    
                    # 값 추출
                    is_final = stt_result.get('is_final', False)
                    text = stt_result.get('text')
                    language = stt_result.get('language')

                    # recognized인 경우에만 번역 처리
                    if is_final == True:
                        # 번역 태스크 시작 (백그라운드에서 처리)
                        asyncio.create_task(self._translate_and_queue(text, language, is_final))
                    else:
                        # recognizing인 경우에는 번역 x
                        raw_result = {
                            'is_final': False    
                        }

                        # 현재 발화 언어
                        simple_lang_code = language.split('-')[0];

                        for lang in self.current_target_languages:
                            if lang == simple_lang_code:
                                raw_result[simple_lang_code] = {
                                    'target_lang': lang,
                                    'result_text': text
                                }
                            else:
                                raw_result[lang] = {
                                    'target_lang': lang,
                                    'result_text': "..."
                                } # 번역 x 원문 그대로 대입

                        # 번역 결과를 큐에 저장
                        await self.translation_result_queue.put(raw_result)
                
                # 짧은 대기 후 다시 확인
                await asyncio.sleep(0.1)
                
            except Exception as e:
                print(f"STT 결과 처리 오류: {e}")
                # 에러가 발생해도 계속 실행
                await asyncio.sleep(0.5)
        
        print("STT 결과 처리 태스크 종료")
    
    # [] 논블로킹 음성 스트림
    def process_audio_chunk(self, audio_data):
        """
        오디오 청크를 논블로킹 방식으로 처리
        
        Args:
            audio_data: 오디오 바이트 데이터
        """
        if not self.is_active:
            return
            
        # STT에 오디오 데이터 전달 (즉시 반환)
        self.stt.write_audio_chunk(audio_data)

    # [] 번역 후 결과 큐에 저장
    async def _translate_and_queue(self, text, language, is_final):
        """텍스트를 번역하고 결과 큐에 저장"""
        try:
            print(f"번역 시작: {language} - \"{text}")

            input_language = language
            
            # 번역 실행
            translation_result = await self.translator.translate_multiple_languages(
                text, 
                input_language, 
                self.current_target_languages
            )
            
            if translation_result:
                # 번역 결과에 stt 모드 값 추가
                translation_result['is_final'] = is_final

                print(f"번역 완료: (최종: {is_final}): {list(translation_result.keys())}")
                # 번역 결과를 큐에 저장
                await self.translation_result_queue.put(translation_result)
            
        except Exception as e:
            print(f"번역 처리 오류: {e}")

    # [] 최신 번역 결과 가져오기
    async def get_latest_translation_result(self):
        """최신 번역 결과를 논블로킹으로 가져오기"""
        try:
            # 큐에서 결과를 논블로킹으로 가져오기
            return self.translation_result_queue.get_nowait()
        except:
            # 큐가 비어있으면 None 반환
            return None

    # [3] 음성 스트림 전달 -> 번역 결과 반환
    # async def process_audio_with_translation(self, audio_data, target_languages : list[str], timeout=3.0):
    #     """
    #     오디오 청크 처리 - STT에 전달
        
    #     Args:
    #         audio_data: 오디오 바이트 데이터
    #         target_languages : 출력 언어 리스트
    #         timeout : stt 결과 대기 시간
    #     """
    #     # 1. 오디오 추가
    #     self.stt.write_audio_chunk(audio_data)
        
    #     # 2. 결과 체크 (timeout 동안만 결과값 대기 -> 블로킹 방지)
    #     try:
    #         text = await asyncio.wait_for(
    #             self.stt.get_recognition_result(), 
    #             timeout=timeout
    #         )
    #         if text:
    #             return await self.translator.translate_multiple_languages(text, self.current_input_language, self.current_target_languages)   # 번역 결과값 반환
    #     except asyncio.TimeoutError:
    #         return None  # 결과 없으면 즉시 None 반환
    
    # [3-1] 음성 인식 언어 변경
    async def change_input_language_settings(self, input_languages: list[str]):
        """
        언어 설정 변경
        
        Args:
            input_languages: 새로운 입력 언어들
        """
        try:
            print(f"입력 언어 설정 변경: {input_languages}")

            # 새 설정 저장
            self.current_input_languages = input_languages
            
            # STT 언어 변경 (기존 세션 종료 -> 재시작)
            self.stt.change_setup_recognition(self.current_input_languages)
            
            print(f"언어 설정 변경 완료: {self.current_input_languages} -> {self.current_target_languages}")
            
        except Exception as e:
            print(f"언어 변경 오류: {e}")
            raise
    
    # [3-2] 번역 언어 변경
    async def change_target_languages_settings(self, target_languages: list[str]):
        """
        언어 설정 변경
        
        Args:
            targer_languages: 변경된 번역 언어
        """
        try:
            print(f"번역 언어 설정 변경: {target_languages}")

            # 새 설정 저장
            self.current_target_languages= target_languages
            
            print(f"언어 설정 변경 완료: {self.current_input_languages} -> {self.current_target_languages}")
            
        except Exception as e:
            print(f"언어 변경 오류: {e}")
            raise

    # [4] 세션 
    def stop_session(self):
        """번역 세션 종료"""
        try:
            if self.is_active:
                self.is_active = False

                # 백그라운드 태스크 정리
                for task in self.background_tasks:
                    if not task.done():
                        task.cancel()
                self.background_tasks.clear()
                
                self.stt.stop_recognition()
                
                print("번역 세션 종료")
        except Exception as e:
            print(f"세션 종료 오류: {e}")
    
    # 현재 세션 상태 확인
    def get_status(self):
        """현재 상태 반환"""
        return {
            'is_active': self.is_active,
            'input_languages': self.current_input_languages,
            'stt_active': self.stt.is_active() if self.stt else False
        }