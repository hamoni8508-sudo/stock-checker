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
        
        # 페이지 이동 후 자바스크립트 로딩 완료를 위해 5초 대기
        page.goto(TARGET_URL, wait_until="domcontentloaded", timeout=60000)
        time.sleep(5)
        
        # 실제 렌더링된 화면 전체 텍스트 추출
        content = page.content()
        browser.close()
        
        # '일시품절' 문구가 정상적으로 인식되었는지 검증
        if "일시품절" in content or "일시 품절" in content or "재입고 알림" in content:
            msg = f"✅ [텍스트 인식 성공!]\n\n소니 스토어 페이지에서 '일시품절' 문구를 완벽하게 읽어냈습니다!\n\n자바스크립트 렌더링 및 페이지 탐색이 정상 작동 중입니다."
            send_telegram(msg)
            print("일시품절 문구 인식 성공! 텔레그램 메시지를 전송했습니다.")
        else:
            msg = f"⚠️ [텍스트 인식 실패]\n\n페이지에서 '일시품절' 문구를 읽어내지 못했습니다."
            send_telegram(msg)
            print("일시품절 문구를 찾지 못했습니다.")

if __name__ == "__main__":
    check()
