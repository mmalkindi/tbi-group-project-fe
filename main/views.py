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

def search(request):
    ''' Menampilkan hasil pencarian '''
    query = request.GET.get("q", "").strip()
    results = []

    if query:
        try:
            response = es.search(
                index="airports",
                query={
                    "multi_match": {
                        "query": query,
                        "fields": ["name", "name_ngrams", "iata_code", "iso_country"],
                        "fuzziness": "AUTO"
                    }
                }
            )
            results = [hit["_source"] for hit in response["hits"]["hits"]]
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

    context = {
        'page_title': f"Search results for \"{query}\"",
        'search_results': results,
    }
    response = render(request, 'search_results.html', context)
    return response