import random
import time
import json
import os
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, TimeoutError
from typing import Dict, Optional
from source.generate.chat_seesion import Pipeline
from utils.utils_pipeline import HelperPiline
from configs.config_system import LoadConfig

HELPER = HelperPiline()

def handle_request(
    InputText: None,
    IdRequest: None,
    UserName: None,
    MemberCode: None,
    NameBot: None,
    Address: None,
    PhoneNumber: None):
    
    start_time = time.time()
    results = {
        "products": [], 
        "product_confirms": [],
        "terms": [], 
        "content": "",
        "status": 200, 
        "message": "", 
        "time_processing": "", 
    }
    
    valid_codes = ['NORMAL']
    MemberCode = MemberCode if MemberCode in valid_codes else "NORMAL"
    Users = {
        "phone_number": PhoneNumber,
        "name": UserName,
    }
    
    try:
        if InputText not in ("terms", "first_text", None):
            response = Pipeline(member_code=MemberCode).chat_session(
                InputText=InputText, 
                IdRequest=IdRequest, 
                NameBot=NameBot, 
                UserInfor=Users)
            
            results.update(**response)
            
        elif InputText == "first_text" or InputText is None:
            results["terms"] = LoadConfig.BUTTON
            results["content"] = random.choice(LoadConfig.MESSAGE)
        else:
            results["message"] = 'Invalid input or missing data.'
            results["status"] = 400

    except Exception as e:
        results["status"] = 500
        results["content"] = LoadConfig.SYSTEM_MESSAGE["error_system"]
        results["message"] = str(e)

    results["time_processing"] = f"{time.time() - start_time:.2f}s"
    return results

# def handle_request(
#     InputText=None,
#     IdRequest=None,
#     UserName=None,
#     MemberCode=None,
#     NameBot=None,
#     Address=None,
#     PhoneNumber=None):

#     start_time = time.time()
#     results = {
#         "products": [], 
#         "terms": [], 
#         "content": "",
#         "status": 200, 
#         "message": "", 
#         "time_processing": "", 
#     }

#     valid_codes = ['NORMAL']
#     MemberCode = MemberCode if MemberCode in valid_codes else "NORMAL"
#     Users = {
#         "phone_number": PhoneNumber,
#         "name": UserName,
#     }

#     try:
#         if InputText not in ("terms", "first_text", None):
#             response = Pipeline(member_code=MemberCode).chat_session(
#                 InputText=InputText, 
#                 IdRequest=IdRequest, 
#                 NameBot=NameBot, 
#                 UserInfor=Users)
            
#             results.update(**response)

#         elif InputText == "first_text" or InputText is None:
#             results["terms"] = LoadConfig.BUTTON
#             results["content"] = random.choice(LoadConfig.MESSAGE)
#             results["message"] = "Welcome message loaded."

#         else:
#             results["message"] = 'Invalid input or missing data.'
#             results["status"] = 400

#     except Exception as e:
#         results["status"] = 500
#         results["content"] = LoadConfig.SYSTEM_MESSAGE.get("error_system", "Lỗi hệ thống.")
#         results["message"] = str(e)

#     results["time_processing"] = f"{time.time() - start_time:.2f}s"

#     # Convert results to JSON
#     return json.dumps(results, ensure_ascii=False, indent=2)

def handle_title_conversation(phone_number: None) -> dict:
    data = {"data": []}
    user_specific_conversation = os.path.join(LoadConfig.CONVERSATION_STORAGE, phone_number)
    for session_path in os.listdir(user_specific_conversation):
        session_conv_path = os.path.join(user_specific_conversation, session_path)
        with open(session_conv_path, mode='r', encoding='utf-8') as f:
            conversation = json.load(f)
        session_id = list(conversation.keys())[0]
        title = conversation[session_id][0]['human']
        
        data['data'].append({"session_id": session_id, "title": title})
    return data

def hanle_conversation(phone_number: None, session_id: None) -> dict:
    session_conv_path = os.path.join(LoadConfig.CONVERSATION_STORAGE, phone_number, session_id + '.json')
    with open(session_conv_path, mode='r', encoding='utf-8') as f:
            conversation = json.load(f)
    
    data = {"data": conversation[session_id]}
    return data

if __name__ == "__main__":
    data = handle_title_conversation("088695868")
    print(data)
            
    
    
    