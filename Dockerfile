FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Cài đặt curl và PostgreSQL client để kiểm tra kết nối
RUN apt-get update && apt-get install -y curl postgresql-client && apt-get clean

COPY . .

# Tạo thư mục logs nếu chưa có
RUN mkdir -p logs/bash

# Cấp quyền thực thi cho script khởi động
COPY init_elasticsearch.sh /app/
RUN chmod +x /app/init_elasticsearch.sh

# Expose cổng mà ứng dụng sẽ chạy
EXPOSE 7878

# Sử dụng script khởi động làm entrypoint
ENTRYPOINT ["/app/init_elasticsearch.sh"]

# Chạy ứng dụng
CMD ["python", "run_api_zalo.py"] 