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

def check():
    with sync_playwright() as p:
        print("가상 브라우저를 실행합니다...")
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            locale="ko-KR"
        )
        page = context.new_page()
        
        # 페이지 이동 후 리액트 동적 데이터 로딩을 위해 5초 완전 대기
        page.goto(TARGET_URL, wait_until="domcontentloaded", timeout=60000)
        time.sleep(5)
        
        # 실제 렌더링된 화면 텍스트 추출
        content = page.content()
        browser.close()
        
        # 1. '일시품절', '일시 품절', '재입고 알림' 중 하나라도 있으면 품절 상태로 판단
        if "일시품절" in content or "일시 품절" in content or "재입고 알림" in content:
            print("현재 여전히 '일시품절' 상태입니다. (정상 확인)")
            return

        # 2. '장바구니' 조건 제외 / 실제 구매 버튼 문구만 확인
        if "바로 구매" in content or "구매하기" in content:
            msg = f"🎉 [소니 스토어 재입고 알림!]\n\n지금 상품 구매가 가능합니다!\n\n구매하러 가기:\n{TARGET_URL}"
            send_telegram(msg)
            print("재입고 감지! 텔레그램 메시지를 발송했습니다.")
        else:
            print("상태를 구분할 수 없어 알림을 보내지 않았습니다.")

if __name__ == "__main__":
    check()
