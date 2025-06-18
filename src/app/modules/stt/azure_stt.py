# [modules/stt/azure_stt.py]
# Azure Speech to Text AI
import os
import azure.cognitiveservices.speech as speechsdk
import asyncio  #async 선언이 안된 동기 함수에서 비동기 함수를 사용할 때 필요한 라이브러리

class AzureSTT:
    # [1] 초기화
    def __init__(self):
        # stt 변수 초기화
        self.azure_key = os.environ['AZURE_STT_KEY']
        self.azure_region = os.environ['AZURE_REGION']
        self.speech_recognizer = None
        self.audio_stream = None
        self.is_listening = False   # 음성 인식 중복 방지
        self.result_queue = None    # stt 결과 저장 함수 (동기 저장 -> 비동기 추출)

    # [2] 음성 인식 설정
    def setup_streaming_recognition(self, input_language: str) : 
        """
        실시간 스트리밍 음성 인식 설정
        input_language : 입력 언어 코드
        """

        # stt 결과 저장 queue 생성
        if self.result_queue is None:
            self.result_queue = asyncio.Queue()

        #speech 설정
        speech_config = speechsdk.SpeechConfig(
            subscription=self.azure_key,
            region=self.azure_region
        )
        #인식 언어 설정
        speech_config.speech_recognition_language = input_language

        #오디오 설정
        audio_format = speechsdk.audio.AudioStreamFormat(
            samples_per_second=16000, 
            bits_per_sample=16, 
            channels=1
        )
        self.audio_stream = speechsdk.audio.PushAudioInputStream(audio_format)
        audio_config = speechsdk.audio.AudioConfig(stream=self.audio_stream)

        # 음성 인식기 생성
        self.speech_recognizer = speechsdk.SpeechRecognizer(
            speech_config=speech_config,
            audio_config=audio_config
        )

        # 이벤트 핸들러 설정 
        def recognized_handler(evt):
            if evt.result.reason == speechsdk.ResultReason.RecognizedSpeech:    #stt 결과 받아오기 -> 처리 자체를 동기 방식으로 진행 (비동기 함수 사용x)
                text = evt.result.text.strip()
                if text:
                    print(f"🗣️ 원본: {text}\n")
                    asyncio.create_task(self.result_queue.put(text))    #동기 방식으로 반환된 stt 결과를 queue에 순서대로 저장

        def session_started_handler(evt):
            print("🎯 음성 인식 세션이 시작되었습니다.")
            
        def session_stopped_handler(evt):
            print("🛑 음성 인식 세션이 종료되었습니다.")
            self.is_listening = False
            
        def canceled_handler(evt):
            print(f"❌ 음성 인식이 취소되었습니다: {evt.result.cancellation_details.reason}")
            if evt.result.cancellation_details.reason == speechsdk.CancellationReason.Error:
                print(f"오류 세부사항: {evt.result.cancellation_details.error_details}")
            self.is_listening = False
        
        # 이벤트 연결
        self.speech_recognizer.recognized.connect(recognized_handler)                   # stt 결과가 나왔을 때,
        self.speech_recognizer.session_started.connect(session_started_handler)         # 세션이 시작되었을 때, 
        self.speech_recognizer.session_stopped.connect(session_stopped_handler)         # 세션이 종료되었을 때,
        self.speech_recognizer.canceled.connect(canceled_handler)                       # 인식이 취소되었을 떄,
    
    # [3] 음성 인식 
    def start_recognition(self):
        """연속 음성 인식 시작"""
        
        # 중복 인식 방지
        if self.is_listening:
            print("⚠️ 이미 음성 인식이 진행 중입니다.")
            return
        
        # 연속 인식 시작
        self.speech_recognizer.start_continuous_recognition()   ## Azure STT audio_stream 모니터링 시작 -> audio_data 추가되는 것 인식
        self.is_listening = True

    #[3-1] 실시간 음성 받아오기 : audio_stream에 데이터 추가 → Azure가 자동 감지 → STT 처리 → 콜백 호출
    def write_audio_chunk(self, audio_data: bytes):
        """
        오디오 청크를 스트림에 추가
        
        Args:
            audio_data: 오디오 바이트 데이터
        """
        if self.audio_stream and self.is_listening:
            self.audio_stream.write(audio_data)
    
    # [3-2] 음성 처리 결과 queue 비동기로 반환
    async def get_recognition_result(self):
        """STT 결과를 비동기로 반환"""
        return await self.result_queue.get()

    # [4] 실행 중지
    def stop_recognition(self):
        """연속 음성 인식 중지"""
        if self.speech_recognizer and self.is_listening:
            print("\n🛑 음성 인식을 중지합니다...")
            self.speech_recognizer.stop_recognition()
            self.is_listening = False
        else:
            print("⚠️ 진행 중인 음성 인식이 없습니다.")

        if self.audio_stream:
            self.audio_stream.close()
            self.audio_stream = None

        print("✅ 음성 인식 중지 완료")

    # [5] 음성 인식 언어 변경
    def change_setup_recognition(self, input_language) : 
        self.stop_recognition()                                     # 기존 인식 중지
        self.setup_streaming_recognition(input_language)  # 음성 인식 언어 변경
        self.start_recognition()                                    # 다시 시작

    def is_active(self) -> bool:
        """현재 인식이 활성화되어 있는지 확인"""
        return self.is_listening