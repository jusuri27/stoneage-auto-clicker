import os
from datetime import datetime
import pyautogui

OUTPUT_DIR = "debug_output"


def capture_full_screen() -> str:
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    filename = datetime.now().strftime("%Y%m%d_%H%M%S") + ".png"
    filepath = os.path.join(OUTPUT_DIR, filename)

    try:
        screenshot = pyautogui.screenshot()
        screenshot.save(filepath)
    except Exception as e:
        # 화면 캡처 실패 시 스케줄러가 죽지 않도록 원인을 명확히 알려주고 상위로 전파
        raise RuntimeError(f"화면 캡처 실패: {e}") from e

    return filepath


if __name__ == "__main__":
    saved_path = capture_full_screen()
    print(f"저장 완료: {saved_path}")
