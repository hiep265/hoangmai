#!/bin/bash

echo "Waiting for Elasticsearch to start..."
sleep 10

# Kiểm tra kết nối đến Elasticsearch
echo "Checking connection to Elasticsearch..."
until curl -s http://elasticsearch:9200 > /dev/null; do
    echo "Elasticsearch is not ready yet. Waiting..."
    sleep 5
done

echo "Elasticsearch is ready. Loading data..."

# Chạy script Python để tải dữ liệu
python /app/load_data_to_elasticsearch.py

echo "Waiting for PostgreSQL to start..."

# Kiểm tra kết nối đến PostgreSQL
echo "Checking connection to PostgreSQL..."
until PGPASSWORD=20032003 psql -h postgres -U postgres -d chatbot_hm -c "SELECT 1" > /dev/null 2>&1; do
    echo "PostgreSQL is not ready yet. Waiting..."
    sleep 5
done

echo "PostgreSQL is ready."
echo "All services are ready. Starting application..."

# Khởi động ứng dụng chính
exec "$@" 