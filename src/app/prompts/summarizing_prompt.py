# [prompts/summarizing_prompt.py]
# 발화 요약용 프롬프트

from src.app.prompts.language_name_map import LANGUAGE_NAME_MAP

def summarize_lecture_prompt(language: str) -> str:
    language = LANGUAGE_NAME_MAP.get(language, language)
    
    prompt = f"""
당신은 대학 강의 요약 도우미입니다. 지금부터 전달하는 텍스트는 강의 발화 내용입니다.

 **다음의 조건을 반드시 지켜주세요**:
1. 모든 출력은 반드시 **{language}**로 작성해야 합니다.
2. 줄글 형식으로 요약해주세요.
3. 이모티콘 사용 금지.
4. 수업 내용과 관련 없는 잡담은 제외해주세요.
5. 공지사항, 일정, 과제 제출 기한 등은 요약에서 제외해주세요.

이제 아래의 강의 내용을 요약해주세요.
"""
    return prompt

def summarize_meeting_prompt(language: str) -> str:
    # 언어 이름 매핑 (예: "en" → "영어")
    language_name = LANGUAGE_NAME_MAP.get(language, language)

    # 출력 레이블 다국어 대응
    label_map = {
        "ko": {
            "minutes": "회의록",
            "date": "일시",
            "topic": "주제",
            "agenda": "안건",
            "conclusion": "결론",
            "final_conclusion": "최종 결론",
        },
        "en": {
            "minutes": "Minutes",
            "date": "Date",
            "topic": "Topic",
            "agenda": "Agenda",
            "conclusion": "Conclusion",
            "final_conclusion": "Final Conclusion",
        },
        "ja": {
            "minutes": "議事録",
            "date": "日付",
            "topic": "議題",
            "agenda": "アジェンダ",
            "conclusion": "結論",
            "final_conclusion": "最終結論",
        },
    }

    labels = label_map.get(language, label_map["ko"])  # 기본은 한국어

    prompt = f"""
당신은 회의 내용을 정리하는 비서입니다. 아래는 회의 녹취록 텍스트입니다.

**요약 조건**:
1. 모든 출력은 반드시 **{language_name}**로 작성해주세요. (아래의 출력 형식 포함)
2. 발언자의 이름은 생략하고 내용만 정리합니다.
3. 각 안건의 핵심 내용을 요약하고, 마지막에 전체 결론을 작성합니다.
4. 특수문자, 이모지, 마크다운 문법 금지. 일반 텍스트만 사용합니다.

출력 형식:

{labels["minutes"]}: (회의 제목)
{labels["date"]}: (회의 날짜)
{labels["topic"]}: (전체 주제)

{labels["agenda"]} 1: (소주제 제목)
- 논의 내용 요약
- 논의 내용 요약
- 논의 내용 요약
{labels["conclusion"]}: (해당 안건의 결론 요약)

...

{labels["final_conclusion"]}: (전체 회의 내용을 종합한 결론)

이제 아래 회의 텍스트를 위 형식에 따라 요약해주세요.
"""
    return prompt
