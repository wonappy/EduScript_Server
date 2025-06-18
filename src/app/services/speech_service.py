# [serivces/speech_service.py]
# speech_translation 작업 로직 처리 
from interfaces.speech_translation_interface import SpeechTranslationInterface
from dto.speech_translation_dto import ConfigMessage, SpeechTranslationResponse, StatusMessage
from fastapi import WebSocket, WebSocketDisconnect
import json

# [1] WebSocket 연결 -> speech_translation 처리
async def websocket_translation_service(websocket : WebSocket):
    try:
        # 인터페이스 호출 (init)
        interface = SpeechTranslationInterface()

        # 1. WebSocket 연결
        await websocket.accept()
        print("클라이언트 연결됨")

        # 2. speech_translation 설정
        # 2-1. 초기 설정 request 받아오기
        config_msg = await websocket.receive_json()
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

        # 3. 실시간 처리
        await audio_handler(websocket, interface)        # 음성 스트림 수신 -> 결과 송신

    except WebSocketDisconnect:
        disconnect_status = StatusMessage(
            status="disconnected",
            message="클라이언트가 연결을 종료했습니다",
            error_code="CLIENT_DISCONNECT"
        )
        print(f"클라이언트 연결 종료 : {disconnect_status}")
    except Exception as e:
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
        interface.stop_session()
        print("세션 종료 완료")


# [2] 음성 스트림 or JSON 통신 : 1. audio stream(음성 번역 실행) 2. json(설정 변경)
async def audio_handler(websocket, interface):
    while True:
        try:
            # JOSN 형식을 수신받았을 경우,
            message = await websocket.receive_text()
            config_data = json.loads(message)
            
            if config_data["type"] == "setting":
                # 설정 변경
                config = ConfigMessage(**config_data)
                try : 
                    # 입력 언어 설정 변경
                    if interface.current_input_language != config.input_language : 
                        await interface.change_input_language_settings(config.input_language)
                    # 번역 언어 설정 변경
                    if interface.current_target_languages != config.target_languages : 
                        await interface.change_target_languages_settings(config.target_languages)
                except Exception as e:
                    error_status = StatusMessage(
                        status="error",
                        message=f"언어 변경 실패: {str(e)}",
                        error_code="LANGUAGE_CHANGE_FAILED" 
                    )
                    await websocket.send_json(error_status.model_dump())        # error 메시지 전송
        except json.JSONDecodeError:
            # ready가 안됐는데 음성을 전송받았다면 -> 경고 메시지 전송
            if not interface.is_active:
                warning = StatusMessage(
                    status="warning",
                    message="아직 준비되지 않았습니다. 설정 완료를 기다려주세요"
                )
                await websocket.send_json(warning.model_dump())
                continue    # 오디오 처리 x 후 다시 음성 들어오기를 기다림...
            # 음성 스트림 수신
            audio_data = await websocket.receive_bytes()
            print(f"오디오 수신 길이: {len(audio_data)} bytes")
            # speech_translation 작업 시작
            result = await interface.process_audio_with_translation(
                audio_data, interface.current_target_languages, timeout=3.0
            )
            if result:
                print(f"번역 결과: {result}")
                response = SpeechTranslationResponse(translations=result)
                await websocket.send_json(response.model_dump())
            