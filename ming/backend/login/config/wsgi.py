import os
from django.core.wsgi import get_wsgi_application

# 프로젝트 설정 폴더가 config이므로 아래와 같이 설정합니다.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

application = get_wsgi_application()