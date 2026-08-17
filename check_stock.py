import os
import requests
from playwright.sync_api import sync_playwright

# 소니 스토어 해당 상품 URL
TARGET_URL = "https://store.sony.co.kr/product-view/135951891"

# 텔레그램 보안 정보 (GitHub Secrets에서 받아옴)
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
        # 가상 크롬 브라우저 실행
        print("가상 브라우저를 실행하여 소니 스토어에 접속합니다...")
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        
        # 페이지 이동 및 자바스크립트 로딩 완료 대기
        page.goto(TARGET_URL, wait_until="networkidle", timeout=60000)
        
        # 자바스크립트 실행이 끝난 실제 화면의 전체 텍스트 추출
        content = page.content()
        browser.close()
        
        # 화면 텍스트에 '일시품절'이 포함되어 있는지 확인
        if "일시품절" in content:
            print("현재 여전히 '일시품절' 상태입니다. (자바스크립트 렌더링 확인 완료)")
        elif "바로 구매" in content or "장바구니" in content:
            msg = f"🎉 [소니 스토어 재입고 알림!]\n\n지금 상품 구매가 가능합니다!\n\n구매하러 가기:\n{TARGET_URL}"
            send_telegram(msg)
            print("재입고 감지! 텔레그램 메시지를 발송했습니다.")
        else:
            print("페이지를 읽었으나 상태를 판단할 수 없습니다. 로그 확인 필요.")

if __name__ == "__main__":
    check()
