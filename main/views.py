from django.shortcuts import render, redirect
from django.urls import reverse
from django.http import JsonResponse
from elasticsearch import Elasticsearch
import environ
from django.views.decorators.csrf import csrf_exempt

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
@csrf_exempt
def index(request):
    ''' Menampilkan halaman utama '''
    query = request.GET.get("q")

    if query != None:
        return redirect(reverse("search") + "?q=" + query)

    context = {
        'page_title': "homepage",
    }
    return render(request, "index.html", context)

@csrf_exempt
def search(request):
    ''' Menampilkan hasil pencarian '''
    query = request.GET.get("q", "").strip()
    results = []
    summary = ""  # Initialize summary here to avoid the error
    
    if query:
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

            # Adding RAG LLM implementation
            # Add RAG functionality - generate summary if results exist
            if results:
                # Create context for LLM from search results
                context_text = f"Search results for '{query}':\n\n"
                for i, result in enumerate(results[:5], 1):  # Limit to top 5 results for LLM
                    context_text += f"{i}. Airport: {result.get('name', 'N/A')}, "
                    context_text += f"IATA Code: {result.get('iata_code', 'N/A')}, "
                    context_text += f"Country: {result.get('iso_country', 'N/A')}\n"
                
                # Create prompt for LLM
                prompt = f"""Based on the following airport information:
                
{context_text}

Please provide a concise summary addressing the query: "{query}".
Include key details from the search results and any relevant insights.
"""
                # Get summary from LLM
                summary = get_llm_response(prompt)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

    context = {
            'page_title': "Search results for \"" + (request.GET.get("q") or "") + "\"",
            'search_results': results, 
            'summary': summary,
        }
    response = render(request, 'search_results.html', context)
    return response

import json
@csrf_exempt
def rag(request):
    ''' Retrieval-Augmented Generation: Search + LLM summary '''
    query = request.GET.get("q", "").strip()
    results = []
    summary = ""
    k = 5  # Number of top results to retrieve
    
    if query:
        try:
            # Step 1: Retrieve top k results from Elasticsearch
            response = es.search(
                index="airports",
                query={
                    "multi_match": {
                        "query": query,
                        "fields": ["name", "iata_code", "iso_country"]
                    }
                },
                size=k  # Get top k results
            )
            results = [hit["_source"] for hit in response["hits"]["hits"]]
            
            # Step 2: Generate context from search results for the LLM
            if results:
                context = f"Search results for '{query}':\n\n"
                for i, result in enumerate(results, 1):
                    context += f"{i}. Airport: {result.get('name', 'N/A')}, "
                    context += f"IATA Code: {result.get('iata_code', 'N/A')}, "
                    context += f"Country: {result.get('iso_country', 'N/A')}\n"
                
                # Step 3: Create prompt for LLM
                prompt = f"""Based on the following airport information:
                
{context}

Please provide a concise summary addressing the query: "{query}".
Include key details from the search results and any relevant insights.
"""
                # Step 4: Call LLM API to generate summary
                summary = get_llm_response(prompt)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

    # Return JSON response instead of rendering HTML
    return JsonResponse({
        'query': query,
        'search_results': results,
        'summary': summary
    })

import requests
def get_llm_response(prompt):
    """Call the Groq API to get LLM response"""
    url = "https://api.groq.com/openai/v1/chat/completions"
    
    # Get API token from environment variables
    api_token = env("GROQ_API_TOKEN")
    
    headers = {
        "Authorization": f"Bearer {api_token}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": "meta-llama/llama-4-scout-17b-16e-instruct",
        "messages": [{
            "role": "user",
            "content": prompt
        }]
    }
    
    try:
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()
        
        result = response.json()
        return result["choices"][0]["message"]["content"]
    except Exception as e:
        print(f"Error calling LLM API: {str(e)}")
        return "Unable to generate summary. Please try again later."