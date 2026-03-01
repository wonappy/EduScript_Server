# [config.py] 
# .env에서 API Key 호출
# from pydantic_settings import BaseSettings, SettingsConfigDict

# class APISettings(BaseSettings):
#     model_config = SettingsConfigDict(env_file = ".env")
#     google_cloud_key: str
#     azure_stt_key: str
#     azure_translation_key: str
#     deepl_translation_key: str
#     openai_llm_key: str

# api_settings = APISettings()

import os
from dotenv import load_dotenv

# .env 파일 로드
load_dotenv()

class APISettings:
    def __init__(self):
        self.google_cloud_key = os.getenv("GOOGLE_CLOUD_KEY")
        self.azure_stt_key = os.getenv("AZURE_STT_KEY") 
        self.azure_translation_key = os.getenv("AZURE_TRANSLATION_KEY")
        self.deepl_translation_key = os.getenv("DEEPL_TRANSLATION_KEY")
        self.openai_llm_key = os.getenv("OPENAI_LLM_KEY")

api_settings = APISettings()