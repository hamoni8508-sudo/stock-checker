import os
import time
import requests
from playwright.sync_api import sync_playwright

# 소니 스토어 해당 상품 URL
TARGET_URL = "https://store.sony.co.kr/product-view/135951891"

# 환경 변수 (GitHub Secrets 및 기본 제공 변수)
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")
GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN")
GITHUB_REPOSITORY = os.environ.get("GITHUB_REPOSITORY")

def send_telegram(message):
    if not TELEGRAM_TOKEN or not TELEGRAM_CHAT_ID:
        print("텔레그램 토큰 또는 Chat ID가 설정되지 않았습니다.", flush=True)
        return
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    data = {"chat_id": TELEGRAM_CHAT_ID, "text": message}
    try:
        requests.post(url, data=data, timeout=10)
    except Exception as e:
        print(f"텔레그램 발송 실패: {e}", flush=True)

def trigger_next_run():
    """종료 직전 깃허브 API를 직접 호출하여 공백 없이 다음 워크플로우를 즉시 실행시킵니다."""
    if not GITHUB_TOKEN or not GITHUB_REPOSITORY:
        print("  -> ⚠️ GITHUB_TOKEN 또는 GITHUB_REPOSITORY 설정이 없어 자동 바통 터치를 스킵합니다.", flush=True)
        return

    url = f"https://api.github.com/repos/{GITHUB_REPOSITORY}/actions/workflows/check.yml/dispatches"
    headers = {
        "Authorization": f"Bearer {GITHUB_TOKEN}",
        "Accept": "application/vnd.github.v3+json"
    }
    data = {"ref": "main"}
    try:
        res = requests.post(url, headers=headers, json=data, timeout=10)
        if res.status_code == 204:
            print("  -> 🚀 [셀프 바통 터치] 다음 2시간 감시 작업을 공백 없이 즉시 호출했습니다!", flush=True)
        else:
            print(f"  -> ⚠️ 바통 터치 호출 응답 코드: {res.status_code}", flush=True)
    except Exception as e:
        print(f"  -> ⚠️ 바통 터치 API 호출 중 오류 발생: {e}", flush=True)

def check_once():
    """1회 재고 검사 수행"""
    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=True,
            args=[
                "--no-sandbox",
                "--disable-setuid-sandbox",
                "--disable-dev-shm-usage",
                "--disable-gpu"
            ]
        )
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
            locale="ko-KR"
        )
        page = context.new_page()
        
        try:
            page.goto(TARGET_URL, wait_until="domcontentloaded", timeout=30000)
            time.sleep(3)
            content = page.content()
        finally:
            page.close()
            context.close()
            browser.close()

    # 1. 품절 키워드 감지
    outofstock_keywords = ["일시품절", "일시 품절", "재입고 알림"]
    if any(kw in content for kw in outofstock_keywords):
        print("  -> [결과] 현재 여전히 '일시품절' 상태입니다.", flush=True)
        return False

    # 2. 구매 가능 키워드 감지
    available_keywords = ["바로 구매", "바로구매", "구매하기"]
    if any(kw in content for kw in available_keywords):
        msg = f"🎉 [소니 스토어 재입고 알림!]\n\n지금 상품 구매가 가능합니다!\n\n구매하러 가기:\n{TARGET_URL}"
        send_telegram(msg)
        print("  -> 🎉 [결과] 재입고 감지! 텔레그램 메시지 발송 완료.", flush=True)
        return True
    else:
        print("  -> [결과] 상태 키워드를 확실히 구별할 수 없어 스킵합니다.", flush=True)
        return False

def main():
    CHECK_COUNT = 120  # 1분 간격 120회 (2시간)
    INTERVAL_SECONDS = 60

    print(f"🔄 [초밀착 감시 시작] 총 {CHECK_COUNT}회, {INTERVAL_SECONDS}초(1분) 간격으로 검사합니다.\n", flush=True)

    for i in range(1, CHECK_COUNT + 1):
        print(f"[{i}/{CHECK_COUNT} 회차] {time.strftime('%H:%M:%S')}", flush=True)
        
        # 119회차(종료 1분 전)에 다음 2시간 작업을 미리 구동시킴 (공백 제거)
        if i == CHECK_COUNT - 1:
            trigger_next_run()

        try:
            is_found = check_once()
            if is_found:
                print("재입고가 확인되어 연속 감시를 종료합니다.", flush=True)
                break
        except Exception as e:
            print(f"  -> ⚠️ 접속 중 일시 오류 발생 (1분 뒤 자동 재시도): {e}", flush=True)

        if i < CHECK_COUNT:
            print(f"  -> 다음 1분 뒤 재검사를 위해 대기 중...\n", flush=True)
            time.sleep(INTERVAL_SECONDS)

if __name__ == "__main__":
    main()
