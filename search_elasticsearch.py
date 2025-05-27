import os
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

# Kiểm tra số lượng documents trong index
count = client.count(index=index_name)["count"]
print(f"Total documents in index: {count}")

# Tìm kiếm các nhóm sản phẩm
print("\nSearch for product groups:")
query = {
    "size": 0,
    "aggs": {
        "group_names": {
            "terms": {
                "field": "group_product_name.keyword",
                "size": 50
            }
        }
    }
}

try:
    result = client.search(index=index_name, body=query)
    for bucket in result["aggregations"]["group_names"]["buckets"]:
        print(f"- {bucket['key']} ({bucket['doc_count']} products)")
except Exception as e:
    print(f"Error searching for product groups: {str(e)}")

# Tìm kiếm máy hàn
print("\nSearch for 'máy hàn':")
query = {
    "query": {
        "bool": {
            "should": [
                {"match": {"group_name": "máy hàn"}},
                {"match": {"product_name": "máy hàn"}},
                {"match": {"group_product_name": "máy hàn"}}
            ]
        }
    }
}

try:
    result = client.search(index=index_name, body=query)
    print(f"Found {result['hits']['total']['value']} results")
    
    for hit in result["hits"]["hits"]:
        source = hit["_source"]
        print(f"- {source.get('product_name')} (Group: {source.get('group_product_name')}, Group Name: {source.get('group_name')})")
except Exception as e:
    print(f"Error searching for 'máy hàn': {str(e)}")

# Tìm kiếm theo group_product_name = 'máy hàn & pk'
print("\nSearch for group_product_name = 'máy hàn & pk':")
query = {
    "query": {
        "match_phrase": {
            "group_product_name": "máy hàn & pk"
        }
    }
}

try:
    result = client.search(index=index_name, body=query)
    print(f"Found {result['hits']['total']['value']} results")
    
    for hit in result["hits"]["hits"]:
        source = hit["_source"]
        print(f"- {source.get('product_name')} (Group: {source.get('group_product_name')}, Group Name: {source.get('group_name')})")
except Exception as e:
    print(f"Error searching for group_product_name = 'máy hàn & pk': {str(e)}")

# Tìm kiếm theo group_name = 'máy hàn'
print("\nSearch for group_name = 'máy hàn':")
query = {
    "query": {
        "match_phrase": {
            "group_name": "máy hàn"
        }
    }
}

try:
    result = client.search(index=index_name, body=query)
    print(f"Found {result['hits']['total']['value']} results")
    
    for hit in result["hits"]["hits"]:
        source = hit["_source"]
        print(f"- {source.get('product_name')} (Group: {source.get('group_product_name')}, Group Name: {source.get('group_name')})")
except Exception as e:
    print(f"Error searching for group_name = 'máy hàn': {str(e)}") 