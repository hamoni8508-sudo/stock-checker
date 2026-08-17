import os
import requests

# 텔레그램 보안 정보 (GitHub Secrets)
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")

def send_test_message():
    if not TELEGRAM_TOKEN or not TELEGRAM_CHAT_ID:
        print("❌ 오류: TELEGRAM_TOKEN 또는 TELEGRAM_CHAT_ID가 GitHub Secrets에 설정되지 않았습니다.")
        return

    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    message = "🔔 [텔레그램 연동 테스트]\n\n알림 기능이 정상적으로 가동 중입니다!\n이 메시지가 도착했다면 토큰 및 Chat ID 설정이 완벽하게 완료된 상태입니다."
    data = {"chat_id": TELEGRAM_CHAT_ID, "text": message}

    try:
        response = requests.post(url, data=data, timeout=10)
        res_json = response.json()
        
        if res_json.get("ok"):
            print("✅ 텔레그램 메시지 발송에 성공했습니다!")
        else:
            print(f"❌ 텔레그램 발송 실패 (오류 응답): {res_json}")
    except Exception as e:
        print(f"❌ 네트워크 또는 기타 오류 발생: {e}")

if __name__ == "__main__":
    send_test_message()
