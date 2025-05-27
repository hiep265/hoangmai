# Helper functions
import re
import ast
import markdown
import logging 
import pandas as pd
from typing import List, Dict, Any, Union
from source.model.loader import ModelLoader
import requests
from bs4 import BeautifulSoup

class HelperPiline:

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
    #                     # Ghép với domain nếu là đường dẫn tương đối
    #                     return "https://hoangmaimobile.vn" + src
    #     except Exception as e:
    #         logging.error("CRAWL IMAGE ERROR: " + str(e))
    #     return ""
    # @staticmethod
    # def _product_seeking(output_from_llm: str, query_rewritten: str, dataframe: pd.DataFrame) -> List[Dict[str, Any]]:
    #     results = []
    #     try: 
    #         for index, row in dataframe.iterrows():
    #             if any(str(item).lower() in output_from_llm.lower() or 
    #                 str(item) in query_rewritten 
    #                 for item in (row['product_name'], row['product_code'])):

    #                 # Lấy ảnh jpg từ link_product
    #                 jpg_image = HelperPiline._get_jpg_image_link(row['link_product'])

    #                 product = {
    #                     "product_code": row['product_code'],
    #                     "product_name": row['product_name'],
    #                     "link_image": jpg_image,
    #                     "link_web": row['link_product']
    #                 }
    #                 results.append(product)
    #         return results
    #     except Exception as e:
    #         logging.error("PRODUCT SEEKING ERROR: " + str(e))
    #         return results

    @staticmethod
    def _product_seeking(output_from_llm: str, query_rewritten: str,  dataframe: pd.DataFrame) -> List[Dict[str, Any]]:
        results = []
        try: 
            for index, row in dataframe.iterrows():
                if any(str(item).lower() in output_from_llm.lower() or 
                       str(item) in query_rewritten 
                       for item in (row['product_name'], row['product_code'])):
                    
                    product = {
                        "product_code": row['product_code'],
                        "product_name": row['product_name'],
                        "link_image": row['avatar_images'],
                        "link_web": row['link_product']
                    }
                    results.append(product)
            return results
        except Exception as e:
            logging.error("PRODUCT SEEKING ERROR: " + str(e))
            return results

    def _product_confirms(self, 
                        output_from_llm: str, 
                        query_rewritten: str, 
                        dataframe: pd.DataFrame) -> List[Dict[str, Any]]:
        """
        Trích xuất thông tin xác nhận sản phẩm từ đầu ra của mô hình ngôn ngữ và đối chiếu với DataFrame đã cho.
        
        Args:
            output_from_llm (str): Chuỗi đầu ra từ mô hình ngôn ngữ chứa thông tin đơn hàng.
            query_rewritten (str): Chuỗi truy vấn đã được viết lại.
            dataframe (pd.DataFrame): DataFrame chứa thông tin sản phẩm với các cột 'product_name', 'product_info_id', 'file_path', 'avatar_images', 'product_code'.

        Returns:
            List[Dict[str, Any]]: Danh sách các từ điển chứa thông tin sản phẩm được trích xuất.
        """
        import ast
        import logging

        llm = ModelLoader.load_rag_model()

        AMOUNT_PROMPT = f"""Lấy ra số lượng sản phẩm và giá sản phẩm khách đã chốt trong form đơn hàng:
        Ví dụ:
        Input:  <p>Thông tin đơn hàng:</p><ul>
                <li><strong>Tên:</strong> Hoàng  </li>
                <li><strong>SĐT:</strong> 0886945868  </li>
                <li><strong>Sản phẩm:</strong> Điều hòa MDV - Inverter 9000 BTU  </li>
                <li><strong>Số lượng:</strong> 3 cái  </li>
                <li><strong>Giá 1 sản phẩm:</strong> 6,000,000 đồng  </li>
        Format json(không trả markdown): 
                "amount": 3,
                "price": 6000000
        ---------
        Đơn hàng:
        {output_from_llm}
        Lưu ý: trả ra đúng format json ở dạng text, không trả ra gì khác"""

        results = []

        try:
            # Parse LLM response
            response = llm.invoke(AMOUNT_PROMPT.format(output_from_llm=output_from_llm)).content
            response_json = ast.literal_eval(response)
            amount = response_json.get("amount")
            price = response_json.get("price")
            if not amount or not price:
                return results

            # Normalize all text
            normalized_output = output_from_llm.lower()
            normalized_query = query_rewritten.lower()

            # Try to extract product_info_id from text
            matched_product = None
            for _, row in dataframe.iterrows():
                # So khớp theo product_info_id trước
                if str(row['product_code']) in normalized_output or str(row['product_code']) in normalized_query:
                    matched_product = row
                    break
                # Nếu không thì thử theo tên sản phẩm đầy đủ
                if row['product_name'].lower() in normalized_output or row['product_name'].lower() in normalized_query:
                    matched_product = row
                    break

            if matched_product is not None:
                result = {
                    "amount": amount,
                    "price": price,
                    "product_name": matched_product['product_name'],
                    "link_image": matched_product['avatar_images'],
                    "product_code": matched_product['product_code'],
                    "link_product": matched_product['link_product']
                }
                results.append(result)

            return results

        except Exception as e:
            logging.error("PRODUCT CONFIRMS ERROR: " + str(e))
            return results


    @staticmethod
    def _double_check(question: str, dataframe: pd.DataFrame) -> str:
        """

        Kiểm tra lại thông tin sản phẩm trong câu hỏi dựa trên dữ liệu từ dataframe.
        Hàm này sẽ duyệt qua từng hàng trong dataframe và kiểm tra xem tên sản phẩm hoặc ID sản phẩm
        có xuất hiện trong câu hỏi hay không. Nếu có, thông tin về sản phẩm sẽ được thêm vào kết quả.
        Args:
            question (str): Câu hỏi chứa thông tin cần kiểm tra.
            dataframe (pd.DataFrame): DataFrame chứa dữ liệu sản phẩm.
        Returns:
            str: Chuỗi chứa thông tin về các sản phẩm phù hợp với câu hỏi.
        
        """
        
        result = ""
        try: 
            for index, row in dataframe.iterrows():
                if any(str(item).lower() in question.lower() for item in (row['product_name'], row['product_code'])):
                    result += f"Name: {row['product_name']} - ID: {row['product_code']} - Price: {row['lifecare_price']}\n"
            return result
        except Exception as e:
            logging.error("DOUBLE CHECK ERROR: " + str(e))
            return result