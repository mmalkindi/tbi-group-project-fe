from django.shortcuts import render, redirect
from django.urls import reverse
import environ
from django.http import JsonResponse
from .util import get_elasticsearch_client
import logging

# Setup environment variables
env = environ.Env()
environ.Env.read_env()
search_host = env("SEARCH_HOST", default="http://localhost:9200")
logger = logging.getLogger(__name__)
# Create your views here.
def index(request):
    ''' Menampilkan halaman utama '''
    query = request.GET.get("q")

    if query != None:
        return redirect(reverse("search") + "?q=" + query)

    context = {
        'page_title': "homepage",
    }
    return render(request, "index.html", context)

def test_es_connection(request):
    '''Test Elasticsearch connection and return info'''
    es_client = get_elasticsearch_client()
    
    if es_client is not None and es_client.ping():
        # Connection successful, get cluster info
        info = es_client.info()
        cluster_health = es_client.cluster.health()
        
        # Get indices if any exist
        try:
            indices = list(es_client.indices.get(index='*').keys())
        except Exception as e:
            indices = []
            logger.error(f"Error getting indices: {str(e)}")
            
        return JsonResponse({
            'status': 'connected',
            'cluster_name': info.get('cluster_name'),
            'elasticsearch_version': info.get('version', {}).get('number'),
            'cluster_health': cluster_health,
            'indices': indices,
        })
    else:
        # Connection failed
        return JsonResponse({
            'status': 'error',
            'message': 'Failed to connect to Elasticsearch',
            'host': search_host
        }, status=200)  # Changed from 500 to avoid server error