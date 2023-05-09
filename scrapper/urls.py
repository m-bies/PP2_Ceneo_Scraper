from django.contrib import admin
from django.urls import path
from .views import *

urlpatterns = [
    path('', index, name='index'),
    path('extract/', extract, name='extract'),
    path('products/', products, name='products'),
    path('products/<str:productname>', product_page, name='product_page'),
    path('products/<str:productname>/download_csv', download, name='download'),
    path('products/<str:productname>/download_json', download_json, name='download_json'),
    path('products/<str:productname>/download_xlsx', download_xlsx, name='download_xlsx'),
    path('products/<str:productname>/charts', charts, name='charts'),
]