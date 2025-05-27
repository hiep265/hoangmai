from elasticsearch import Elasticsearch
import os

def check_connection(client: Elasticsearch):
    try:
        info = client.info()
        print("✅ Connected to Elasticsearch:", info['cluster_name'])
    except Exception as e:
        print("❌ Connection failed:", e)

if __name__ == "__main__":
    elastic_host = os.getenv("ELASTIC_HOST", "http://localhost:9200")
    client = Elasticsearch(hosts=[elastic_host])

    check_connection(client)
