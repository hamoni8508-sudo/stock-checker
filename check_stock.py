import os
import time
import requests
from playwright.sync_api import sync_playwright

# 소니 스토어 해당 상품 URL
TARGET_URL = "https://store.sony.co.kr/product-view/135951891"

# 텔레그램 보안 정보
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")

def send_telegram(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    data = {"chat_id": TELEGRAM_CHAT_ID, "text": message}
    try:
        requests.post(url, data=data, timeout=10)
    except Exception as e:
        print(f"텔레그램 발송 실패: {e}")

def check_once():
    """1회 재고 단단히 확인 함수"""
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            locale="ko-KR"
        )
        page = context.new_page()
        
        # 페이지 로딩 후 5초 대기
        page.goto(TARGET_URL, wait_until="domcontentloaded", timeout=60000)
        time.sleep(5)
        
        content = page.content()
        browser.close()
        
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
            print("  -> 상태를 구분할 수 없어 스킵합니다.")
            return False

def main():
    # 한번 실행 시 5분(300초) 간격으로 총 5번(약 20~25분) 연속 체크
    CHECK_COUNT = 5
    INTERVAL_SECONDS = 300

    print(f"🔄 [연속 감시 시작] 총 {CHECK_COUNT}회, {INTERVAL_SECONDS//60}분 간격으로 엄격하게 검사합니다.\n")
    
    for i in range(1, CHECK_COUNT + 1):
        print(f"[{i}/{CHECK_COUNT} 회차 검사] {time.strftime('%H:%M:%S')}")
        is_found = check_once()
        
        if is_found:
            print("재입고가 확인되어 연속 감시를 종료합니다.")
            break
            
        if i < CHECK_COUNT:
            print(f"  -> 다음 5분 뒤 검사를 위해 대기 중...\n")
            time.sleep(INTERVAL_SECONDS)

if __name__ == "__main__":
    main()