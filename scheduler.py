import time
import schedule
import pyautogui

from capture_screen import capture_full_screen, save_screenshot
from template_match import check_and_click, run_balloon_popup_flow

BALLOON_ICON_PATH = "assets/balloon_icon.png"
FORM_START_BUTTON_PATH = "assets/form_start_button.png"


def get_template_paths():
    # 템플릿 매칭은 화면 해상도에 따라 픽셀 크기가 달라져 확신도가 크게 떨어지므로,
    # 1920x1080 / 2560x1440 환경을 오가며 써도 되도록 실행 시점 해상도에 맞는 에셋을 고른다
    width, height = pyautogui.size()
    resolution = "1920" if width <= 1920 else "2560"
    print(f"현재 해상도: {width}x{height} -> {resolution} 템플릿 세트 사용")
    return [
        f"assets/idle_state_beginner_{resolution}.png",
        f"assets/idle_state_intermediate_{resolution}.png",
        f"assets/idle_state_advanced_{resolution}.png",
    ]


def job():
    print("시작...")
    try:
        screenshot = capture_full_screen()
        match_count = check_and_click(screenshot, get_template_paths())
        if match_count > 0:
            # 매칭 성공(클릭 발생)한 회차만 남겨서 로그 용량 낭비 방지
            saved_path = save_screenshot(screenshot)
            print(f"매칭 성공 로그 저장: {saved_path}")

            # 완료 상태 클릭 후 나타나는 풍선 아이콘 -> 양식 시작 팝업 처리
            handled = run_balloon_popup_flow(BALLOON_ICON_PATH, FORM_START_BUTTON_PATH)
            print(f"양식 시작 처리 개수: {handled}")
    except Exception as e:
        # 한 회차 실패로 스케줄 루프 전체가 종료되지 않도록 여기서 잡아서 다음 주기를 계속 진행
        print(f"작업 실행 중 오류 발생: {e}")


if __name__ == "__main__":
    job()  # 시작하자마자 1회 실행
    schedule.every(30).minutes.do(job)

    print("30분마다 반복 실행 중... (Ctrl+C로 종료)")
    while True:
        schedule.run_pending()
        time.sleep(1)
