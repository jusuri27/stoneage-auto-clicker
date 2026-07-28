import cv2
import numpy as np
import pyautogui
from PIL import Image

pyautogui.FAILSAFE = True  # 마우스를 화면 좌상단 모서리로 이동하면 즉시 중단


def find_template(screen: Image.Image, template_path: str, threshold: float = 0.8):
    screen_bgr = cv2.cvtColor(np.array(screen), cv2.COLOR_RGB2BGR)
    template = cv2.imread(template_path, cv2.IMREAD_COLOR)
    if template is None:
        raise FileNotFoundError(f"템플릿 이미지를 찾을 수 없습니다: {template_path}")

    result = cv2.matchTemplate(screen_bgr, template, cv2.TM_CCOEFF_NORMED)
    _, max_val, _, max_loc = cv2.minMaxLoc(result)

    if max_val < threshold:
        return None

    h, w = template.shape[:2]
    x, y = max_loc
    return {"x": x, "y": y, "width": w, "height": h, "confidence": max_val}


def click_match(match: dict):
    center_x = match["x"] + match["width"] // 2
    center_y = match["y"] + match["height"] // 2
    pyautogui.moveTo(center_x, center_y)
    pyautogui.click()


def check_and_click(screen: Image.Image, template_path: str, threshold: float = 0.8) -> bool:
    match = find_template(screen, template_path, threshold)
    if match is None:
        print(f"매칭 실패: {template_path}를 찾지 못했습니다.")
        return False

    print(f"매칭 성공 (confidence={match['confidence']:.4f})")
    click_match(match)
    return True


if __name__ == "__main__":
    from capture_screen import capture_full_screen

    screenshot_path = capture_full_screen()
    screenshot = Image.open(screenshot_path)

    check_and_click(screenshot, "idle_state.png")
