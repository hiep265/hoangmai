# from configs.config_system import SYSTEM_CONFIG
# from icecream import ic

######## TEST ELASTICSEARCH ########
# from source.retriever.elastic import ElasticQueryEngine
# from source.retriever.extract_specifications import extract_info

# query = "camera kính hiển vi"
# demands = extract_info(query=query)
# # print(demands)
# response = ElasticQueryEngine(member_code="NORMAL").search_db(demands=demands)
# print(response[0])

# from source.retriever.elastic_search.elastic_helper import RetrieveHelper
# es = RetrieveHelper()
# es.check_specific_field("sold_quantity")
####### TEST CHAT SEASION ########
# from source.generate.chat_seasion import chat_interface
# while True:
#     query = input("Nhập câu hỏi: ")
#     if query == "exits":
#         break
#     response = chat_interface(query=query)
#     ic(response)

######### TEST CRAWLER ########
# from utils.crawler.crawler_website import CrawlerWebsites
# crawler = CrawlerWebsite(url="https://www.dienmayxanh.com/may-lanh")
# df = crawler.get_info_product()

######### TEST ROUTER ########
# from source.router.router import decision_search_type
# query = ""
# type = decision_search_type(query=query)
# print("Type: ", type['content'])

# ######### TEST TOOL SEARCH ########
# from source.similar_product.searcher import SimilarProductSearchEngine
# from langchain_core.prompts import PromptTemplate
# from langchain_core.output_parsers import StrOutputParser
# from source.prompt.template import PROMPT_SIMILAR_PRODUCT

# engine = SimilarProductSearchEngine()
# similar_product_found = engine.search(product_find=type.split("|")[1].strip())
# product_found_str = "\n".join(similar_product_found)


# prompt = PromptTemplate(
#     input_variables=['question', 
#                      'context'],
#     template=PROMPT_SIMILAR_PRODUCT
# )
# model = SYSTEM_CONFIG.load_rag_model()
# chain = prompt | model | StrOutputParser()
# response = chain.invoke({'question': query, 
#                         'context': product_found_str})
# print(response)

######### TEST CHAT CLS PRODUCT ########
# from source.router.router import classify_product
# query = "điều hòa giá 10 triệu"
# response = classify_product(query=query)
# print(response)

######### TEST CHAT API CALL ########
# from source.generate.chat_seesion import Pipeline
# from handle_request import handle_request

# response = handle_request(
#     # InputText = "có loại nào khác nữa không",
#     # InputText = "cho tôi xem máy hàn",
#     InputText = "cho tôi xem tua vít",
#     UserName="Nguyễn Công Vinh",
#     IdRequest="8386",
#     PhoneNumber='0123456789',
#     Address='Hà Nội',
#     MemberCode="NORMAL",
#     NameBot=None)
# print(response)
#so sách chatbot dùng backend là code python và n8n

# from utils.user_helper import UserHelper
# UserHelper().save_conversation(phone_number="0123456789", id_request="123", query="gmsdgsdm", response="sdmn")
# response = UserHelper().load_conversation(conv_user="0123456789", id_request="123")
# print(response)

######### TEST CHATCHIT  ############
# from langchain_core.prompts import PromptTemplate
# from source.prompt.template import PROMPT_CHATCHIT

# while True:
#     question = input("Nhập câu hỏi của bạn:")
#     if question == "q":
#         break
#     template = PromptTemplate(
#                     input_variables=['question'],
#                     template=PROMPT_CHATCHIT).format(question=question)
#     response = SYSTEM_CONFIG.load_chatchit_model().invoke(template).content
#     print(response)

######### TEST DATABASE ############
# from utils.postgre_logger import PostgreHandler
# postgres_handle = PostgreHandler()
# postgres_handle.create_table()
# postgres_handle.connector.close()

# import logging
# from utils.postgre_logger import PostgreHandler

# if __name__ == "__main__":
#     logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

#     postgres_handle = PostgreHandler()

