import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import gradio as gr
import re
import threading
import time
import os
import schedule
from datetime import datetime
from collections import Counter
import logging
import tempfile
from utils.postgre_logger import PostgreHandler

global df1
def upload_sales_force_data():
    global df1
    postgres_handler = PostgreHandler()
    postgres_handler.create_table()
    df1 = postgres_handler.get_logging()
    postgres_handler.connector.close()

    if not df1.empty:
        df1['date_request'] = pd.to_datetime(df1['date_request'])
    else:
        logging.warning("No data fetched for HM Mobile Bot.")
        df1 = pd.DataFrame(
            columns=[
                'date_request', 'user_name', 'total_cost', 'total_token', 
                'human', 'object_product'
            ]
        )

# Hàm tạo biểu đồ 
def create_sales_force_chart(monthly_data):
    fig, ax = plt.subplots(figsize=(10, 6))
    width = 0.25
    x = range(len(monthly_data['Month']))

    bars1 = ax.bar([i - width for i in x], monthly_data['Requests/month'], width, label='Requests/month', color='blue', alpha=0.7)
    bars2 = ax.bar(x, monthly_data['Sessions/month'], width, label='Sessions/month', color='red', alpha=0.7)
    bars3 = ax.bar([i + width for i in x], monthly_data['Users/month'], width, label='Users/month', color='orange', alpha=0.7)

    for bars in [bars1, bars2, bars3]:
        for bar in bars:
            ax.text(
                bar.get_x() + bar.get_width() / 2,
                bar.get_height(),
                f'{int(bar.get_height())}',
                ha='center', va='bottom', fontsize=8
            )

    ax.set_title('HM Mobile Monthly Data')
    ax.set_xlabel('Month')
    ax.set_ylabel('Count')
    ax.set_xticks(x)
    ax.set_xticklabels(monthly_data['Month'], rotation=45)
    ax.legend()
    plt.tight_layout()

    # Lưu file vào thư mục tạm hệ thống
    chart_path = os.path.join(tempfile.gettempdir(), "sales_force_chart.png")
    plt.savefig(chart_path, format='png')
    plt.close(fig)
    return chart_path

# HÀm tạo biểu đồ xem sản phẩm bán chạy
def create_product_popularity_chart(df):
    if df.empty or 'object_product' not in df.columns:
        return None

    product_counts = df['object_product'].dropna().value_counts().head(15)  # top 15 sản phẩm
    fig, ax = plt.subplots(figsize=(10, 6))
    product_counts.plot(kind='bar', ax=ax, color='green', alpha=0.8)

    ax.set_title('Top 15 Sản phẩm được tìm kiếm nhiều nhất')
    ax.set_xlabel('Sản phẩm')
    ax.set_ylabel('Số lượt tìm kiếm')
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()

    chart_path = os.path.join(tempfile.gettempdir(), "product_popularity_chart.png")
    plt.savefig(chart_path, format='png')
    plt.close(fig)
    return chart_path

# Hàm tạo biểu đồ xem khách hàng tiềm năng
def create_top_customers_chart(df):
    if df.empty or 'user_name' not in df.columns or 'session_id' not in df.columns or 'phone_number' not in df.columns:
        return None

    # Ghép tên người dùng + số điện thoại thành 1 cột mới
    df['user_identity'] = df['user_name'].astype(str) + " (" + df['phone_number'].astype(str) + ")"

    # Đếm số lượng session_id duy nhất theo user_identity
    customer_sessions = df.groupby('user_identity')['session_id'].nunique()
    top_customers = customer_sessions.sort_values(ascending=False).head(5)

    # Vẽ biểu đồ
    fig, ax = plt.subplots(figsize=(8, 5))
    top_customers.plot(kind='bar', ax=ax, color='purple', alpha=0.8)

    ax.set_title('Top 5 Khách hàng tiềm năng')
    ax.set_xlabel('Người dùng (Tên + SĐT)')
    ax.set_ylabel('Số phiên trò chuyện')
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()

    chart_path = os.path.join(tempfile.gettempdir(), "top_customers_chart.png")
    plt.savefig(chart_path, format='png')
    plt.close(fig)
    return chart_path

def fetch_sales_force_data():
    postgres_handler = PostgreHandler()

    weekly_query = """
    WITH weekly_data AS (
        SELECT
            DATE_TRUNC('week', date_request::date) AS week,
            COUNT(DISTINCT user_name) AS unique_user_count,
            COUNT(DISTINCT session_id) AS unique_session_count,
            COUNT(*) AS request_count
        FROM
            chatbot_mobile.log_chatbot
        GROUP BY
            DATE_TRUNC('week', date_request::date)
    )
    SELECT
        week :: DATE,
        request_count AS "Requests/week",
        unique_session_count AS "Sessions/week",
        unique_user_count AS "Users/week"
    FROM 
        weekly_data
    ORDER BY 
        week;
    """

    monthly_query = """
    WITH monthly_data AS (
        SELECT
            DATE_TRUNC('month', date_request::date) AS month,
            COUNT(DISTINCT user_name) AS unique_user_count,
            COUNT(DISTINCT session_id) AS unique_session_count,
            COUNT(*) AS request_count
        FROM
            chatbot_mobile.log_chatbot
        GROUP BY
            DATE_TRUNC('month', date_request::date)
    )
    SELECT
        TO_CHAR(month, 'yyyy-MM') as month,
        request_count AS "Requests/month",
        unique_session_count AS "Sessions/month",
        unique_user_count AS "Users/month"
    FROM 
        monthly_data
    ORDER BY 
        month;
    """

    weekly_data = postgres_handler.execute_query(weekly_query)
    monthly_data = postgres_handler.execute_query(monthly_query)
    return pd.DataFrame(weekly_data, columns=["Week", "Requests/week", "Sessions/week", "Users/week"]), \
           pd.DataFrame(monthly_data, columns=["Month", "Requests/month", "Sessions/month", "Users/month"])

# Giao diện Gradio
def gradio_interface():
    def update_sales_force_data():
        weekly_data, monthly_data = fetch_sales_force_data()
        chart_path = create_sales_force_chart(monthly_data)
        product_chart_path = create_product_popularity_chart(df1)
        customer_chart_path = create_top_customers_chart(df1)  # THÊM DÒNG NÀY
        return weekly_data, monthly_data, chart_path, product_chart_path, customer_chart_path



    with gr.Blocks() as demo:
        with gr.Tab("Hoang Mai Mobile"):
            gr.Markdown("### HM Mobile Dashboard")
            sf_weekly_table = gr.DataFrame(label="Weekly Data")
            sf_monthly_table = gr.DataFrame(label="Monthly Data")
            sf_chart = gr.Image(type="filepath", label="Monthly Chart")
            sf_product_chart = gr.Image(type="filepath", label="Top Sản phẩm được tìm kiếm")
            sf_top_customers_chart = gr.Image(type="filepath", label="Khách hàng tiềm năng")  # THÊM DÒNG NÀY

            sf_update_button = gr.Button("Update HM Mobile Bot Data")
            sf_update_button.click(
                update_sales_force_data,
                outputs=[sf_weekly_table, sf_monthly_table, sf_chart, sf_product_chart, sf_top_customers_chart]  # THÊM DÒNG NÀY
            )

    return demo

# Lập lịch tải dữ liệu định kỳ
def schedule_task():
    schedule.every(5).minutes.do(upload_sales_force_data)
    while True:
        schedule.run_pending()
        time.sleep(1)

if __name__ == "__main__":
    upload_sales_force_data()
    threading.Thread(target=schedule_task).start()
    interface = gradio_interface()
    interface.launch()
