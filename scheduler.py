import time
import schedule
from PIL import Image

from capture_screen import capture_full_screen
from template_match import check_and_click

TEMPLATE_PATHS = [
    "assets/idle_state_beginner.png",
    "assets/idle_state_intermediate.png",
    "assets/idle_state_advanced.png",
]


def job():
    print("시작...")
    try:
        screenshot_path = capture_full_screen()
        screenshot = Image.open(screenshot_path)
        check_and_click(screenshot, TEMPLATE_PATHS)
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
