from django.contrib import admin
from django.urls import path
from .views import *

urlpatterns = [
    path('', index, name='index'),
    path('extract/', extract, name='extract'),
    path('products/', products, name='products'),
    path('products/<str:productname>', product_page, name='product_page'),
]