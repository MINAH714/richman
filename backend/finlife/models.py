from django.db import models

# Create your models here.
# finlife/models.py

BANK_HOME_URLS = {
    "KB국민은행": "https://www.kbstar.com",
    "신한은행": "https://www.shinhan.com",
    "하나은행": "https://www.kebhana.com",
    "우리은행": "https://www.wooribank.com",
    "NH농협은행": "https://www.nonghyup.com",
    "IBK기업은행": "https://www.ibk.co.kr",
    "SC제일은행": "https://www.standardchartered.co.kr",
    "씨티은행": "https://www.citibank.co.kr",
    "카카오뱅크": "https://www.kakaobank.com",
    "케이뱅크": "https://www.kbanknow.com",
    "토스뱅크": "https://www.tossbank.com",
    "새마을금고": "https://www.kfcc.co.kr",
    "신협": "https://www.cu.co.kr",
    "우체국예금": "https://www.epostbank.go.kr",
    "수협은행": "https://www.suhyup-bank.com",
    "전북은행": "https://www.jbbank.co.kr",
    "광주은행": "https://www.kjbank.com",
    "제주은행": "https://www.jejubank.co.kr",
    "부산은행": "https://www.busanbank.co.kr",
    "경남은행": "https://www.knbank.co.kr",
    "대구은행": "https://www.dgb.co.kr",
}

class DepositProduct(models.Model):
    fin_prdt_cd = models.CharField(max_length=100, unique=True)
    kor_co_nm = models.CharField(max_length=100)
    fin_prdt_nm = models.CharField(max_length=100)
    join_way = models.TextField()
    join_member = models.TextField(blank=True, null=True)
    spcl_cnd = models.TextField(blank=True, null=True)
    etc_note = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"[{self.kor_co_nm}] {self.fin_prdt_nm}"

    @property
    def finlife_url(self):
        """금융상품한눈에 상품 상세 링크"""
        return f"https://finlife.fss.or.kr/finlife/fncPrdCmpr/prdDetail.do?menuNo=700002&fin_prdt_cd={self.fin_prdt_cd}"

    @property
    def bank_home_url(self):
        """은행 공홈 (매핑 없으면 None)"""
        return BANK_HOME_URLS.get(self.kor_co_nm)

    @property
    def can_join_online(self):
        """온라인 가입 가능 여부"""
        return any(k in self.join_way for k in ["인터넷", "스마트폰", "온라인"])

class DepositOption(models.Model):
    product = models.ForeignKey(DepositProduct, on_delete=models.CASCADE, related_name='options')
    save_trm = models.IntegerField()                            # 가입기간 (개월)
    intr_rate = models.FloatField(blank=True, null=True)        # 기본금리
    intr_rate2 = models.FloatField(blank=True, null=True)       # 최고우대금리

    def __str__(self):
        return f"{self.product.fin_prdt_nm} - {self.save_trm}개월"