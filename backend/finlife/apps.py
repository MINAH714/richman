# backend/finlife/apps.py
from django.apps import AppConfig

class FinlifeConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'finlife'

    def ready(self):
        # 서버 시작 시 딱 한 번만 데이터가 없는지 확인하고 로드
        from django.db.models.signals import post_migrate
        from django.core.management import call_command
        
        def run_initial_data(sender, **kwargs):
            from .models import DepositProduct
            if not DepositProduct.objects.exists():
                print("📡 예적금 데이터를 불러오는 중...")
                # 여기서 save_products 로직을 호출하거나 
                # 별도로 작성한 management command를 실행
        
        post_migrate.connect(run_initial_data, sender=self)