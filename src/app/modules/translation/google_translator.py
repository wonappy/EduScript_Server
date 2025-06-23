# [modules/translation/google_translator.py]
# google translator AI
import os
from google.cloud import translate_v2 as translate
import asyncio
import concurrent.futures

class GoogleTranslator:
    # [1] 초기화
    def __init__(self):
        # Google Translator 변수 초기화
        self.credentials_path = os.environ.get('GOOGLE_APPLICATION_CREDENTIALS')
        if not self.credentials_path:
            raise Exception("GOOGLE_APPLICATION_CREDENTIALS 환경변수가 설정되지 않았습니다")
        self.translator = None

    # [2] 번역 설정    
    def setup_translation(self) :
        """ 번역기 초기화 """ 
        # Google Translator 설정
        self.translator = translate.Client()
        print("Google Translator 초기화 완료")

    # [3] 번역 
    # 3-1) 다중 번역 실행 -> 다중 번역 결과 반환
    async def translate_multiple_languages(self, text, input_language, target_languages : list[str]):
        """텍스트를 여러 언어로 동시 번역"""
        # 결과 저장 변수
        results = {}

        # 원문 내용 저장 (가장 첫번째로 저장)
        results[input_language] = {
                'target_lang': input_language,
                'result_text': text,
            }
        
        # 비동기 루프 가져오기
        loop = asyncio.get_event_loop()

        # 스레드 풀 생성
        with concurrent.futures.ThreadPoolExecutor() as executor:
            # 언어 별 번역 처리 -> 별도 스레드 병렬 구조로 시간 단축!
            tasks = []
            for lang in target_languages:
                # Google Translation API는 동기 -> 각 스레드에서 동기 작업을 병렬로 처리
                task = loop.run_in_executor(executor, self.translate_text, text, lang)
                tasks.append((lang, task))      # task 추가
                
            # 각 번역 결과 저장
            for lang, task in tasks:
                result = await task 
                if result:
                    results[lang] = result
        
        #모든 번역 결과 반환
        return results
    
    # 3-2) 지정된 언어로 text 번역 -> 번역 결과 반환
    def translate_text(self, text, target_language : str):
        if not text:
            return None
            
        try:
            result = self.translator.translate(text, target_language=target_language)       # 번역 요청
            translated_text = result['translatedText']                                      # 번역 결과
            
            return {
                'target_lang': target_language,
                'result_text': translated_text,
            }
            
        except Exception as e:
            print(f"❌ {target_language} 번역 중 오류 발생: {e}")
            return None