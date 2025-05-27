import os
import pandas as pd
from elasticsearch import Elasticsearch

# Kết nối đến Elasticsearch
elastic_host = os.getenv("ELASTIC_HOST", "http://elasticsearch:9200")
print(f"Connecting to Elasticsearch at {elastic_host}")

client = Elasticsearch(
    hosts=[elastic_host],
    timeout=30
)

# Kiểm tra kết nối
if client.ping():
    print("Successfully connected to Elasticsearch")
else:
    print("Failed to connect to Elasticsearch")
    exit(1)

# Tên index
index_name = "normal"

# Kiểm tra nếu index đã tồn tại thì xóa đi
if client.indices.exists(index=index_name):
    print(f"Deleting existing index {index_name}")
    client.indices.delete(index=index_name)

# Define the mappings
mappings = {
    "properties": {
        "product_code": { "type":"text"},
        "product_name": {"type": "text"},
        "group_product_name": {"type": "text"},
        "lifecare_price": {"type": "float"},
        "trademark": {"type": "text"},
        "inventory": {"type": "integer"},
        "specifications": {"type": "text"},
        "avatar_images": {"type" : "text"},
        "link_product" : {"type" : "text"},
        "group_name": {"type": "text"},
    }
}

# Tạo index mới với mappings
print(f"Creating new index {index_name}")
client.indices.create(index=index_name, body={"mappings": mappings})

# Đọc dữ liệu từ file Excel
print("Reading data from Excel file")
df = pd.read_excel('/app/data/data_private/data_member/data_final_NORMAL_merged.xlsx')
print(f"Read {len(df)} records from Excel file")

# Làm sạch dữ liệu
df = df.fillna({
    "product_code": "",
    "product_name": "",
    "lifecare_price": 0.0,
    "group_product_name": "",
    "trademark": "",
    "inventory": 0,
    "specifications": "",
    "avatar_images": "",
    "link_product": "",
    "group_name": ""
})

df["lifecare_price"] = df["lifecare_price"].astype(float)
df["inventory"] = df["inventory"].astype(int)

# Index documents
print("Indexing documents to Elasticsearch")
for i, row in df.iterrows():
    doc = {
        "product_code": row["product_code"],
        "product_name": row["product_name"],
        "group_product_name": row["group_product_name"],
        "lifecare_price": row["lifecare_price"],
        "trademark": row["trademark"],
        "inventory": row["inventory"],
        "specifications": row["specifications"],
        "avatar_images": row["avatar_images"],
        "link_product": row["link_product"],
        "group_name": row["group_name"],
    }
    client.index(index=index_name, id=i, document=doc)
    
    # In tiến trình
    if i % 100 == 0:
        print(f"Indexed {i}/{len(df)} documents")

# Refresh index
client.indices.refresh(index=index_name)

# Kiểm tra số lượng documents trong index
count = client.count(index=index_name)["count"]
print(f"Total documents indexed: {count}")

print("Data loading completed successfully!") 