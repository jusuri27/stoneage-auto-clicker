import os
from datetime import datetime
import pyautogui
from PIL import Image

from log_utils import log

OUTPUT_DIR = "match_success_log"


def capture_full_screen() -> Image.Image:
    try:
        return pyautogui.screenshot()
    except Exception as e:
        # 화면 캡처 실패 시 스케줄러가 죽지 않도록 원인을 명확히 알려주고 상위로 전파
        raise RuntimeError(f"화면 캡처 실패: {e}") from e


def save_screenshot(screenshot: Image.Image) -> str:
    # 매칭 성공 로그용으로만 호출되므로 폴더명(match_success_log)과 의미를 맞춤
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    filename = datetime.now().strftime("%Y%m%d_%H%M%S") + ".png"
    filepath = os.path.join(OUTPUT_DIR, filename)
    screenshot.save(filepath)
    return filepath


if __name__ == "__main__":
    screenshot = capture_full_screen()
    saved_path = save_screenshot(screenshot)
    log(f"저장 완료: {saved_path}")
