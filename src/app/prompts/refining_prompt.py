# [prompts/refining_prompt.py]
# 발화 정제용 프롬프트

from src.app.prompts.language_name_map import LANGUAGE_NAME_MAP

def refine_lecture_prompt(language: str) -> str:
    language = LANGUAGE_NAME_MAP.get(language, language)
    
    prompt = f"""
다음 발화 내용은 대학 강의에서 교수님이 실제로 말씀하신 내용을 STT(음성 인식)를 통해 텍스트로 변환한 {language} 텍스트입니다.

이 발화 내용을 다음 유의사항에 맞추어 **자연스럽게 정제**하되, 반드시 **출력 언어도 {language}로 유지**해주세요. 번역하지 마세요.

[유의사항]
- 교수님의 실제 발화를 바탕으로 하되, STT 오류로 인해 어색하거나 왜곡된 표현은 자연스럽게 수정합니다.
- 오탈자 및 잘못된 띄어쓰기를 수정합니다.
- 문맥상 의미가 어긋나는 경우, 교수님의 의도에 맞게 자연스럽게 고쳐줍니다.
- ‘어’, ‘음’, ‘아’ 등 의미 없는 추임새는 제거합니다.
- 교수님의 어투(높임말 포함)는 최대한 유지하며, 하지 않은 말을 지어내서는 안 됩니다.
- 반복된 말은 문맥에 따라 간결하게 정리하되, 중요한 강조는 유지합니다.

[출력 형식]
- 첫 줄에 "주제: [강의 주제]" 형식으로 내용의 핵심 주제를 명시해주세요.
- 그 다음 줄부터 정제된 발화 내용을 작성해주세요.
- 출력은 반드시 **{language}로만** 작성해주세요. **다른 언어로 번역하지 마세요.**
"""
    return prompt

def refine_meeting_prompt(language:str) -> str:
    language = LANGUAGE_NAME_MAP.get(language, language)

    """회의 정제용 프롬프트"""
    prompt = f"""
다음 발화 내용은 회의 중 {language}를 사용하는 참석자가 말한 내용을 STT로 변환한 텍스트입니다.

이 내용을 다음 기준에 따라 **자연스럽게 정제**하되, 반드시 **출력도 {language}로 유지**해주세요. 번역하지 마세요.

[유의사항]
- 오탈자 수정
- 의미없는 추임새('어', '아' 등) 제거
- 회의 참석자들의 발언 내용은 최대한 유지
- 자연스러운 문어체로 정제
- 이전 텍스트와 다음 텍스트의 언어가 다른 경우 한 줄 띄어 출력
  (예시: 안녕하세요, 오늘 주제는 먹거리에요.  
   oh, that's interesting)
- 출력은 반드시 **{language}로만** 작성해주세요. **다른 언어로 번역하지 마세요.**
"""
    return prompt