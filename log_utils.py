from datetime import datetime


def log(message: str) -> None:
    # 30분 주기로 오래 돌아가는 스케줄러라 로그만 보고도 언제 일어난 일인지 알 수 있어야 함
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] {message}")
