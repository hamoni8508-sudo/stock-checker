import os
import requests

# 소니 스토어 해당 상품 URL
TARGET_URL = "https://store.sony.co.kr/product-view/135951891"

# 텔레그램 보안 정보 (GitHub Secrets에서 받아옴)
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")

def send_telegram(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    data = {"chat_id": TELEGRAM_CHAT_ID, "text": message}
    try:
        requests.post(url, data=data)
    except Exception as e:
        print(f"텔레그램 발송 실패: {e}")

def check():
    # 차단 방지를 위한 브라우저 헤더 설정
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept-Language": "ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7",
    }
    
    try:
        response = requests.get(TARGET_URL, headers=headers, timeout=10)
        response.encoding = 'utf-8'
        html_text = response.text
        
        # '일시품절' 문구가 사라졌거나 '바로 구매' 문구가 나타나면 알림
        if "일시품절" not in html_text or "바로 구매" in html_text:
            msg = f"🎉 [소니 스토어 재입고 알림!]\n\n지금 상품 구매가 가능합니다!\n\n구매하러 가기:\n{TARGET_URL}"
            send_telegram(msg)
            print("재입고 감지! 텔레그램 메시지를 발송했습니다.")
        else:
            print("현재 여전히 '일시품절' 상태입니다.")
            
    except Exception as e:
        print(f"페이지 확인 중 오류 발생: {e}")

if __name__ == "__main__":
    check()
