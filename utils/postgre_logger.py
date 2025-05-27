import pandas as pd
import logging
import psycopg2
from psycopg2 import sql
from configs.config_system import LoadConfig


class PostgreHandler:
    def __init__(self):
        self.host = LoadConfig.POSTGRES_HOST
        self.database_name = LoadConfig.POSTGRES_DB_NAME
        self.password = LoadConfig.POSTGRES_PASSWORD
        self.user = LoadConfig.POSTGRES_USER
        self.port = LoadConfig.POSTGRES_PORT
        self.max_timeout = LoadConfig.POSTGRE_TIMEOUT
        self.connector, error = self.connect_to_postgre()

        if self.connector is None:
            logging.error(f"Error: {error.upper()}")
        else:
            self.create_table()

    def connect_to_postgre(self):
        try:
            conn_string = f"""
                host={self.host} dbname={self.database_name} 
                user={self.user} password={self.password} 
                port={self.port} connect_timeout={self.max_timeout}
            """
            conn = psycopg2.connect(conn_string)
            cursor = conn.cursor()
            cursor.execute("SELECT 1")
            result = cursor.fetchone()

            if result[0] == 1:
                logging.info(f"Successful connection to PostgreSQL database {self.database_name}!")
                return conn, "Success"
            else:
                cursor.close()
                conn.close()
                return None, "Connection failed: Unable to verify connection"

        except psycopg2.OperationalError as e:
            if "timeout expired" in str(e):
                return None, f"Error: Connection timeout after {self.max_timeout} seconds"
            else:
                return None, f"Connection error: {e}"

        except Exception as e:
            return None, f"Unknown error: {e}"

    def create_table(self, table_schema: str = "chatbot_mobile", table_name: str = "log_chatbot"):
        try:
            with self.connector.cursor() as cursor:
                logging.info(f"Creating schema: {table_schema}")
                cursor.execute(sql.SQL("CREATE SCHEMA IF NOT EXISTS {}").format(
                    sql.Identifier(table_schema)
                ))

                # Kiểm tra bảng đã tồn tại
                cursor.execute(
                    """
                    SELECT EXISTS (
                        SELECT FROM information_schema.tables 
                        WHERE table_schema = %s 
                        AND table_name = %s
                    );
                    """, (table_schema, table_name)
                )

                exists = cursor.fetchone()[0]

                if exists:
                    logging.info("Table already exists in PostgreSQL")
                    return

                logging.info(f"Creating table: {table_schema}.{table_name}")
                cursor.execute(
                    sql.SQL("""
                        CREATE TABLE {}.{} (
                            id SERIAL PRIMARY KEY,
                            user_name VARCHAR(50) NOT NULL,
                            phone_number VARCHAR(20) NOT NULL,
                            session_id VARCHAR(100) NOT NULL,
                            object_product TEXT,
                            date_request TIMESTAMP,
                            total_token INT,
                            total_cost FLOAT,
                            time_request VARCHAR(255),
                            status VARCHAR(100),
                            error_message TEXT,
                            name_bot TEXT,
                            rewritten_human TEXT,
                            human TEXT,
                            ai TEXT
                        )
                    """).format(sql.Identifier(table_schema), sql.Identifier(table_name))
                )

                self.connector.commit()
                logging.info("Table created successfully in PostgreSQL")

        except Exception as e:
            logging.error(f"Error creating table: {e}")
            self.connector.rollback()

    def insert_data(self, user_name: str, phone_number: str, session_id: str, object_product: str,
                    date_request: str, total_token: int, total_cost: float, time_request: str, status: str,
                    error_message: str, name_bot: str, rewritten_human: str, human: str, ai: str):

        insert_query = '''
        INSERT INTO chatbot_mobile.log_chatbot(user_name, phone_number, session_id, object_product, 
            date_request, total_token, total_cost, time_request, status, error_message, 
            name_bot, rewritten_human, human, ai)
        VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        '''

        try:
            with self.connector.cursor() as cursor:
                cursor.execute(insert_query, (user_name, phone_number, session_id, object_product,
                                              date_request, total_token, total_cost, time_request, status, error_message,
                                              name_bot, rewritten_human, human, ai))
                self.connector.commit()
                logging.info("Data inserted successfully in PostgreSQL")
        except Exception as e:
            logging.error(f"Error inserting data to database: {e}")
            self.connector.rollback()

    def get_logging(self):
        select_query = '''
        SELECT * FROM chatbot_mobile.log_chatbot
        '''
        try:
            df = pd.read_sql_query(select_query, self.connector)
            return df
        except Exception as e:
            logging.error(f"Error reading data: {e}")
            return pd.DataFrame()

    def execute_query(self, query: str):
        try:
            cursor = self.connector.cursor()
            cursor.execute(query)
            result = cursor.fetchall()
            return result
        except Exception as e:
            logging.error(f"Error executing query: {e}")
            self.connector.rollback()
            return []
        finally:
            cursor.close()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    postgres_handle = PostgreHandler()
    if postgres_handle.connector:
        postgres_handle.connector.close()
