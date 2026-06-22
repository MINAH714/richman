from django.db import models

# Create your models here.
class DepositProduct(models.Model):
    fin_prdt_cd = models.CharField(max_length=100, unique=True) # 금융상품 코드 (고유값)
    kor_co_nm = models.CharField(max_length=100)                # 금융회사명
    fin_prdt_nm = models.CharField(max_length=100)              # 금융상품명
    join_way = models.TextField()                               # 가입방법
    join_member = models.TextField(blank=True, null=True)       # 가입대상
    spcl_cnd = models.TextField(blank=True, null=True)          # 우대조건
    etc_note = models.TextField(blank=True, null=True)          # 기타유의사항

    def __str__(self):
        return f"[{self.kor_co_nm}] {self.fin_prdt_nm}"

class DepositOption(models.Model):
    product = models.ForeignKey(DepositProduct, on_delete=models.CASCADE, related_name='options')
    save_trm = models.IntegerField()                            # 가입기간 (개월)
    intr_rate = models.FloatField(blank=True, null=True)        # 기본금리
    intr_rate2 = models.FloatField(blank=True, null=True)       # 최고우대금리

    def __str__(self):
        return f"{self.product.fin_prdt_nm} - {self.save_trm}개월"