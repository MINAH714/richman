from django.urls import path
from . import views

app_name = 'commodities'

urlpatterns = [
    # 프론트엔드의 axios.get 주소 구조와 일치하도록 파라미터 맵핑
    path('<str:asset_type>/', views.get_commodity_data, name='get_commodity_data'),
]