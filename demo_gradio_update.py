import gradio as gr
from typing import Dict, Optional
import random
import time
import uuid
import logging
import datetime
import json
import requests
from PIL import Image
from io import BytesIO

from configs import config_system
from handle_request import handle_request, handle_title_conversation, hanle_conversation

logging.basicConfig(
    filename='security/feedback_storage/chat.log',
    level=logging.INFO,
    format='%(asctime)s - %(message)s'
)

class ChatBot:
    def __init__(self):
        self.user_sessions = {}
        self.greetings = [
            "Chào mừng anh/chị đã tin tưởng mua sắm tại Hoàng Mai Mobile. Em là Diệu Linh, trợ lý tư vấn bán hàng luôn ở đây để hỗ trợ và tư vấn mua sắm. Chúc anh/chị một ngày rực rỡ và thành công! 🌈",
            "Xin chào! Em là Diệu Linh, trợ lý mua sắm tại Hoàng Mai Mobile sẵn sàng tư vấn cho anh/chị về sản phẩm bên em. Có phải anh chị đang có nhu cầu mua sắm phải không ạ. Anh/chị có thể cho em biết mình đang cần mua sản phẩm gì không ạ?",
        ]
        self.last_response = ""

    def get_user_session(self, phone_number):
        if phone_number not in self.user_sessions:
            self.user_sessions[phone_number] = {
                'chat_history': [],
                'last_response': "",
                'session_id': str(uuid.uuid4()),
            }
        return self.user_sessions[phone_number]

    def validate_chat_preconditions(self, user_name, phone_number, address):
        if not user_name or not phone_number or not address:
            raise gr.Error("Vui lòng nhập đầy đủ thông tin (Tên, Số điện thoại, Địa chỉ) trước khi chat!")
        if not phone_number.isdigit() or len(phone_number) < 10:
            raise gr.Error("Số điện thoại không hợp lệ!")

    def chat(self, message, history, phone_number, address, user_name, name_bot=None):
        self.validate_chat_preconditions(user_name, phone_number, address)
        session = self.get_user_session(phone_number)

        if not message or message.strip() == "":
            bot_message = random.choice(self.greetings)
            session['last_response'] = bot_message
            session['chat_history'].append(("", bot_message))
            return "", session['chat_history'], []

        input_text = message
        session_id = session.get('session_id', str(uuid.uuid4()))

        response = handle_request(
            InputText=input_text,
            IdRequest=session_id,
            NameBot=name_bot,
            UserName=user_name,
            MemberCode="NORMAL",
            PhoneNumber=phone_number,
            Address=address
        )

        bot_message = response.get("content", "")
        print(response.get("products"))
        if response.get("terms"):
            bot_message += "\n\nTerms: " + ", ".join(response.get("terms"))

        product_images = extract_images_from_response(response)

        buy_html = ""
        for p in response.get("product_confirms", []):
            if p.get("link_product"):
                buy_html += f'<a href="{p["link_product"]}" target="_blank">'
                buy_html += f'<button style="margin:5px;padding:10px;background:#DC143C;color:white;border:none;border-radius:5px;">Mua {p["product_name"]}</button>'
                buy_html += '</a>'

        session['last_response'] = bot_message
        session['chat_history'].append((message, bot_message))

        return "", session['chat_history'], product_images, buy_html
        
    def clear_chat(self, phone_number):
        if phone_number in self.user_sessions:
            self.user_sessions[phone_number] = {
                'chat_history': [],
                'last_response': "",
                'session_id': str(uuid.uuid4())
            }
        return None

def extract_images_from_response(response_json):
    images = []
    try:
        for product in response_json.get("products", []):
            url = product.get("link_image", "")
            if url:
                img_response = requests.get(url)
                img = Image.open(BytesIO(img_response.content))
                name = product.get("product_name", "Sản phẩm")
                images.append((img, name))
    except Exception as e:
        print(f"Lỗi khi xử lý ảnh: {e}")
    return images

chatbot = ChatBot()

def get_session_choices(phone_number):
    result = handle_title_conversation(phone_number=phone_number)
    sessions = result.get("data", [])
    choices = [f"{s['session_id']} - {s['title']}" for s in sessions]
    default = choices[0] if choices else None
    return gr.update(choices=choices, value=default)

def load_chat_session(selected_session, phone_number):
    if not selected_session:
        return [], "", []
    
    session_id = selected_session.split(" - ")[0]
    conversation = hanle_conversation(phone_number, session_id)
    chat_history = []
    data = conversation.get("data", []) if conversation else []

    for msg_item in data:
        human = msg_item.get("human", "")
        ai = msg_item.get("ai", "")
        chat_history.append((human, ai))

    chatbot.user_sessions[phone_number] = {
        'chat_history': chat_history,
        'last_response': chat_history[-1][1] if chat_history else "",
        'session_id': session_id
    }

    return chat_history, "", []

def new_session_handler(phone_number):
    if phone_number:
        chatbot.clear_chat(phone_number)
        return [], "", []
    return [], "", []

def recommend_handler(text):
    return text

