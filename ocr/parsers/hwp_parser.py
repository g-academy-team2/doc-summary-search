import logging
import olefile
import zlib
from .vision_helper import get_text_from_image_bytes

logger = logging.getLogger(__name__)

def extract_text_from_hwp(file_path):
    """한글(HWP) 파일 본문 및 포함된 이미지 텍스트 추출"""
    try:
        f = olefile.OleFileIO(file_path)
        full_text = []

        # 1. 본문 텍스트 추출 (PrvText 사용)
        dirs = f.listdir()
        if ["PrvText"] in dirs:
            try:
                data = f.openstream("PrvText").read()
                # utf-16 디코딩 시 발생할 수 있는 작은 에러들을 무시하여 안전하게 읽음
                text_content = data.decode("utf-16", errors='ignore')
                if text_content.strip():
                    full_text.append(text_content)
            except Exception as e:
                logger.warning(f"⚠️ PrvText 디코딩 중 에러 발생: {e}")

        # 2. 이미지 추출 및 OpenAI Vision OCR
        bin_data_list = [d for d in dirs if d[0] == "BinData"]
        
        image_count = 0
        for bin_dir in bin_data_list:
            try:
                stream_name = "/".join(bin_dir)
                img_data = f.openstream(stream_name).read()
                
                # [비용 절감 핵심] 너무 작은 파일(예: 10KB 미만)은 아이콘일 확률이 높으므로 제외
                if len(img_data) < 10240: 
                    continue

                # zlib 압축 해제 시도
                try:
                    img_data = zlib.decompress(img_data, -15)
                except:
                    pass 

                image_count += 1
                logger.info(f"📸 {file_path} 내 {image_count}번째 주요 이미지 분석 중... ({len(img_data)} bytes)")
                
                vision_text = get_text_from_image_bytes(img_data)
                if vision_text:
                    full_text.append(f"\n[한글 문서 내 이미지 OCR 결과]:\n{vision_text}")
            except Exception as img_err:
                logger.warning(f"⚠️ HWP 이미지 추출 중 건너뜀: {img_err}")

        # 최종 결과 확인
        result = "\n\n".join(full_text)
        if not result.strip():
            return "⚠️ HWP 파일 본문을 읽을 수 없습니다. (미리보기 텍스트가 없는 파일일 수 있습니다.)"

        logger.info(f"✅ HWP 분석 완료 (텍스트 + 주요 이미지 {image_count}개)")
        return result

    except Exception as e:
        logger.error(f"❌ HWP 파싱 전체 에러: {e}")
        return f"HWP 읽기 실패: {str(e)}"