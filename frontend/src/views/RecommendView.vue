<template>
  <div class="recommend-page">
    <div class="section-inner recommend-container">
      
      <div class="recommend-header">
        <p class="eyebrow">AI FINANCIAL RECOMMENDATION</p>
        <h1 class="hero-title">고객님을 위한 맞춤 금융상품</h1>
        <p class="hero-desc">
          입력해주신 자산 규모와 투자 성향을 바탕으로<br>
          가장 적합한 상위 3개 상품을 분석했습니다.
        </p>
      </div>

      <div class="recommend-grid">
        
        <div class="feature-card product-card rank-1">
          <div class="card-header">
            <span class="rank-badge">1위</span>
            <p class="bank-name">신한은행</p>
          </div>
          <h3 class="product-name">청년 처음적금</h3>
          <p class="product-rate">최고 연 <span>6.50%</span></p>
          
          <div class="ai-reason">
            <strong>AI 추천 이유</strong>
            <p>공격적인 투자 성향을 보완할 수 있는 안정적인 고금리 적금입니다. 20대 청년 우대 이율을 최대한 활용할 수 있습니다.</p>
          </div>
          
          <button class="btn btn-primary w-100">가입하기</button>
        </div>

        <div class="feature-card product-card">
          <div class="card-header">
            <span class="rank-badge default-badge">2위</span>
            <p class="bank-name">우리은행</p>
          </div>
          <h3 class="product-name">우리 청년도약계좌</h3>
          <p class="product-rate">최고 연 <span>6.00%</span></p>
          
          <div class="ai-reason">
            <strong>AI 추천 이유</strong>
            <p>월 50만 원 이상의 여유 자금을 중장기적으로 굴리기에 적합하며, 비과세 혜택으로 실질 수익률이 높습니다.</p>
          </div>
          
          <button class="btn btn-outline w-100">가입하기</button>
        </div>

        <div class="feature-card product-card">
          <div class="card-header">
            <span class="rank-badge default-badge">3위</span>
            <p class="bank-name">카카오뱅크</p>
          </div>
          <h3 class="product-name">한달적금</h3>
          <p class="product-rate">최고 연 <span>5.50%</span></p>
          
          <div class="ai-reason">
            <strong>AI 추천 이유</strong>
            <p>가상화폐 등 변동성이 큰 자산에 투자하기 전, 단기적으로 목돈을 파킹하고 소소한 성취감을 얻기에 좋습니다.</p>
          </div>
          
          <button class="btn btn-outline w-100">가입하기</button>
        </div>

      </div>

    </div>
  </div>
</template>

<script setup>
// 추후 백엔드 API (GET /api/products/recommend/) 호출 로직이 이곳에 들어갈 예정입니다.
</script>

<style scoped>
.recommend-page {
  min-height: 100vh;
  background: var(--color-bg-page);
  font-family: var(--font-main);
  color: var(--color-text-primary);
  padding: 60px 24px;
}

.recommend-container {
  max-width: 1080px;
  margin: 0 auto;
}

/* ── HEADER ── */
.recommend-header {
  text-align: center;
  margin-bottom: 56px;
}
.eyebrow {
  font-size: 12px;
  font-weight: 600;
  letter-spacing: 0.1em;
  color: var(--color-primary);
  margin: 0 0 14px;
}
.hero-title {
  font-size: 2.1rem;
  font-weight: 600;
  margin: 0 0 16px;
  letter-spacing: -0.02em;
}
.hero-desc {
  font-size: 0.95rem;
  color: var(--color-text-secondary);
  line-height: 1.6;
}

/* ── GRID & CARDS ── */
.recommend-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 24px;
}

.product-card {
  padding: 32px 24px;
  display: flex;
  flex-direction: column;
  background: var(--color-bg-card);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-lg);
  transition: transform 0.2s, border-color 0.2s;
}
.product-card:hover {
  transform: translateY(-4px);
  border-color: var(--color-primary);
}
.rank-1 {
  border: 2px solid var(--color-primary);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.04);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}
.rank-badge {
  background: var(--color-primary);
  color: #fff;
  font-size: 0.8rem;
  font-weight: 700;
  padding: 4px 10px;
  border-radius: 4px;
}
.default-badge {
  background: var(--color-border-strong);
  color: var(--color-text-primary);
}
.bank-name {
  font-size: 0.85rem;
  color: var(--color-text-secondary);
  font-weight: 500;
  margin: 0;
}

.product-name {
  font-size: 1.3rem;
  font-weight: 600;
  margin: 0 0 8px;
  letter-spacing: -0.01em;
}
.product-rate {
  font-size: 0.9rem;
  color: var(--color-text-secondary);
  margin: 0 0 24px;
}
.product-rate span {
  font-size: 1.4rem;
  font-weight: 700;
  color: var(--color-text-primary);
  margin-left: 4px;
}

/* ── AI REASON BOX ── */
.ai-reason {
  background: var(--color-bg-secondary);
  padding: 16px;
  border-radius: var(--radius-md);
  margin-bottom: 24px;
  flex-grow: 1; /* 카드 높이 맞추기 */
}
.ai-reason strong {
  display: block;
  font-size: 0.8rem;
  color: var(--color-primary);
  margin-bottom: 8px;
}
.ai-reason p {
  font-size: 0.85rem;
  line-height: 1.5;
  color: var(--color-text-secondary);
  margin: 0;
}

/* ── BUTTONS ── */
.btn {
  padding: 14px;
  font-size: 0.95rem;
  font-weight: 600;
  border-radius: var(--radius-md);
  cursor: pointer;
  transition: all 0.2s;
  text-align: center;
}
.btn-primary {
  background: var(--color-primary);
  color: #fff;
  border: 1px solid var(--color-primary);
}
.btn-primary:hover {
  background: var(--color-text-primary);
  border-color: var(--color-text-primary);
}
.btn-outline {
  background: transparent;
  color: var(--color-text-primary);
  border: 1px solid var(--color-border-strong);
}
.btn-outline:hover {
  border-color: var(--color-text-primary);
}
.w-100 {
  width: 100%;
}

/* ── RESPONSIVE ── */
@media (max-width: 900px) {
  .recommend-grid { grid-template-columns: repeat(2, 1fr); }
}
@media (max-width: 600px) {
  .recommend-grid { grid-template-columns: 1fr; }
}
</style>