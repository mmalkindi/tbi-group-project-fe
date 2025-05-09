from django.urls import path
from main.views import *


urlpatterns = [
    path('', index, name='index'),
    path('es-test/', test_es_connection, name='test_es_connection'),
]