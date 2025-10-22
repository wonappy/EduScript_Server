#[modules/llm/openai_llm.py]
# LLM API Key 호출 
import openai
from openai import AsyncOpenAI
from src.app.core.config import api_settings

class OpenAILLM:
    # [1] 초기화 - OpenAI API 키 호출 
    def __init__(self):
        self.client = AsyncOpenAI(
            api_key=api_settings.openai_llm_key
        )

    # [2] LLM 모델 호출 - 텍스트 생성 및 반환
    async def select_gpt_model(self, messages: list, temperature: float = 0.3) -> str:
        try:
            response = await self.client.chat.completions.create(
                model="gpt-4o-mini", # Chat GPT 모델 
                messages=messages,
                temperature=temperature
            )
            return response.choices[0].message.content # choices[0] : content만 반환
        
        except openai.AuthenticationError as e:
            raise Exception(f"[MODULE ERROR] API 키 인증 실패 - {str(e)}")
        except openai.RateLimitError as e:
            raise Exception(f"[MODULE ERROR] API 호출 제한 초과 - {str(e)}")
        except openai.APIConnectionError as e:
            raise Exception(f"[MODULE ERROR] API 연결 실패 - {str(e)}") # 네트워크 연결 문제
        except openai.BadRequestError as e:
            raise Exception(f"[MODULE ERROR] 잘못된 요청 - {str(e)}") # 빈 메시지 or 잘못된 파라미터
        except Exception as e:
            raise Exception(f"[MODULE ERROR] OpenAI API 호출 실패 - {str(e)}")
        