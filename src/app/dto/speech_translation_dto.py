# [dto/speech_translation_dto.py] 
# 발화 정제 요청 & 응답 클래스 
from pydantic import BaseModel
from typing import Dict, Optional

# [1] 언어 설정 메시지 (Request)
class ConfigMessage(BaseModel):
    type: str = "setting" 
    input_language: str                    # 음성 인식 언어
    target_languages: list[str]            # 번역 출력 언어

# [2] 오디오 전송 메시지 (Request) - 음성 데이터는 binary 형식으로 전송
class AudioMessage(BaseModel):
    type: str = "audio"
    target_languages: list[str]             # 번역 언어
    # audio_data는 실제로는 bytes로 별도 전송

# [3] 번역 결과 반환 (Response)
class TranslationResult(BaseModel):
    target_lang: str
    result_text: str
class SpeechTranslationResponse(BaseModel):
    type: str = "result"
    translations: Dict[str, TranslationResult]

# 상태 반환 (Response)
class StatusMessage(BaseModel):
    type: str = "status"
    status: str                           # "ready", "error", "disconnected"
    message: Optional[str] = None         # nullable str형 : msg
    error_code: Optional[str] = None      # nullable str형 : error 코드