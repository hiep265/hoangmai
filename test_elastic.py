import os
from elasticsearch import Elasticsearch

# Kết nối đến Elasticsearch
elastic_host = os.getenv("ELASTIC_HOST", "http://elasticsearch:9200")
print(f"Connecting to Elasticsearch at {elastic_host}")

try:
    client = Elasticsearch(
        hosts=[elastic_host],
        timeout=30
    )
    
    # Kiểm tra kết nối
    if client.ping():
        print("Successfully connected to Elasticsearch")
        
        # Kiểm tra thông tin cluster
        info = client.info()
        print(f"Elasticsearch info: {info}")
        
        # Liệt kê các indices
        indices = client.indices.get_alias(index="*")
        print(f"Indices: {list(indices.keys())}")
    else:
        print("Failed to connect to Elasticsearch")
except Exception as e:
    print(f"Error connecting to Elasticsearch: {str(e)}") 