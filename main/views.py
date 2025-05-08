from django.shortcuts import render, redirect
from django.urls import reverse
import environ

# Setup environment variables
env = environ.Env()
environ.Env.read_env()
searh_host = env("SEARCH_HOST")

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