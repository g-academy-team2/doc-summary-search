import pdfplumber
import os
import re  # 정규표현식 도구 추가!

# === [새로 추가된 데이터 세탁기(전처리) 함수] ===
def clean_text(raw_text):
    text = raw_text
    
    # 1. 깨진 한글 수동 복원 (자주 깨지는 글자들)
    broken_words = {'핚': '한', '핛': '할', '갂': '간', '싞': '신', '모듞': '모든', '젂': '전'}
    for broken, fixed in broken_words.items():
        text = text.replace(broken, fixed)
        
    # 2. 불필요한 기호 및 페이지 번호 제거 (-1-, -2- 등)
    text = text.replace("", "")
    text = re.sub(r'-\s*\d+\s*-', '', text) # 페이지 번호 패턴 삭제
    
    # 3. 중간에 뚝 끊긴 줄바꿈 이어 붙이기 
    # (엔터가 한 번만 쳐진 곳은 띄어쓰기로 바꾸고, 두 번 쳐진 문단 구분은 유지)
    text = re.sub(r'(?<!\n)\n(?!\n)', ' ', text)
    
    # 4. 쓸데없이 넓은 띄어쓰기(공백)를 하나로 압축
    text = re.sub(r' +', ' ', text)
    
    return text.strip()
# =================================================

def extract_text_from_pdf(file_path):
    print(f"🔍 [{file_path}] 파일 분석을 시작합니다...")
    full_text = ""
    
    if not os.path.exists(file_path):
        return "❌ 파일을 찾을 수 없습니다."

    try:
        with pdfplumber.open(file_path) as pdf:
            print(f"📄 총 {len(pdf.pages)}페이지를 발견했습니다.\n")
            for i, page in enumerate(pdf.pages):
                text = page.extract_text() 
                if text:
                    full_text += text + "\n\n" # 문단 구분을 위해 엔터 두 번
                print(f"  ✔️ {i+1}페이지 추출 완료")
                
        print("\n✨ 파싱 완료! 텍스트 전처리를 시작합니다...")
        
        # 여기서 방금 만든 세탁기 함수를 통과시킵니다!
        cleaned_text = clean_text(full_text) 
        
        return cleaned_text

    except Exception as e:
        return f"❌ 오류가 발생했습니다: {e}"

if __name__ == "__main__":
    target_pdf = "sample.pdf" 
    result = extract_text_from_pdf(target_pdf)
    
    print("\n=== [전처리 완료된 텍스트 (앞부분 500자)] ===")
    print(result[:500])
    print("\n=============================================")