#     if postgres_handle.connector:
#         # Nếu cần tạo lại table (tùy bạn)
#         # postgres_handle.create_table()
        
#         postgres_handle.connector.close()
#         logging.info("Connection closed.")
#     else:
#         logging.error("Failed to connect to PostgreSQL.")


######### TIEN XU LY DU LIEU ##########
# import pandas as pd
# from bs4 import BeautifulSoup
# import re

# # Đọc file Excel
# df = pd.read_excel('product_update.xlsx')

# # Chỉ giữ lại các hàng có giá trị 'kich_hoat' là 1
# df = df[df['kich_hoat'] == 1]

# # Bỏ tiền tố "Thiết bị>>" và "Linh kiện>>" trong cột 'danh_muc'
# df['danh_muc'] = df['danh_muc'].str.replace('^Thiết bị>>', '', regex=True)
# df['danh_muc'] = df['danh_muc'].str.replace('^Linh kiện>>', '', regex=True)

# # Thay 'KHÁC' bằng chuỗi rỗng trong cột 'thuong_hieu'
# df['thuong_hieu'] = df['thuong_hieu'].replace('KHÁC', '')

# # Xóa các cột không cần thiết (nếu tồn tại)
# columns_to_drop = [
#     'gia_cu','hinh_anh','link_video','xoa_anh','trong_luong','kich_hoat','sp_moi','main_keyword',
#     'tom_tat','seo_title','seo_keyword','seo_description','hien_trang_chu','khuyen_mai'
# ]
# df.drop(columns=[col for col in columns_to_drop if col in df.columns], inplace=True)

# # Hàm làm sạch HTML, icon và xóa đoạn Hoàng Mai Mobile
# def clean_html(text):
#     if pd.isna(text):
#         return ''
#     soup = BeautifulSoup(text, 'html.parser')
#     plain_text = soup.get_text(separator=' ', strip=True)

#     hoangmai_pattern = (
#         r"(Nếu có bất kỳ thắc mắc nào liên quan tới sản phẩm, hãy liên hệ với Hoàng Mai Mobile để được chăm sóc tốt nhất nhé!\s*)?"
#         r"HOÀNG MAI MOBILE Chuyên cung cấp: Linh kiện điện thoại, dụng cụ sửa chữa, vật tư ép kính Smartphone\s*"
#         r"Địa chỉ: Ngõ 117 Thái Hà - Phường Trung Liệt - Quận Đống Đa - TP Hà Nội\s*"
#         r"(☎\s*)?Điện thoại: 098\.215\.3333"
#     )
#     plain_text = re.sub(hoangmai_pattern, '', plain_text)

#     cleaned_text = re.sub(r'[✔✅➤►★☆•+☎🔧🛠️❌💡➡️→←↑↓⚡🌟🔥📱🔍✨🔹📢📌🔊🔄🛡🔋📡🏠🌡🔋]', '', plain_text)
#     cleaned_text = re.sub(r'\s{2,}', ' ', cleaned_text).strip()
#     return cleaned_text

# # Làm sạch cột 'mo_ta'
# df['mo_ta'] = df['mo_ta'].apply(clean_html)

# # Sắp xếp theo cột 'danh_muc'
# df.sort_values(by='danh_muc', inplace=True)

# # Đổi tên các cột
# df.rename(columns={
#     'id': 'product_info_id',
#     'ma_san_pham': 'product_code',
#     'ten_san_pham': 'product_name',
#     'gia_ban': 'lifecare_price',
#     'danh_muc': 'group_product_name',
#     'thuong_hieu': 'trademark',
#     'ton_kho': 'inventory',
#     'mo_ta': 'specifications',
#     'anh_avatar': 'avatar_images',
# }, inplace=True)
# df['group_product_name'] = df['group_product_name'].str.lower()
# df['group_name'] = df['product_name']
# # Ghi lại vào file mới
# df.to_excel('data_final_NORMAL_merged.xlsx', index=False)



# import pandas as pd

