import logging
import datetime
import os

def set_logging_error():
    logger = logging.getLogger("error")
    logger.setLevel(logging.DEBUG)

    # Tạo thư mục logs/error nếu chưa tồn tại
    folder_path = os.path.join("logs", "error")
    os.makedirs(folder_path, exist_ok=True)
    
    # Đặt tên tệp log theo ngày tháng hiện tại
    today = datetime.date.today()
    log_filename = today.strftime('%Y-%m-%d') + '-log_error.txt'  # Định dạng: YYYY-MM-DD.log

    # Cấu hình FileHandler với encoding utf-8 để tránh lỗi mã hóa
    file_handler = logging.FileHandler(os.path.join(folder_path, log_filename), mode='a', encoding='utf-8')  # Chỉ định encoding
    formatter = logging.Formatter('%(asctime)s - %(levelname)s: %(message)s')
    file_handler.setFormatter(formatter)
    
    # Thêm handler vào logger
    logger.addHandler(file_handler)

def set_logging_postgres():
    logger = logging.getLogger("terminal")
    logger.setLevel(logging.DEBUG)

    # Tạo thư mục logs/Postgres nếu chưa tồn tại
    folder_path = os.path.join("logs", "Postgres")
    os.makedirs(folder_path, exist_ok=True)
    
    # Đặt tên tệp log theo ngày tháng hiện tại
    today = datetime.date.today()
    log_filename = today.strftime('%Y-%m-%d') + '-log_info_postgres.txt'  # Định dạng: YYYY-MM-DD.log

    # Cấu hình FileHandler với encoding utf-8
    file_handler = logging.FileHandler(os.path.join(folder_path, log_filename), mode='a', encoding='utf-8')  # Chỉ định encoding
    formatter = logging.Formatter('%(asctime)s - %(levelname)s: %(message)s')
    file_handler.setFormatter(formatter)
    
    # Thêm handler vào logger
    logger.addHandler(file_handler)

    return logger

def set_logging_time():
    logger = logging.getLogger("time")
    logger.setLevel(logging.DEBUG)

    # Tạo thư mục logs/times nếu chưa tồn tại
    folder_path = os.path.join("logs", "times")
    os.makedirs(folder_path, exist_ok=True)
    
    # Đặt tên tệp log theo ngày tháng hiện tại
    today = datetime.date.today()
    log_filename = today.strftime('%Y-%m-%d') + '-processed_times.txt'  # Định dạng: YYYY-MM-DD.log

    # Cấu hình FileHandler với encoding utf-8
    file_handler = logging.FileHandler(os.path.join(folder_path, log_filename), mode='a', encoding='utf-8')  # Chỉ định encoding
    formatter = logging.Formatter('%(asctime)s - %(levelname)s: %(message)s')
    file_handler.setFormatter(formatter)
    
    # Thêm handler vào logger
    logger.addHandler(file_handler)

    return logger