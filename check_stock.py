import os
import time
import requests
from playwright.sync_api import sync_playwright

# 소니 스토어 해당 상품 URL
TARGET_URL = "https://store.sony.co.kr/product-view/135951891"

# 텔레그램 보안 정보 (GitHub Secrets)
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")

def send_telegram(message):
    if not TELEGRAM_TOKEN or not TELEGRAM_CHAT_ID:
        print("텔레그램 토큰 또는 Chat ID가 설정되지 않았습니다.")
        return
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    data = {"chat_id": TELEGRAM_CHAT_ID, "text": message}
    try:
        requests.post(url, data=data, timeout=10)
    except Exception as e:
        print(f"텔레그램 발송 실패: {e}")

def check_once(browser):
    """1회 재고 검사 수행"""
    context = browser.new_context(
        user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        locale="ko-KR"
    )
    page = context.new_page()
    try:
        # 60초 타임아웃 설정
        page.goto(TARGET_URL, wait_until="domcontentloaded", timeout=60000)
        time.sleep(5)
        content = page.content()
    finally:
        context.close()
    
    # 1. 품절 키워드 감지
    outofstock_keywords = ["일시품절", "일시 품절", "재입고 알림"]
    if any(kw in content for kw in outofstock_keywords):
        print("  -> 현재 여전히 '일시품절' 상태입니다.")
        return False

    # 2. 구매 가능 키워드 감지
    available_keywords = ["바로 구매", "바로구매", "구매하기"]
    if any(kw in content for kw in available_keywords):
        msg = f"🎉 [소니 스토어 재입고 알림!]\n\n지금 상품 구매가 가능합니다!\n\n구매하러 가기:\n{TARGET_URL}"
        send_telegram(msg)
        print("  -> 🎉 재입고 감지! 텔레그램 메시지 발송 완료.")
        return True
    else:
        print("  -> 키워드를 확실히 구별할 수 없어 스킵합니다.")
        return False

def main():
    # 1분(60초) 간격으로 총 20번(약 20분간) 연속 검사
    CHECK_COUNT = 20
    INTERVAL_SECONDS = 60

    print(f"🔄 [초밀착 감시 시작] 총 {CHECK_COUNT}회, {INTERVAL_SECONDS}초(1분) 간격으로 검사합니다.\n")

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        try:
            for i in range(1, CHECK_COUNT + 1):
                print(f"[{i}/{CHECK_COUNT} 회차] {time.strftime('%H:%M:%S')}")
                try:
                    is_found = check_once(browser)
                    if is_found:
                        print("재입고가 확인되어 연속 감시를 종료합니다.")
                        break
                except Exception as e:
                    print(f"  -> ⚠️ 접속 중 일시 오류 발생 (1분 뒤 자동 재시도): {e}")

                if i < CHECK_COUNT:
                    print(f"  -> 다음 1분 뒤 재검사를 위해 대기 중...\n")
                    time.sleep(INTERVAL_SECONDS)
        finally:
            browser.close()

if __name__ == "__main__":
    main()