# --- Gradio Interface ---
with gr.Blocks(css="""
    #chatbot { 
        height: 400px; 
        overflow-y: hidden; 
        border: 1px solid #ddd; 
        border-radius: 15px; 
        padding: 20px;
        background-color: #f7f7f7;
    }
    .user, .bot { 
        padding: 10px 15px; 
        border-radius: 20px; 
        margin: 5px;
    }
    .user { 
        background-color: #F08080; 
        color: black;
    }
    .bot { 
        background-color: #F0F8FF; 
        color: black;
    }
    #input-row {
        display: flex;
        align-items: center;
        gap: 8px;
        margin-top: 10px;
    }
    #input-row .gr-textbox {
        flex-grow: 5;
    }
    #input-row .gr-button {
        flex-grow: 1;
    }
    #input-row .gr-html {
        flex-grow: 2;
        min-width: 150px;
    }

    #input-row button {
        background-color: #DC143C !important;
        color: white !important;
        border: none !important;
        border-radius: 5px;
        padding: 8px 16px;
    }
    #input-row button:hover {
        background-color: #B22222 !important;
    }


""") as demo:
    with gr.Row():
    #     with gr.Column(scale=5, elem_id="logo-col"):
    #         gr.Image(value="static/logo_HMMobile.png", width=500, show_label=False)
        # gr.HTML("""
        #     <div style="text-align:center;">
        #         <img src="https://hoangmaimobile.vn/images/config/logo.svg" style="width: 320px;" />
        #     </div>
        # """)
        gr.HTML("""
            <div style="text-align:center;">
                <a href="https://hoangmaimobile.vn/" target="_blank">
                    <img src="https://hoangmaimobile.vn/images/config/logo.svg" style="width: 320px;" />
                </a>
            </div>
        """)
        
    # with gr.Row():
    #     with gr.Column(scale=1):
    #         gr.Markdown("## Chatbot tư vấn bán hàng 🤖")
    
    with gr.Row():
        with gr.Column(scale=3):
            chatbot_interface = gr.Chatbot(
                elem_id="chatbot",
                avatar_images=("static/avt_user.png", "static/avt_bot.png")
            )
            with gr.Row(elem_id="input-row"):
                msg = gr.Textbox(show_label=False, placeholder="Nhập tin nhắn của bạn ở đây...", scale=5)
                submit_btn = gr.Button("Gửi", variant="primary", scale=1)
                buy_now_html = gr.HTML(label="Nút mua", visible=True)
            with gr.Row():
                recommend_1 = gr.Button("Cho tôi xem danh sách sản phẩm bên bạn?")
                recommend_2 = gr.Button("Tôi cần tìm hộp để tô vít?")
            with gr.Row():
                recommend_3 = gr.Button("Có bán đồng hồ vạn năng không?")
                recommend_4 = gr.Button("Thông tin địa chỉ của shop ở đâu?")
            image_gallery = gr.Gallery(label="Hình ảnh sản phẩm", columns=3, height=200)

        with gr.Column(scale=1):
            user_name = gr.Textbox(
                label="Họ và tên:", 
                value="Vinh"
                # placeholder="Nhập họ & tên của bạn"
            )
            phone_number = gr.Textbox(
                label="Số điện thoại:", 
                value="0868669999"
                # placeholder="Nhập số điện thoại"
            )
            address = gr.Textbox(
                label="Địa chỉ:", 
                value="Hồ Chí Minh"
                # placeholder="Nhập địa chỉ"
            )
            session_dropdown = gr.Dropdown(label="Danh sách lịch sử chat", choices=[], value=None)
            refresh_sessions = gr.Button("Lấy danh sách lịch sử chat")
            load_session_btn = gr.Button("Tải lại cuộc trò chuyện")
            new_session_btn = gr.Button("Tạo cuộc trò chuyện mới")

    # Liên kết sự kiện
    for btn, msg_text in zip(
        [recommend_1, recommend_2, recommend_3, recommend_4],
        ["Cho tôi xem danh sách sản phẩm bên bạn?", "Tôi cần tìm hộp để tô vít?", "Có bán đồng hồ vạn năng không?", "Thông tin địa chỉ của shop ở đâu?"]
    ):
        btn.click(
            lambda text=msg_text: recommend_handler(text),
            outputs=msg
        ).then(
            chatbot.chat,
            inputs=[msg, chatbot_interface, phone_number, address, user_name],
            outputs=[msg, chatbot_interface, image_gallery]
        )

    submit_btn.click(
        chatbot.chat,
        inputs=[msg, chatbot_interface, phone_number, address, user_name],
        outputs=[msg, chatbot_interface, image_gallery, buy_now_html]
    )

    msg.submit(
        chatbot.chat,
        inputs=[msg, chatbot_interface, phone_number, address, user_name],
        outputs=[msg, chatbot_interface, image_gallery, buy_now_html]
    )

    refresh_sessions.click(
        get_session_choices,
        inputs=[phone_number],
        outputs=session_dropdown,
        queue=False
    )
    load_session_btn.click(
        load_chat_session,
        inputs=[session_dropdown, phone_number],
        outputs=[chatbot_interface, msg, image_gallery],
        queue=False
    )
    new_session_btn.click(
        new_session_handler,
        inputs=[phone_number],
        outputs=[chatbot_interface, msg, image_gallery],
        queue=False
    )

demo.launch(share=True)



