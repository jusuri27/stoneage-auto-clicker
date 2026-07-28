import os
from datetime import datetime
import pyautogui

OUTPUT_DIR = "debug_output"


def capture_full_screen() -> str:
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    filename = datetime.now().strftime("%Y%m%d_%H%M%S") + ".png"
    filepath = os.path.join(OUTPUT_DIR, filename)

    screenshot = pyautogui.screenshot()
    screenshot.save(filepath)
    return filepath


if __name__ == "__main__":
    saved_path = capture_full_screen()
    print(f"저장 완료: {saved_path}")
