# [serivces/speech_service.py]
# speech_translation 작업 로직 처리 
from src.app.interfaces.speech_translation_interface import SpeechTranslationInterface
from src.app.dto.speech_translation_dto import ConfigMessage, SpeechTranslationResponse, StatusMessage
from fastapi import WebSocket, WebSocketDisconnect
import json, traceback, asyncio

# [1] WebSocket 연결 -> speech_translation 처리
async def websocket_translation_service(websocket : WebSocket):
    interface = None
    try:
        # 인터페이스 호출 (init)
        print("SpeechTranslationInterface 생성 시도...")
        interface = SpeechTranslationInterface()
        print("SpeechTranslationInterface 생성 성공")

        # 1. WebSocket 연결
        await websocket.accept()
        print("클라이언트 연결됨")

        # 2. speech_translation 설정
        # 2-1. 초기 설정 request 받아오기
        print("설정 메시지 수신 대기")
        config_msg = await websocket.receive_json()
        print("설정 메시지 수신 완료")
        config = ConfigMessage(**config_msg)   
        
        # 2-2. 설정에 맞춰 session 열기
        try:
            await interface.start_session(config.input_language, config.target_languages)
        except Exception as e:
            error_status = StatusMessage(
                status="error", 
                message="STT 초기화 실패", 
                error_code="STT_INIT_FAILED"
            )
            await websocket.send_json(error_status.model_dump())        # error 메시지 전송 
            return
        # 2-3. speech_translation 준비 완료 response 전송
        status = StatusMessage(status="ready", message="speech_translation 준비 완료")
        await websocket.send_json(status.model_dump())

         # 3. 개선된 실시간 처리 - 백그라운드에서 번역 결과 전송
        result_sender_task = asyncio.create_task(
            send_translation_results(websocket, interface)
        )

        # 4. 오디오 스트림 수신 - 논블로킹
        await process_audio_stream(websocket, interface)

        # 3. 실시간 처리
        # await audio_handler(websocket, interface)        # 음성 스트림 수신 -> 결과 송신

    except WebSocketDisconnect:
        disconnect_status = StatusMessage(
            status="disconnected",
            message="클라이언트가 연결을 종료했습니다",
            error_code="CLIENT_DISCONNECT"
        )
        print(f"클라이언트 연결 종료 : {disconnect_status}")
    except Exception as e:
        print(f"❌ 정확한 오류: {e}") 
        traceback.print_exc()  # 전체 스택 트레이스 출력
        error_status = StatusMessage(
            status="disconnected", 
            message=f"네트워크 오류로 연결 종료: {str(e)}",
            error_code="NETWORK_ERROR"
        )
        try:
            await websocket.send_json(error_status.model_dump())        # disconnected 메시지 전송
        except:
            print("연결 종료로 에러 메시지 전송 실패")
    finally:
        if interface is not None:
            interface.stop_session()
        print("세션 종료 완료")
            
# [2] 오디오 스트림 처리 - 논블로킹 방식
async def process_audio_stream(websocket: WebSocket, interface):
    """오디오 스트림을 논블로킹 방식으로 처리"""
    while True:
        try:
            # 메시지 수신
            message_type = await websocket.receive()
            
            # JSON 메시지 처리 (설정 변경)
            if message_type.get("type") == "websocket.receive" and "text" in message_type:
                message_text = message_type["text"]
                config_data = json.loads(message_text)
                
                if config_data["type"] == "setting":
                    print(f"설정 변경 요청: {config_data}")
                    # 설정 변경 처리 (기존과 동일)
                    
            # 오디오 데이터 처리
            elif message_type.get("type") == "websocket.receive" and "bytes" in message_type:
                if not interface.is_active:
                    continue
                
                audio_data = message_type["bytes"]
                print(f"오디오 수신: {len(audio_data)} bytes")
                
                # 타임아웃 없이 오디오 처리
                interface.process_audio_chunk(audio_data)
                
        except Exception as e:
            print(f"오디오 스트림 처리 오류: {e}")
            break

# [3] 번역 결과 전송 - 백그라운드 태스크
async def send_translation_results(websocket: WebSocket, interface):
    """백그라운드에서 번역 결과를 지속적으로 전송"""
    print("번역 결과 전송 태스크 시작")
    
    while True:
        try:
            # 논블로킹으로 결과 확인
            result = await interface.get_latest_translation_result()
            
            if result:
                print(f"번역 결과 받음: {list(result.keys())}")
                response = SpeechTranslationResponse(translations=result)
                await websocket.send_json(response.model_dump())
                print("클라이언트에 번역 결과 전송 완료")
            else:
                # 결과가 없으면 잠깐 대기
                await asyncio.sleep(0.1)
                
        except Exception as e:
            print(f"번역 결과 전송 오류: {e}")
            break


# [2] 음성 스트림 or JSON 통신 : 1. audio stream(음성 번역 실행) 2. json(설정 변경)
# async def audio_handler(websocket, interface):
#     while True:
#         try:
#             message = await websocket.receive()

#             # JOSN 형식을 수신받았을 경우,
#             if message.get("type") == "websocket.receive" and "text" in message:
#                 print(f"메시지 타입 수신: text")
#                 message_text = message["text"]
#                 config_data = json.loads(message_text)

#                 if config_data["type"] == "setting":
#                     # 설정 변경
#                     config = ConfigMessage(**config_data)
#                     try : 
#                         # 입력 언어 설정 변경
#                         if interface.current_input_language != config.input_language : 
#                             await interface.change_input_language_settings(config.input_language)
#                         # 번역 언어 설정 변경
#                         if interface.current_target_languages != config.target_languages : 
#                             await interface.change_target_languages_settings(config.target_languages)
#                     except Exception as e:
#                         error_status = StatusMessage(
#                             status="error",
#                             message=f"언어 변경 실패: {str(e)}",
#                             error_code="LANGUAGE_CHANGE_FAILED" 
#                         )
#                         await websocket.send_json(error_status.model_dump())        # error 메시지 전송
#             # binary 형식을 수신받았을 경우, (오디오)
#             elif message.get("type") == "websocket.receive" and "bytes" in message:
#                 print(f"메시지 타입 수신: bytes")
#                 # ready가 안됐는데 음성을 전송받았다면 -> 경고 메시지 전송
#                 if not interface.is_active:
#                     warning = StatusMessage(
#                         status="warning",
#                         message="아직 준비되지 않았습니다. 설정 완료를 기다려주세요"
#                     )
#                     await websocket.send_json(warning.model_dump())
#                     continue    # 오디오 처리 x 후 다시 음성 들어오기를 기다림...
#                 # 음성 스트림 수신
#                 audio_data = await websocket.receive_bytes()
#                 print(f"오디오 수신 길이: {len(audio_data)} bytes")
#                 # speech_translation 작업 시작
#                 result = await interface.process_audio_with_translation(
#                     audio_data, interface.current_target_languages, timeout=0.1
#                 )
#                 if result:
#                     print(f"번역 결과: {result}")
#                     response = SpeechTranslationResponse(translations=result)
#                     await websocket.send_json(response.model_dump())
#         except Exception as e:
#             print(f"❌ audio_handler 오류: {e}")
#             break