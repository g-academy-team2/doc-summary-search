import os
import logging
import olefile
import zlib
import subprocess
import uuid # 💡 임시 파일 생성을 위해 추가

# 💡 1. 새로운 비전 헬퍼 함수명과 절대 경로로 수정했습니다.
from app.ocr.parsers.vision_helper import extract_text_from_image

logger = logging.getLogger(__name__)

def extract_text_from_hwp(file_path):
    """한글(HWP) 파일 하이브리드 추출 (PrvText + hwp5txt + 이미지 OCR)"""
    full_text = []
    prv_text = ""

    # ---------------------------------------------------------
    # 단계 1: PrvText(미리보기) 추출 - 표지 및 요약 정보 확보
    # ---------------------------------------------------------
    try:
        with olefile.OleFileIO(file_path) as f:
            dirs = f.listdir()
            if ["PrvText"] in dirs:
                data = f.openstream("PrvText").read()
                prv_text = data.decode("utf-16", errors='ignore').strip()
                if prv_text:
                    full_text.append("=== [문서 요약 및 표지 정보] ===")
                    full_text.append(prv_text)
                    logger.info("✅ PrvText(표지 정보) 추출 성공")
    except Exception as e:
        logger.warning(f"⚠️ PrvText 추출 중 에러 발생 (무시하고 진행): {e}")

    # ---------------------------------------------------------
    # 단계 2: uv 환경에서 hwp5txt를 이용한 전체 본문 추출
    # ---------------------------------------------------------
    try:
        result = subprocess.run(
            ["uv", "run", "hwp5txt", file_path], 
            capture_output=True, 
            text=True,
            encoding="utf-8",
            errors="ignore",
            check=False
        )
        
        if result.returncode == 0 and result.stdout:
            body_content = result.stdout.strip()
            # PrvText와 내용이 너무 겹치지 않게 구분선을 넣어 추가
            full_text.append("\n=== [상세 본문 및 데이터] ===")
            full_text.append(body_content)
            logger.info("✅ hwp5txt로 전체 본문 추출 성공")
        else:
            logger.warning(f"⚠️ hwp5txt 추출 실패. 상세 원인: {result.stderr}")
            
    except Exception as e:
        logger.error(f"❌ 서브프로세스(hwp5txt) 실행 중 에러 발생: {e}")

    # ---------------------------------------------------------
    # 단계 3: BinData 이미지 OCR 추출
    # ---------------------------------------------------------
    try:
        with olefile.OleFileIO(file_path) as f:
            dirs = f.listdir()
            bin_data_list = [d for d in dirs if d[0] == "BinData"]
            image_count = 0
            
            for bin_dir in bin_data_list:
                try:
                    stream_name = "/".join(bin_dir)
                    img_data = f.openstream(stream_name).read()
                    if len(img_data) < 10240: continue # 너무 작은 이미지는 제외

                    try:
                        img_data = zlib.decompress(img_data, -15)
                    except:
                        pass 

                    image_count += 1
                    
                    # 💡 2. 바이트 데이터를 임시 이미지 파일로 저장합니다.
                    temp_img_path = f"temp_hwp_img_{uuid.uuid4().hex}.png"
                    with open(temp_img_path, "wb") as img_file:
                        img_file.write(img_data)
                        
                    # 💡 3. 실제 파일 경로를 넘겨서 비전 헬퍼에게 읽게 합니다.
                    vision_text = extract_text_from_image(temp_img_path)
                    
                    # 💡 4. 다 쓴 임시 파일은 즉시 삭제!
                    if os.path.exists(temp_img_path):
                        os.remove(temp_img_path)
                    
                    if vision_text:
                        full_text.append(f"\n[이미지 내 텍스트 분석 결과]:\n{vision_text}")
                except Exception as inner_e:
                    logger.warning(f"⚠️ 개별 이미지 처리 중 건너뜀: {inner_e}")
                    continue
                    
        logger.info(f"✅ 이미지 OCR 분석 완료 ({image_count}개)")
    except Exception as e:
        logger.error(f"❌ 이미지 추출 프로세스 에러: {e}")

    # 최종 결과 조합
    final_result = "\n\n".join(full_text)
    if not final_result.strip():
        return "⚠️ HWP 파일에서 유효한 텍스트를 추출할 수 없습니다."

    return final_result