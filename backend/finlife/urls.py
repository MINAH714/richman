# backend/finlife/urls.py
from django.urls import path
from . import views

urlpatterns = [
    # API 호출로 DB에 데이터 적재 (http://localhost:8000/finlife/save/)
    path('save/', views.save_products, name='save_products'),
    
    # 상품 목록 (http://localhost:8000/finlife/)
    path('', views.product_list, name='product_list'),
    
    # 상품 상세 (http://localhost:8000/finlife/<상품코드>/)
    path('<str:fin_prdt_cd>/', views.product_detail, name='product_detail'),
    
    # 상품 가입 (http://localhost:8000/finlife/<상품코드>/join/)
    path('<str:fin_prdt_cd>/join/', views.join_product, name='join_product'),
]