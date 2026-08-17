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
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    data = {"chat_id": TELEGRAM_CHAT_ID, "text": message}
    try:
        requests.post(url, data=data, timeout=10)
    except Exception as e:
        print(f"텔레그램 발송 실패: {e}")

def check():
    with sync_playwright() as p:
        print("가상 브라우저를 실행하여 소니 스토어 재고 상태를 확인합니다...")
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            locale="ko-KR"
        )
        page = context.new_page()
        
        # 페이지 이동 후 동적 자바스크립트 렌더링 완료를 위해 5초 대기
        page.goto(TARGET_URL, wait_until="domcontentloaded", timeout=60000)
        time.sleep(5)
        
        # 실제 렌더링된 화면 전체 텍스트 추출
        content = page.content()
        browser.close()
        
        # 1. 품절 키워드 감지 ('일시품절', '일시 품절', '재입고 알림')
        outofstock_keywords = ["일시품절", "일시 품절", "재입고 알림"]
        if any(kw in content for kw in outofstock_keywords):
            print("현재 여전히 '일시품절' 상태입니다. (정상 모니터링 중)")
            return

        # 2. 구매 가능 키워드 감지 ('바로 구매', '바로구매', '구매하기')
        available_keywords = ["바로 구매", "바로구매", "구매하기"]
        if any(kw in content for kw in available_keywords):
            msg = f"🎉 [소니 스토어 재입고 알림!]\n\n지금 상품 구매가 가능합니다!\n\n구매하러 가기:\n{TARGET_URL}"
            send_telegram(msg)
            print("재입고 감지! 텔레그램 메시지를 성공적으로 발송했습니다.")
        else:
            print("재고 상태를 완벽히 구분할 수 없어 오탐 방지를 위해 알림을 발송하지 않았습니다.")

if __name__ == "__main__":
    check()