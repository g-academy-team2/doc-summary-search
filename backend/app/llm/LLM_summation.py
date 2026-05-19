import ollama
import json

def summarize_document(raw_text: str) -> dict:
    """
    Ollama 로컬 LLM을 사용해 문서를 요약하고, 
    DB의 enum 정의에 맞춰 [법률, 법안, 교육, IT, 기타] 중 하나로 분류합니다.
    """
    model_name = "gemma2" 
    
    # DB enum에 정의된 유효 카테고리 리스트 (백엔드 추가 예정인 '기타' 포함)
    VALID_ENUM_CATEGORIES = ["법률", "법안", "교육", "IT", "기타"]
    
    prompt = f"""
    # 역할
    - 당신은 문서 분석 전문가입니다. 
    
    # 규칙
    - 주어진 문서의 요약을 출력 할 것.
    - 문서 요약 내용은 주어진 문서에 존재하지 않는 내용을 포함할 수 없습니다.
    - {VALID_ENUM_CATEGORIES} 중 가장 적절한 하나를 선택하여 출력 할 것.
    - 만약 적절한 카테고리가 없거나 모호하다면 '기타'를 선택하십시오.
    - 출력 포맷은 다음과 같으며, 해당 형식을 엄격히 지켜 출력해야 합니다.
    
    [카테고리 선택 항목]:
    {", ".join(VALID_ENUM_CATEGORIES)}
    
    [문서 원문]:
    {raw_text}
    
    [출력 포맷]:
    {{
        "summary": "문서의 핵심 내용을 3줄 이내로 요약한 문장",
        "category": "위의 5가지 항목 중 정확히 일치하는 한 단어만 입력"
    }}
    """
    
    try:
        response = ollama.chat(
            model=model_name,
            messages=[{"role": "user", "content": prompt}],
            options={"temperature": 0.0},
            format="json"
        )
        
        result_text = response['message']['content']
        result_dict = json.loads(result_text)
        
        # ─── [데이터 가드레일 로직] ───
        category_output = result_dict.get("category", "").strip()
        
        # 1. 정확히 일치하는 경우
        if category_output in VALID_ENUM_CATEGORIES:
            result_dict["category"] = category_output
        else:
            # 2. 포함 관계 분석 (중복 매칭 문제 해결)
            matched_categories = [val for val in VALID_ENUM_CATEGORIES if val in category_output]
            
            if len(matched_categories) == 1:
                # 하나만 매칭되면 해당 값 사용
                result_dict["category"] = matched_categories[0]
            elif len(matched_categories) > 1:
                # 'IT/교육'처럼 여러 개가 걸릴 경우, LLM에게 '기타' 권한을 주거나 
                # 여기서는 '기타'로 분류하여 데이터 무결성을 유지합니다.
                result_dict["category"] = "기타"
            else:
                # 71번째 줄: 보정 실패 시 '기타'로 대체
                print(f"[경고] 유효하지 않은 카테고리('{category_output}') -> '기타'로 대체")
                result_dict["category"] = "기타"
                
        return result_dict
        
    except Exception as e:
        # 78번째 줄: 에러 발생 시 '기타'로 반환
        print(f"Ollama 호출 중 오류 발생: {e}")
        return {"summary": "요약 처리 실패", "category": "기타"}