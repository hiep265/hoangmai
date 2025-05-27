import os
from dataclasses import dataclass
from dotenv import load_dotenv
import pandas as pd

load_dotenv()
os.environ['OPENAI_API_KEY'] = os.getenv("OPENAI_API_KEY")
@dataclass
class LoadConfig:
    # API CONFIG
    MEMBER_CODE = ["NORMAL"]
    TIMEOUT = 50
    
    # SEVER CONFIG
    IP = "0.0.0.0"
    PORT = 7878

    # POSTGRES CONFIG
    POSTGRES_HOST = "localhost"
    POSTGRES_DB_NAME = "chatbot_hm"
    POSTGRES_PASSWORD = "20032003"
    POSTGRES_USER = "postgres"
    POSTGRES_PORT = 5432
    POSTGRE_TIMEOUT = 6

    # ELASTIC_SEACH_CONFIG
    INDEX_NAME_ELS = [index_name.replace("-", "").lower() for index_name in MEMBER_CODE]
    NUM_SIZE_ELAS = 8
    CHEAP_KEYWORDS =  ["rẻ", "giá rẻ", "giá thấp", "bình dân", "tiết kiệm", "khuyến mãi", "giảm giá", "hạ giá", "giá cả phải chăng", "ưu đãi", "rẻ nhất", "nhỏ nhất"]
    EXPENSIVE_KEYWORDS =  ["giá đắt", "giá cao", "xa xỉ", "sang trọng", "cao cấp", "đắt đỏ", "chất lượng cao", "hàng hiệu", "hàng cao cấp", "thượng hạng", "lớn nhất", "đắt nhất", "giá đắt nhất"]

    # DIRECTORIES
    VECTOR_DATABASE_STORAGE = 'data/vector_db/{member_code}'
    ALL_PRODUCT_FILE_NOT_MERGE_STORAGE = 'data/data_private/data_member/data_final_{member_code}.xlsx'
    ALL_PRODUCT_FILE_MERGED_STORAGE = 'data/data_private/data_member/data_final_{member_code}_merged.xlsx'
    CONVERSATION_STORAGE = 'security/conv_storage'
    INFO_USER_STORAGE = 'security/info_user_storage' 
    FEEDBACK_STORAGE = "security/feedback"

    # LLM_CONFIG
    GPT_MODEL = 'gpt-4o-mini-2024-07-18'
    TEMPERATURE_RAG = 0.2
    TEMPERATURE_CHAT = 0.5
    MAX_TOKEN = 1024

    # RETRIEVER_CONFIG
    EMBEDDING_BAAI = 'BAAI/bge-small-en-v1.5'
    VECTOR_EMBED_BAAI = 384
    EMBEDDING_OPENAI = 'text-embedding-ada-002'
    VECTOR_EMBED_OPENAI = 1536
    TOP_K_PRODUCT = 3
    TOP_K_QUESTION = 3
    TOP_P = 0.9

    LIST_GROUP_NAME = pd.unique(pd.read_excel("data/data_private/data_member/data_final_NORMAL_merged.xlsx")['group_product_name'].tolist())
    TOP_CONVERSATION = 4
  
    MESSAGE = [
        "Chào anh/chị, Hoàng Mai Mobile cảm ơn anh/chị đã quan tâm đến sản phẩm của cửa hàng. Em có thể hỗ trợ anh/chị thông tin gì không ạ?",
        "Chào mừng anh/chị đã đến với Hoàng Mai Mobile. Anh/chị cần tìm hiểu sản phẩm nào ạ ?",
        "Em rất vui khi được hỗ trợ anh/chị! Em có thể giúp gì cho anh/chị về tìm kiếm thông tin sản phẩm hôm nay?",
    ]
    
    BUTTON = [
        "Có bán cap âm lượng Iphone không",
        "Cần tìm keo oca samsung",
        "Bên bạn có những sản phẩm gì?",
        "Thông tin địa chỉ của shop ở đâu?",
    ]
    
    SYSTEM_MESSAGE = {"error_system": "Hiện tại em đang chưa hiểu rõ yêu cầu anh/chị đưa ra, để đảm bảo trải nghiệm tốt nhất trong quá trình mua sắm em mong anh/chị vui lòng đặt lại câu hỏi ạ!",
                      "end_message": f"""Cảm ơn anh/chị đã quan tâm đến sản phẩm của Hoàng Mai Mobile. Nếu có bất kì thắc mắc hay câu hỏi xin vui lòng liên hệ đến SĐT: 0982153333""",
                      "question_other": "Hiện tại em đang chưa hiểu rõ yêu cầu anh/chị đưa ra, để đảm bảo trải nghiệm tốt nhất trong quá trình mua sắm em mong anh/chị vui lòng đặt lại câu hỏi hoặc liên hệ SĐT: 0982153333 để được tư vấn thêm & hỗ trợ ạ! Em xin chân thành cảm ơn!"} # lỗi