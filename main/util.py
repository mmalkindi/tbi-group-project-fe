from elasticsearch import Elasticsearch
import environ
import logging

env = environ.Env()
environ.Env.read_env()

logger = logging.getLogger(__name__)

def get_elasticsearch_client():
    """
    Creates and returns an Elasticsearch client instance
    """
    try:
        # Get Elasticsearch connection details from environment variables
        elasticsearch_host = env("SEARCH_HOST", default="http://localhost:9200")
        
        # Create Elasticsearch client with verify_certs=False for testing
        es_client = Elasticsearch(elasticsearch_host, verify_certs=False, retry_on_timeout=True, request_timeout=30)
        
        # Test connection
        if es_client.ping():
            logger.info("Connected to Elasticsearch")
            return es_client
        else:
            logger.error("Could not connect to Elasticsearch")
            return None
    except Exception as e:
        logger.error(f"Error connecting to Elasticsearch: {str(e)}")
        return None