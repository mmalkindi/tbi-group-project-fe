from django.shortcuts import render, redirect
from django.urls import reverse
from django.http import JsonResponse
from elasticsearch import Elasticsearch
import environ

# Setup environment variables
env = environ.Env()
environ.Env.read_env()
search_host = env("SEARCH_HOST")

# Make sure this header matches your server version if you're using ES 8+
es = Elasticsearch(
    search_host,
    headers={
        "Accept": "application/vnd.elasticsearch+json; compatible-with=8",
        "Content-Type": "application/vnd.elasticsearch+json; compatible-with=8"
    }
)
# Helper function to save recent searches in session
def save_recent_search(request, query, max_items=5):
    recent_searches = request.session.get("recent_searches", [])
    if query:
        if query not in recent_searches:
            recent_searches.insert(0, query)
            recent_searches = recent_searches[:max_items]
            request.session["recent_searches"] = recent_searches
        else:
            recent_searches.remove(query)
            recent_searches.insert(0, query)
            request.session["recent_searches"] = recent_searches
    return recent_searches

# Create your views here.
def index(request):
    ''' Menampilkan halaman utama '''
    query = request.GET.get("q")
    recent_searches = request.session.get("recent_searches", [])

    if query != None:
        return redirect(reverse("search") + "?q=" + query)

    context = {
        'page_title': "homepage",
        'recent_searches': recent_searches
    }
    return render(request, "index.html", context)

def search(request):
    ''' Menampilkan hasil pencarian '''
    query = request.GET.get("q", "").strip()
    recent_searches = []
    results = []

    if query:
        recent_searches = save_recent_search(request, query)
        try:
            response = es.search(
                index="airports",
                query={
                    "multi_match": {
                        "query": query,
                        "fields": ["name", "iata_code", "iso_country"]
                    }
                }
            )
            results = [hit["_source"] for hit in response["hits"]["hits"]]
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

    context = {
            'page_title': "Search results for \"" + request.GET.get("q") + "\"",
            'search_results': results,
            'recent_searches': recent_searches,
        }
    response = render(request, 'search_results.html', context)
    return response