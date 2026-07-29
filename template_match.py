import time

import cv2
import numpy as np
import pyautogui
import pygetwindow as gw
from PIL import Image

pyautogui.FAILSAFE = True  # 마우스를 화면 좌상단 모서리로 이동하면 즉시 중단

def find_all_templates(screen: Image.Image, template_path: str, threshold: float = 0.8):
    screen_bgr = cv2.cvtColor(np.array(screen), cv2.COLOR_RGB2BGR)
    template = cv2.imread(template_path, cv2.IMREAD_COLOR)
    if template is None:
        raise FileNotFoundError(f"템플릿 이미지를 찾을 수 없습니다: {template_path}")

    h, w = template.shape[:2]
    result = cv2.matchTemplate(screen_bgr, template, cv2.TM_CCOEFF_NORMED)
    ys, xs = np.where(result >= threshold)
    candidates = sorted(
        ((x, y, result[y, x]) for x, y in zip(xs, ys)),
        key=lambda c: c[2],
        reverse=True,
    )

    matches = []
    for x, y, conf in candidates:
        # 같은 아이콘 주변의 중복 검출 제거 (템플릿 크기보다 가까우면 같은 매칭으로 간주)
        if any(abs(x - m["x"]) < w and abs(y - m["y"]) < h for m in matches):
            continue
        matches.append({"x": x, "y": y, "width": w, "height": h, "confidence": conf})

    return matches


def click_match(match: dict):
    center_x = match["x"] + match["width"] // 2
    center_y = match["y"] + match["height"]  # 세로는 매칭 영역의 최하단을 클릭
    pyautogui.moveTo(center_x, center_y)
    pyautogui.click() # 대기 상태 아이콘 클릭 
    time.sleep(1)
    pyautogui.click() # 팝업 화면(아이콘 클릭시) 닫기 위해서 다시 클릭


def check_and_click(screen: Image.Image, template_path: str, threshold: float = 0.8) -> int:
    matches = find_all_templates(screen, template_path, threshold)
    if not matches:
        print(f"매칭 실패: {template_path}를 찾지 못했습니다.")
        return 0

    print(f"매칭 성공: {len(matches)}개")
    for i, match in enumerate(matches, 1):
        print(f"  [{i}] confidence={match['confidence']:.4f} at ({match['x']}, {match['y']})")
        click_match(match)
        time.sleep(2)  # 클릭 사이 최소 간격

    return len(matches)


if __name__ == "__main__":
    from capture_screen import capture_full_screen

    screenshot_path = capture_full_screen()
    screenshot = Image.open(screenshot_path)

    check_and_click(screenshot, "assets/idle_state.png")
