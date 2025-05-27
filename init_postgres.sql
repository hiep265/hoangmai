-- Tạo schema nếu chưa tồn tại
CREATE SCHEMA IF NOT EXISTS chatbot_mobile;

-- Tạo bảng log_chatbot nếu chưa tồn tại
CREATE TABLE IF NOT EXISTS chatbot_mobile.log_chatbot (
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
);

-- Thêm chỉ mục để tăng tốc độ truy vấn
CREATE INDEX IF NOT EXISTS idx_phone_number ON chatbot_mobile.log_chatbot(phone_number);
CREATE INDEX IF NOT EXISTS idx_session_id ON chatbot_mobile.log_chatbot(session_id);
CREATE INDEX IF NOT EXISTS idx_date_request ON chatbot_mobile.log_chatbot(date_request); 