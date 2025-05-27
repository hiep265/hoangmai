# Chatbot HM Mobile

## Khắc phục lỗi kết nối Elasticsearch

Trong quá trình triển khai, có thể gặp lỗi kết nối giữa ứng dụng và Elasticsearch. Dưới đây là các bước đã thực hiện để khắc phục:

1. **Vấn đề**: Ứng dụng không thể kết nối đến Elasticsearch do cấu hình bảo mật mặc định của Elasticsearch 8.x.

2. **Giải pháp**: Vô hiệu hóa bảo mật trong môi trường phát triển bằng cách thêm các biến môi trường trong `docker-compose.yml`:
   ```yaml
   elasticsearch:
     environment:
       - discovery.type=single-node
       - ES_JAVA_OPTS=-Xms512m -Xmx512m
       - xpack.security.enabled=false
       - xpack.security.http.ssl.enabled=false
       - xpack.security.transport.ssl.enabled=false
   ```

3. **Cấu hình kết nối**: Đảm bảo ứng dụng sử dụng URL kết nối đúng:
   ```yaml
   hmmobile_bot:
     environment:
       - ELASTIC_HOST=http://elasticsearch:9200
   ```

4. **Kiểm tra kết nối**: Có thể kiểm tra kết nối bằng cách chạy script:
   ```python
   import os
   from elasticsearch import Elasticsearch
   
   elastic_host = os.getenv("ELASTIC_HOST", "http://elasticsearch:9200")
   client = Elasticsearch(hosts=[elastic_host], timeout=30)
   print("Connected:", client.ping())
   ```

## Tải dữ liệu vào Elasticsearch

Để đảm bảo dữ liệu được tải vào Elasticsearch, chúng ta đã thực hiện các bước sau:

1. **Tạo script tải dữ liệu**: File `load_data_to_elasticsearch.py` đọc dữ liệu từ file Excel và tải vào Elasticsearch.

2. **Kết quả**: Sau khi chạy script, 2467 sản phẩm đã được tải thành công vào Elasticsearch.

3. **Tự động hóa**: Để tự động tải dữ liệu khi khởi động container, chúng ta đã thêm script `init_elasticsearch.sh` và cập nhật Dockerfile để sử dụng script này làm entrypoint.

4. **Kiểm tra**: Sau khi tải dữ liệu, chúng ta đã kiểm tra và xác nhận rằng API có thể trả về kết quả tìm kiếm chính xác cho các sản phẩm.

## Cấu hình PostgreSQL

Để lưu trữ logs và dữ liệu người dùng, chúng ta đã thêm PostgreSQL vào hệ thống:

1. **Cấu hình trong docker-compose.yml**:
   ```yaml
   postgres:
     image: postgres:15
     container_name: postgres-db
     ports:
       - "5432:5432"
     environment:
       POSTGRES_DB: chatbot_hm
       POSTGRES_USER: postgres
       POSTGRES_PASSWORD: 20032003
     volumes:
       - pgdata:/var/lib/postgresql/data
       - ./init_postgres.sql:/docker-entrypoint-initdb.d/init_postgres.sql
   ```

2. **Khởi tạo cơ sở dữ liệu**: File `init_postgres.sql` tự động tạo schema và bảng cần thiết khi container khởi động.

3. **Kết nối từ ứng dụng**: Cập nhật biến môi trường cho container hmmobile_bot:
   ```yaml
   hmmobile_bot:
     environment:
       - POSTGRES_HOST=postgres
       - POSTGRES_DB_NAME=chatbot_hm
       - POSTGRES_PASSWORD=20032003
       - POSTGRES_USER=postgres
       - POSTGRES_PORT=5432
   ```

4. **Kiểm tra kết nối**: Script khởi động `init_elasticsearch.sh` đảm bảo cả Elasticsearch và PostgreSQL đều sẵn sàng trước khi khởi động ứng dụng.

## Sử dụng API

API endpoint chính: `/chatbot_proactive`

Ví dụ gọi API bằng Python:
```python
import requests

url = "http://localhost:7878/chatbot_proactive"
data = {
    "idRequest": "123",
    "nameBot": "hmmobile_bot",
    "phoneNumber": "0123456789",
    "userName": "test_user",
    "inputText": "Tôi muốn xem máy hàn"
}

response = requests.post(url, data=data)
print(f"Status Code: {response.status_code}")
print(f"Response: {response.text}")
```