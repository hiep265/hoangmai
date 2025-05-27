import os
import time
import logging
import pandas as pd
import re
from datetime import datetime
from typing import Dict, Any, List
from langchain_core.globals import set_llm_cache
from langchain_core.prompts import PromptTemplate
from langchain_core.caches import InMemoryCache
from source.model.loader import ModelLoader
from langchain_community.callbacks.manager import get_openai_callback
from source.router.router import decision_search_type
from source.retriever.elastic import ElasticQueryEngine
from source.retriever.extract_specifications import extract_info
from source.prompt.template import PROMPT_HISTORY, PROMPT_HEADER, PROMPT_CHATCHIT, PROMPT_ORDER, PROMPT_HELLO
from utils import GradeReWrite, UserHelper, timing_decorator, PostgreHandler, HelperPiline
from configs.config_system import LoadConfig

cache = InMemoryCache()
set_llm_cache(cache)

class Pipeline:
    def __init__(self, member_code: str):
        self.member_code = member_code
        self.llm_rag = ModelLoader.load_rag_model()
        self.llm_chatchit = ModelLoader.load_chatchit_model()
        self.els_seacher = ElasticQueryEngine(member_code=self.member_code)
        self.user_helper =  UserHelper()  
        self.pipeline_helper = HelperPiline()  
        self.db_logger = PostgreHandler()   
        self.user_info = None
        
    def _execute_llm_call(self, llm, prompt, structured_output=None):
        with get_openai_callback() as cb:
            if structured_output:
                llm_with_output = llm.with_structured_output(structured_output)
                response = llm_with_output.invoke(prompt).rewrite 
            else:
                response = llm.invoke(prompt)
            return {
                "content": response.content if hasattr(response, 'content') else response,
                "total_token": cb.total_tokens,
                'total_cost': cb.total_cost
            }    
    
    def _rewrite_query(self, query: str, history: list) -> Dict[str, Any]:
        try:
            return self._execute_llm_call(
                self.llm_rag, 
                PROMPT_HISTORY.format(question=query, chat_history=history),
                GradeReWrite
            )
        except Exception as e :
            logging.error("REWRITE QUERY ERROR: " + str(e))
            response = {"content": LoadConfig.SYSTEM_MESSAGE['error_system'], 
                        "total_token": 0, 'total_cost': 0,
                        "status": 500, 
                        "message": f"QUERY REWRITE ERR: {str(e)}"}
            return response 

    def _handle_order_query(self, query: str) -> Dict[str, Any]:
        try:
            all_product_data = pd.read_excel(LoadConfig.ALL_PRODUCT_FILE_MERGED_STORAGE.format(member_code=self.member_code))
            original_product_info = self.pipeline_helper._double_check(question=query, dataframe=all_product_data)
            prompt = PromptTemplate(input_variables=['question', 'user_info', 'original_product_info'], template=PROMPT_ORDER)
            response =  self._execute_llm_call(self.llm_rag, prompt.format(question=query, 
                                                                           user_info=self.user_info, 
                                                                           original_product_info = original_product_info))
            response['content'] = response['content']
            
            response['products'] = self.pipeline_helper._product_seeking(output_from_llm=response['content'], 
                                                                         query_rewritten=query, 
                                                                         dataframe=all_product_data)
            response['product_confirms'] = self.pipeline_helper._product_confirms(output_from_llm=response['content'], 
                                                                                  query_rewritten=query, 
                                                                                  dataframe=all_product_data)
                
        except Exception as e:
            response = {"content": LoadConfig.SYSTEM_MESSAGE['error_system'], 
                        "total_token": 0, 'total_cost': 0,
                        "status": 500, 
                        "message": f"Error processing request: {str(e)}"}
            logging.error("ORDER QUERY ERROR: " + str(e))
        return response

    def _clean_markdown(self, text: str) -> str:
        text = re.sub(r'(\*\*|__)(.*?)\1', r'\2', text)  # bold
        text = re.sub(r'(\*|_)(.*?)\1', r'\2', text)     # italic
        text = re.sub(r'`{1,3}.*?`{1,3}', '', text)      # inline code
        text = re.sub(r'#{1,6}\s*', '', text)            # headings
        text = re.sub(r'>\s?', '', text)                 # blockquote
        text = re.sub(r'\.\.\.+', '.', text)             # ...
        text = re.sub(r'-{3,}', '', text)                # ---
        text = re.sub(r'\n{2,}', '\n', text)             # blank lines
        return text.strip()


    def _is_greeting_or_farewell(self, query: str) -> bool:
        greetings = ['xin chào', 'chào', 'hi', 'hello']
        farewells = ['tạm biệt', 'bye']
        thanks = ['cảm ơn', 'thank you', 'thanks']

        query_lower = query.lower()
        for phrase in greetings + farewells + thanks:
            if phrase in query_lower:
                return True
        return False

    def _handle_text_query(self, query: str) -> Dict[str, Any]:
        try:
            if self._is_greeting_or_farewell(query):
                prompt = PromptTemplate(
                    input_variables=['question', 'user_info'],
                    template=PROMPT_HELLO
                )
            else:
                prompt = PromptTemplate(
                    input_variables=['question', 'user_info'],
                    template=PROMPT_CHATCHIT
                )

            response = self._execute_llm_call(
                self.llm_rag,
                prompt.format(
                    question=query,
                    user_info=self.user_info
                )
            )

            # ===== Clean markdown formatting =====
            content = response['content']
            response['content'] = self._clean_markdown(content)
            return response

        except Exception as e:
            response = {
                "content": LoadConfig.SYSTEM_MESSAGE['error_system'],
                "total_token": 0,
                "total_cost": 0,
                "status": 500,
                "message": f"Error processing request: {str(e)}"
            }
            logging.error("TEXT QUERY ERROR: " + str(e))

        return response

    def _handle_elastic_search(self, query: str, history: list) -> Dict[str, Any]:
        try:
            demands = extract_info(query)
            response_elastic, products_info = self.els_seacher.search_db(demands)
            
            if not response_elastic:
                response = self._handle_text_query(query=query)
                return response

            prompt = PromptTemplate(
                input_variables=['context', 'question', 'user_info', 'chat_history'],
                template=PROMPT_HEADER
            )
            response = self._execute_llm_call(
                self.llm_rag,
                prompt.format(
                    context=response_elastic, 
                    question=query, 
                    user_info=self.user_info,
                    chat_history=history
                )
            )

            # ===== Clean markdown formatting =====
            content = response['content']
            content = self._clean_markdown(content)

            response['product_name'] = demands['object']
            response['content'] = content
            response['products'] = self.pipeline_helper._product_seeking(
                output_from_llm=content,
                query_rewritten=query,
                dataframe=pd.DataFrame(products_info)
            )

        except Exception as e:
            response = {
                "content": LoadConfig.SYSTEM_MESSAGE['error_system'], 
                "total_token": 0,
                "total_cost": 0,
                "status": 500, 
                "message": f"Error processing request: {str(e)}"
            }
            logging.error("ELASTIC SEARCH QUERY ERROR: " + str(e))

        return response


    # Main function
    @timing_decorator
    def chat_session(
        self,
        InputText = None,
        IdRequest = None,
        NameBot = None,
        UserInfor = None,
    ):
    
        self.user_helper.save_users(UserInfor)
        self.user_info = self.user_helper.get_user_info(UserInfor['phone_number'])

        storage_info_output = {
            "product_name": None,
            "products": [], 
            "product_confirms": [],
            "terms": [], 
            "content": "", 
            "total_token": 0, 
            'total_cost': 0,
            "status": 200, 
            "message": None, 
            "time_processing": None,
        }
        time_in = time.time()
        try:
            history_conversation = self.user_helper.load_conversation(conv_user=UserInfor['phone_number'], id_request=IdRequest)
            # print("HISRORY", history_conversation)
            result_rewriten = self._rewrite_query(query=InputText, history=history_conversation)
            query_rewritten = result_rewriten['content']
            print("QUERY REWRITE:", query_rewritten)
            storage_info_output['total_token'] += result_rewriten['total_token']
            storage_info_output['total_cost'] += result_rewriten['total_cost']

            result_type = decision_search_type(result_rewriten['content'])
            search_type = result_type['content']
            print("TYPE SEARCH:", search_type)
            storage_info_output['total_token'] += result_type['total_token']
            storage_info_output['total_cost'] += result_type['total_cost']

            if "ORDER" in search_type:
                results = self._handle_order_query(query_rewritten)
            elif "TEXT" in search_type:
                results = self._handle_text_query(query_rewritten)
            else: 
                results = self._handle_elastic_search(query_rewritten, history=history_conversation)

            storage_info_output.update({
                'product_name': results.get("product_name", None),
                'product_confirms': results.get('product_confirms', []),
                'content': results['content'],
                'total_token': storage_info_output['total_token'] + results['total_token'],
                'total_cost': storage_info_output['total_cost'] + results['total_cost'],
                'products': results.get('products', []),
                'message': "Request processed successfully."
            })
            # print(storage_info_output['content'])
            self.user_helper.save_conversation(phone_number=UserInfor['phone_number'], query=InputText, id_request=IdRequest, response=results['content'])
        
        except Exception as e:
            storage_info_output.update({"content": LoadConfig.SYSTEM_MESSAGE['error_system'],
                                        "status": 500, 
                                        "message": f"Error processing request in func CHAT SESSION: {str(e)}"})
            logging.error("CHAT SESSION ERROR: " + str(e))
            
        storage_info_output['time_processing'] = time.time() - time_in
        
        # Save log to database
        try:
            self.db_logger.insert_data(
                user_name=UserInfor['name'],
                phone_number=UserInfor['phone_number'],
                object_product=storage_info_output['product_name'],
                name_bot=NameBot,
                rewritten_human=query_rewritten,
                session_id=IdRequest,
                human=InputText,
                ai=storage_info_output['content'],
                status=storage_info_output['status'],
                total_token=storage_info_output['total_token'],
                total_cost=storage_info_output['total_cost'],
                date_request=datetime.now().strftime("%A, %d %B %Y, %H:%M:%S"),
                error_message=storage_info_output['message'],
                time_request=storage_info_output['time_processing']
            )
        except Exception as e:
            logging.error("ERROR WHILE INSERT TO DATABSE: " + str(e))
            
        return storage_info_output

if __name__ == "__main__":
    pass