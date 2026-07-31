import time

import cv2
import numpy as np
import pyautogui
import pygetwindow as gw
from PIL import Image

from log_utils import log

pyautogui.FAILSAFE = True  # 마우스를 화면 좌상단 모서리로 이동하면 즉시 중단

def find_all_templates(screen: Image.Image, template_paths, threshold: float = 0.8):
    # 초급/중급/고급처럼 여러 템플릿을 한 번에 검사할 수 있도록 문자열 하나도 리스트로 통일
    if isinstance(template_paths, str):
        template_paths = [template_paths]

    screen_bgr = cv2.cvtColor(np.array(screen), cv2.COLOR_RGB2BGR)

    matches = []
    for template_path in template_paths:
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

        for x, y, conf in candidates:
            # 같은 아이콘 주변의 중복 검출 제거 (템플릿 크기보다 가까우면 같은 매칭으로 간주)
            # 다른 템플릿과의 매칭 결과도 함께 비교해 동일 위치가 중복 처리되지 않도록 함
            if any(abs(x - m["x"]) < w and abs(y - m["y"]) < h for m in matches):
                continue
            matches.append({
                "x": x, "y": y, "width": w, "height": h,
                "confidence": conf, "template": template_path,
            })

    # 서로 다른 템플릿에서 나온 매칭을 confidence 기준으로 다시 정렬
    matches.sort(key=lambda m: m["confidence"], reverse=True)
    return matches


def click_match(match: dict):
    center_x = match["x"] + match["width"] // 2
    center_y = match["y"] + match["height"]  # 세로는 매칭 영역의 최하단을 클릭
    pyautogui.moveTo(center_x, center_y)
    pyautogui.click() # 대기 상태 아이콘 클릭
    time.sleep(1)
    pyautogui.click() # 팝업 화면(아이콘 클릭시) 닫기 위해서 다시 클릭


def click_center(match: dict):
    center_x = match["x"] + match["width"] // 2
    center_y = match["y"] + match["height"] // 2
    pyautogui.moveTo(center_x, center_y)
    pyautogui.click()


def check_and_click(screen: Image.Image, template_paths, threshold: float = 0.8) -> int:
    matches = find_all_templates(screen, template_paths, threshold)
    if not matches:
        log(f"매칭 실패: {template_paths}를 찾지 못했습니다.")
        return 0

    log(f"매칭 성공: {len(matches)}개")
    for i, match in enumerate(matches, 1):
        log(f"  [{i}] template={match['template']} confidence={match['confidence']:.4f} at ({match['x']}, {match['y']})")
        click_match(match)
        time.sleep(2)  # 클릭 사이 최소 간격

    return len(matches)


def run_balloon_popup_flow(
    icon_template_path: str,
    confirm_template_path: str,
    threshold: float = 0.8,
    max_iterations: int = 20,
) -> int:
    # 풍선 아이콘 클릭 -> 팝업의 양식 시작 버튼 클릭을 아이콘이 더 이상 안 보일 때까지 반복
    # (아이콘 개수가 화면마다 달라서 반복 횟수를 미리 알 수 없어 매번 새로 캡처/매칭한다)
    from capture_screen import capture_full_screen

    handled_count = 0
    for _ in range(max_iterations):  # 매칭 오류 등으로 무한 반복되는 것을 방지하기 위한 상한
        try:
            screen = capture_full_screen()
            icon_matches = find_all_templates(screen, icon_template_path, threshold)
        except Exception as e:
            log(f"풍선 아이콘 매칭 중 오류 발생: {e}")
            break

        if not icon_matches:
            break

        icon_match = icon_matches[0]  # confidence가 가장 높은 아이콘부터 처리
        log(f"풍선 아이콘 클릭: confidence={icon_match['confidence']:.4f} at ({icon_match['x']}, {icon_match['y']})")
        click_center(icon_match)
        time.sleep(1)  # 팝업이 뜰 때까지 대기

        try:
            popup_screen = capture_full_screen()
            confirm_matches = find_all_templates(popup_screen, confirm_template_path, threshold)
        except Exception as e:
            log(f"양식 시작 버튼 매칭 중 오류 발생: {e}")
            break

        if not confirm_matches:
            log("양식 시작 버튼을 찾지 못했습니다.")
            break

        confirm_match = confirm_matches[0]
        log(f"양식 시작 버튼 클릭: confidence={confirm_match['confidence']:.4f}")
        click_center(confirm_match)
        handled_count += 1
        time.sleep(2)  # 팝업이 닫히고 다음 아이콘 탐색 전 최소 간격

    return handled_count


if __name__ == "__main__":
    from capture_screen import capture_full_screen

    screenshot = capture_full_screen()

    check_and_click(screenshot, [
        "assets/idle_state_beginner_2560.png",
        "assets/idle_state_intermediate_2560.png",
        "assets/idle_state_advanced_2560.png",
    ])
