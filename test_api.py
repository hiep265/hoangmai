import requests

url = "http://localhost:7878/chatbot_proactive"
data = {
    "idRequest": "123",
    "nameBot": "hmmobile_bot",
    "phoneNumber": "0123456789",
    "userName": "test_user",
    "inputText": "tôi muốn xem máy hàn"
}

response = requests.post(url, data=data)
print(f"Status Code: {response.status_code}")
print(f"Response: {response.text}") 