import ollama
import json

def summarize_document(raw_text: str) -> dict:
    """
    Ollama 로컬 LLM을 사용해 문서를 요약하고, 
    DB의 enum 정의에 맞춰 [법률, 법안, 교육, IT] 중 하나로 분류합니다.
    """
    model_name = "gemma2"  # 사용 중이신 Ollama 모델명
    
    # DB enum에 정의된 정확한 한글 문자열 리스트
    VALID_ENUM_CATEGORIES = ["법률", "법안", "교육", "IT"]
    
    prompt = f"""
    당신은 문서 분석 전문가입니다. 주어진 문서 원문을 읽고 요약본을 작성한 뒤, 지정된 4가지 카테고리 중 가장 적절한 하나를 선택해주세요.
    반드시 아래의 JSON 포맷 형식을 엄격히 지켜서 응답해야 합니다. 다른 텍스트는 출력하지 마세요.
    
    [카테고리 선택 항목]:
    {", ".join(VALID_ENUM_CATEGORIES)}
    
    [문서 원문]:
    {raw_text}
    
    [출력 포맷]:
    {{
        "summary": "문서의 핵심 내용을 3줄 이내로 요약한 문장",
        "category": "위의 4가지 항목 중 정확히 일치하는 한 단어만 입력"
    }}
    """
    
    try:
        # Ollama API 호출
        response = ollama.chat(
            model=model_name,
            messages=[{"role": "user", "content": prompt}],
            options={"temperature": 0.0},  # 무작위성을 없애고 enum 매칭 확률을 극대화
            format="json"                  # 구조화된 JSON 출력 강제
        )
        
        # 결과 파싱
        result_text = response['message']['content']
        result_dict = json.loads(result_text)
        
        # ─── [데이터 가드레일 로직] ───
        # LLM이 출력한 카테고리 앞뒤 공백 제거
        category_output = result_dict.get("category", "").strip()
        
        # DB enum 값과 정확히 일치하는지 확인
        if category_output in VALID_ENUM_CATEGORIES:
            result_dict["category"] = category_output
        else:
            # 일치하지 않는 경우(예: 오타 등), 포함 관계 분석을 통해 보정
            corrected = False
            for valid_val in VALID_ENUM_CATEGORIES:
                if valid_val in category_output:
                    result_dict["category"] = valid_val
                    corrected = True
                    break
            
            # 보정마저 실패하면 DB 에러를 막기 위해 기본값(예: IT)으로 강제 고정
            if not corrected:
                print(f"[경고] LLM이 유효하지 않은 카테고리('{category_output}')를 반환하여 'IT'로 대체합니다.")
                result_dict["category"] = "IT"
                
        return result_dict
        
    except Exception as e:
        print(f"Ollama 호출 중 오류 발생: {e}")
        # 오류 발생 시에도 DB enum 제약조건을 깨뜨리지 않도록 안전한 기본값 반환
        return {"summary": "요약 처리 실패", "category": "IT"}