# # Đọc file Excel
# df1 = pd.read_excel('Book1.xlsx')  # chứa 'Mã SP' và 'Mô tả'
# df2 = pd.read_excel('product-export-12-05-2025.xlsx')  # chứa 'product_code' và 'specifications'

# # Tạo từ điển mapping từ Mã SP -> Mô tả
# desc_map = dict(zip(df1['Mã SP'], df1['Mô tả cho sản phẩm']))

# # Cập nhật specifications nếu có mô tả mới trong excel1
# df2['mo_ta'] = df2['ma_san_pham'].map(lambda x: desc_map.get(x, df2.loc[df2['ma_san_pham'] == x, 'mo_ta'].values[0]))

# # Xuất file kết quả
# df2.to_excel('product_update.xlsx', index=False)


# import pandas as pd

# # Đọc file Excel
# file_path = 'Dulieu Hao.xlsx'  # thay bằng đường dẫn tới file của bạn
# df = pd.read_excel(file_path)

# # Đổi tên các cột
# df.rename(columns={
#     'ID': 'product_code',
#     'name': 'product_name',
#     'category': 'group_product_name',
#     'amount': 'lifecare_price',
#     'provider': 'trademark',
#     'stock': 'inventory',
#     'description': 'specifications',
#     'image': 'avatar_images',
#     'link': 'link_product'
# }, inplace=True)

# # Sắp xếp theo group_product_name
# df.sort_values(by='group_product_name', inplace=True)
# df['group_product_name'] = df['group_product_name'].str.lower()
# df['group_name'] = df['product_name']

# df.to_excel('data_final_NORMAL_merged.xlsx', index=False)







# import pandas as pd

# # Đọc file Excel
# file_path = 'data_final_NORMAL_merged.xlsx'  # thay bằng đường dẫn file thật của anh
# df = pd.read_excel(file_path)

# # Lọc những dòng mà group_product_name chứa từ "vỉ" (không phân biệt chữ hoa/thường)
# df_vi = df[df['group_product_name'].str.lower().str.contains('vỉ', na=False)]

# # Hoặc lưu ra file mới nếu cần
# df_vi.to_excel('data_vi_lam_chan.xlsx', index=False)





# import pandas as pd

# file_path = 'data_final_NORMAL_merged.xlsx'
# df = pd.read_excel(file_path)

# def clean_product_name(name):
#     if isinstance(name, str) and '_' in name:
#         # Lấy phần sau dấu gạch dưới đầu tiên
#         return name.split('_', 1)[1].strip()
#     return name

# df['product_name'] = df['product_name'].apply(clean_product_name)

# df['group_name'] = df['product_name']

# df.to_excel('data_productname_cleaned_v2.xlsx', index=False)




# import pandas as pd
# import requests
# from bs4 import BeautifulSoup
# import logging

# logging.basicConfig(level=logging.INFO)

# def _get_jpg_image_link(url: str) -> str:
#     try:
#         response = requests.get(url, timeout=5)
#         soup = BeautifulSoup(response.text, "html.parser")
#         image_tags = soup.find_all("img")
#         for img in image_tags:
#             src = img.get("src")
#             if src and ".jpg" in src:
#                 if src.startswith("http"):
#                     return src
#                 else:
#                     return "https://hoangmaimobile.vn" + src
#     except Exception as e:
#         logging.error("CRAWL IMAGE ERROR: " + str(e))
#     return ""

# # Đọc file Excel
# file_path = "data_final_NORMAL_merged1.xlsx"
# df = pd.read_excel(file_path)

# # Kiểm tra cột avatar_images có tồn tại không
# if 'avatar_images' in df.columns:
#     df['avatar_images'] = df['avatar_images'].apply(lambda url: _get_jpg_image_link(url) if isinstance(url, str) and url.endswith(".html") else url)
# else:
#     logging.error("Không tìm thấy cột 'avatar_images' trong file Excel.")

# # Ghi lại kết quả ra file mới
# df.to_excel("data_final_NORMAL_merged.xlsx", index=False)
