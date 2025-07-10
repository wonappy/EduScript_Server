# [dto/speech_translation_dto.py] 
# 발화 정제 요청 & 응답 클래스 
from pydantic import BaseModel
from typing import Dict, Optional

# [1]-1 단일 인식 언어 설정 메시지 (Request)
class ConfigMessage(BaseModel):
    type: str = "setting" 
    input_language: str                    # 음성 인식 언어
    target_languages: list[str]            # 번역 출력 언어

# [1]-2 다중 인식 언어 설정 메시지 (Request)
class MultipleConfigMessage(BaseModel):
    type: str = "setting" 
    input_languages: list[str]                    # 음성 인식 언어
    target_languages: list[str]            # 번역 출력 언어

# [2] 번역 결과 반환 (Response)
class TranslationResult(BaseModel):
    target_lang: str
    result_text: str
class SpeechTranslationResponse(BaseModel):
    type: str = "result"
    is_final: bool
    translations: Dict[str, TranslationResult]

# [2]-2 원문 지정 번역 결과 반환 (Response) 
class SeparatedSpeechTranslationResponse(BaseModel):
    type: str = "result"
    is_final: bool
    original: Dict[str, TranslationResult]
    translations: Dict[str, TranslationResult]

# 상태 반환 (Response)
class StatusMessage(BaseModel):
    type: str = "status"
    status: str                           # "ready", "error", "disconnected"
    message: Optional[str] = None         # nullable str형 : msg
    error_code: Optional[str] = None      # nullable str형 : error 코드