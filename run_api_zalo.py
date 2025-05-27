import uvicorn
from fastapi import FastAPI, Form
from fastapi import FastAPI, File, UploadFile
from fastapi import FastAPI, UploadFile, Form, File
from handle_request import handle_request, handle_title_conversation, hanle_conversation
from configs.config_system import LoadConfig
# from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()
numberrequest = 0

# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"],  
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

@app.post('/chatbot_proactive')
async def post_request(
    idRequest: str = Form(...),
    nameBot: str = Form(...),
    phoneNumber: str = Form(...),
    userName: str = Form(...),
    memberCode: str = Form(None),
    inputText: str = Form(None),
    address: str = Form(None),
):
    global numberrequest
    numberrequest += 1

    print("----------------NEW_SESSION--------------")
    print("NumberRequest", numberrequest)
    print("User  = ", userName)
    print("PhoneNumber  = ", phoneNumber)
    print("InputText  = ", inputText)

    results = handle_request(
        # timeout_seconds=LoadConfig.TIMEOUT,
        InputText=inputText,
        IdRequest=idRequest,
        UserName=userName,
        MemberCode=memberCode,
        NameBot=nameBot,
        PhoneNumber=phoneNumber,
        Address=address
    )

    print("----------------HANDLE_REQUEST_OUTPUT--------------")
    print(results)
    return results

@app.post('/get_conv_title')
async def get_title(phoneNumber: str = Form(...)): #10
    data = handle_title_conversation(phone_number=phoneNumber)
    results = {
        'data' : data,
        "status_code" : 200,
        "message" : "Get conversation title successfull0!"
    }
    return results

@app.post('/get_chat_conv')
async def post_session(
    phoneNumber: str = Form(...),
    sessionId: str = Form(...)
):
    data = hanle_conversation(phone_number=phoneNumber, session_id=sessionId)
    return data

# uvicorn.run(app, host="0.0.0.0", port=LoadConfig.PORT)
uvicorn.run(app, host="0.0.0.0", port=7878)
# if __name__ == "__main__":
#     import uvicorn
#     uvicorn.run("run_api:app", host="0.0.0.0", port=7878, reload=True)
