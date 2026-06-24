<template>
  <footer class="site-footer">
    <div class="footer-inner">
      
      <div class="footer-links">
        <router-link to="/terms" class="link-item">이용약관</router-link>
        <router-link to="/privacy" class="link-item font-bold text-black">개인정보처리방침</router-link>
        <router-link to="/disclaimer" class="link-item">금융상품공시 고지</router-link>
        <router-link to="/about" class="link-item">회사소개</router-link>
      </div>

      <div class="footer-grid">
        <div class="footer-info">
          <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 16px; user-select: none;">
            <!-- 1. 로고 이미지 심볼 -->
            <img 
              src="../../assets/logo.png" 
              alt="Richman" 
              style="height: 32px; width: auto; object-fit: contain; opacity: 0.9;" 
            />
            
            <!-- 2. 로고 텍스트 (자간 바짝 줄이고 마침표 블루 포인트 적용) -->
            <span style="font-family: 'Hanken Grotesk', sans-serif; font-weight: 900; font-size: 1.3rem; color: #191c1d; letter-spacing: -0.05em; line-height: 1;">
              Richman<span style="color: #0050cc; margin-left: 1px;">.</span>
            </span>
          </div>
          
          <p class="info-text">
            <span>팀명: SSAFY 15기 부울경 2반 11조</span>
            <span class="bar">|</span>
            <span>대표 연구원: 정병연</span>
          </p>
          <p class="info-text">
            <span>주소: 부산 강서구 녹산산업중로 333 부울경캠퍼스</span>
            <span class="bar">|</span>
            <span>이메일: support@richman.local</span>
          </p>
        </div>

      </div>

      <div class="footer-bottom">
        <p class="copyright">© 2026 Richman. All rights reserved.</p>
      </div>

    </div>
  </footer>
</template>

<style scoped>
.site-footer {
  width: 100%;
  background: #ffffff;
  border-top: 1px solid #e1e3e4; /* 하이라인 보더 */
  padding: 40px 24px 24px;
  font-family: 'Inter', sans-serif;
  color: #4c4546;
}
.footer-inner {
  max-width: 1200px;
  margin: 0 auto;
}

/* 링크 구역 */
.footer-links {
  display: flex;
  gap: 20px;
  margin-bottom: 24px;
  border-bottom: 1px solid #e1e3e4;
  padding-bottom: 16px;
}
.link-item {
  font-size: 0.8rem;
  color: #4c4546;
  text-decoration: none;
}
.link-item:hover {
  color: #0050cc; /* 포인트 블루 */
}

/* 그리드 레이아웃 */
.footer-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 40px;
  align-items: start;
}

/* 좌측 정보 */
.footer-logo {
  font-family: 'Hanken Grotesk', sans-serif;
  font-size: 1.1rem;
  font-weight: 900;
  color: #191c1d;
  margin: 0 0 12px;
  letter-spacing: -0.04em;
}
.footer-logo .dot {
  color: #0050cc;
}
.info-text {
  font-size: 0.78rem;
  color: #818488;
  margin: 0 0 4px;
  line-height: 1.5;
}
.bar {
  margin: 0 8px;
  color: #e1e3e4;
}

/* 우측 면책조항 */
.footer-disclaimer {
  font-size: 0.75rem;
  color: #818488;
  line-height: 1.6;
  background: #f8f9fa;
  padding: 14px;
  border: 1px solid #e1e3e4;
}
.footer-disclaimer strong {
  color: #191c1d;
}

/* 카피라이트 */
.footer-bottom {
  margin-top: 32px;
  padding-top: 16px;
  border-top: 1px solid #e1e3e4;
}
.copyright {
  font-size: 0.75rem;
  color: #818488;
  margin: 0;
}

@media (max-width: 768px) {
  .footer-grid {
    grid-template-columns: 1fr;
    gap: 24px;
  }
}
</style>