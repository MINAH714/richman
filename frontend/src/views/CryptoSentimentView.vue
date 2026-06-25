<!--
  독립 라우트: /crypto/sentiment/:market?name=비트코인
  - 진입 시 캐시된 분석 자동 로드
  - "분석 실행" 버튼 → POST /api/crypto/sentiment/analyze/
  - SentimentGaugeCard(compact=false)로 전체 결과 표시
-->
<template>
  <div class="csv-page">

    <!-- ── 헤더 ── -->
    <header class="csv-header">
      <div class="csv-header-inner">
        <button class="csv-back-btn" @click="$router.back()">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none"
            stroke="currentColor" stroke-width="2.5">
            <path d="M19 12H5M12 5l-7 7 7 7"/>
          </svg>
        </button>
        <div>
          <span class="csv-eyebrow">SENTIMENT ANALYSIS</span>
          <h1 class="csv-title">
            {{ coinName }}
            <span class="csv-symbol-chip">{{ displaySymbol }}</span>
          </h1>
        </div>
      </div>
    </header>

    <!-- ── 분석 실행 바 ── -->
    <div class="csv-action-bar">
      <div class="csv-action-inner">
        <p class="csv-action-desc">
          최신 뉴스 5건을 GPT-4o-mini로 분석합니다
        </p>
        <button
          class="csv-run-btn"
          :class="{ 'csv-run-btn--loading': isAnalyzing }"
          :disabled="isAnalyzing"
          @click="runAnalysis"
        >
          <template v-if="!isAnalyzing">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none"
              stroke="currentColor" stroke-width="2.5">
              <circle cx="11" cy="11" r="8"/>
              <path d="m21 21-4.35-4.35"/>
            </svg>
            분석 실행
          </template>
          <template v-else>
            <span class="csv-dots">
              <i/><i/><i/>
            </span>
            분석 중…
          </template>
        </button>
      </div>
    </div>

    <!-- ── 에러 배너 ── -->
    <transition name="csv-fade">
      <div v-if="errorMsg" class="csv-error">
        <svg width="14" height="14" viewBox="0 0 24 24" fill="none"
          stroke="currentColor" stroke-width="2.5">
          <circle cx="12" cy="12" r="10"/>
          <line x1="12" y1="8" x2="12" y2="12"/>
          <line x1="12" y1="16" x2="12.01" y2="16"/>
        </svg>
        {{ errorMsg }}
      </div>
    </transition>

    <!-- ── 메인 콘텐츠 ── -->
    <main class="csv-main">
      <SentimentGaugeCard
        :positive-score="sentiment.positive_score"
        :neutral-score="sentiment.neutral_score"
        :negative-score="sentiment.negative_score"
        :summary="sentiment.summary"
        :articles="sentiment.articles"
        :analyzed-at="sentiment.analyzed_at"
        :is-loading="isLoadingCache"
        :compact="false"
      />
    </main>

  </div>
</template>

<script setup>
import { ref, computed, onMounted } from "vue";
import { useRoute } from "vue-router";
import { cryptoAPI } from "@/api/crypto.js";
import SentimentGaugeCard from "@/components/crypto/SentimentGaugeCard.vue";

const route = useRoute();

const coinSymbol  = computed(() => (route.params.market || "KRW-BTC").toUpperCase());
const coinName    = computed(() => route.query.name || coinSymbol.value);
const displaySymbol = computed(() => coinSymbol.value.replace("KRW-", ""));

// ── 상태 ──
const sentiment = ref({
  positive_score: 0,
  neutral_score:  0,
  negative_score: 0,
  summary:        "",
  articles:       [],
  analyzed_at:    "",
});
const isLoadingCache = ref(false);
const isAnalyzing    = ref(false);
const errorMsg       = ref("");

// ── 캐시 로드 (진입 시 자동) ──
async function loadCached() {
  isLoadingCache.value = true;
  try {
    const { data } = await cryptoAPI.getSentimentCached(coinSymbol.value);
    sentiment.value = { ...sentiment.value, ...data, articles: data.articles ?? [] };
  } catch {
    // 캐시 없음 — 조용히 무시 (빈 상태 노출)
  } finally {
    isLoadingCache.value = false;
  }
}

// ── 분석 실행 ──
async function runAnalysis() {
  isAnalyzing.value = true;
  errorMsg.value    = "";
  try {
    const { data } = await cryptoAPI.analyzeSentiment(
      coinSymbol.value,
      coinName.value
    );
    sentiment.value = { ...data };
  } catch (e) {
    errorMsg.value =
      e.response?.data?.error || "분석 중 오류가 발생했습니다. 다시 시도해 주세요.";
  } finally {
    isAnalyzing.value = false;
  }
}

onMounted(loadCached);
</script>

<style scoped>
.csv-page {
  min-height: 100vh;
  background: #0a0e1a;
  color: #e8eaf0;
  font-family: "Inter", "Pretendard", -apple-system, sans-serif;
  padding-bottom: 64px;
}

/* ── 헤더 ── */
.csv-header {
  padding: 24px 20px 18px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.06);
}
.csv-header-inner {
  max-width: 720px;
  margin: 0 auto;
  display: flex;
  align-items: center;
  gap: 16px;
}
.csv-back-btn {
  width: 36px;
  height: 36px;
  border-radius: 10px;
  border: none;
  background: rgba(255, 255, 255, 0.06);
  color: #8a8fa8;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  flex-shrink: 0;
  transition: background 0.15s, color 0.15s;
}
.csv-back-btn:hover { background: rgba(255, 255, 255, 0.11); color: #e8eaf0; }
.csv-eyebrow {
  display: block;
  font-size: 10px;
  font-weight: 700;
  letter-spacing: 0.12em;
  color: #5b6aff;
  margin-bottom: 3px;
}
.csv-title {
  margin: 0;
  font-size: 20px;
  font-weight: 800;
  color: #fff;
  line-height: 1.2;
  display: flex;
  align-items: center;
  gap: 8px;
  flex-wrap: wrap;
}
.csv-symbol-chip {
  font-size: 12px;
  font-weight: 600;
  color: #5b6aff;
  background: rgba(91, 106, 255, 0.12);
  border-radius: 6px;
  padding: 2px 8px;
}

/* ── 액션 바 ── */
.csv-action-bar {
  border-bottom: 1px solid rgba(255, 255, 255, 0.06);
  padding: 14px 20px;
}
.csv-action-inner {
  max-width: 720px;
  margin: 0 auto;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
}
.csv-action-desc {
  margin: 0;
  font-size: 13px;
  color: #5a6080;
}
.csv-run-btn {
  display: flex;
  align-items: center;
  gap: 7px;
  padding: 10px 18px;
  border-radius: 10px;
  border: none;
  background: linear-gradient(135deg, #5b6aff 0%, #7c4dff 100%);
  color: #fff;
  font-size: 13px;
  font-weight: 700;
  cursor: pointer;
  flex-shrink: 0;
  transition: opacity 0.15s, transform 0.1s;
  white-space: nowrap;
}
.csv-run-btn:hover:not(:disabled) { opacity: 0.86; transform: translateY(-1px); }
.csv-run-btn:disabled             { opacity: 0.5; cursor: not-allowed; }
.csv-run-btn--loading             { background: rgba(91, 106, 255, 0.4); }

/* 점 애니메이션 */
.csv-dots {
  display: inline-flex;
  gap: 3px;
  align-items: center;
}
.csv-dots i {
  display: block;
  width: 4px;
  height: 4px;
  border-radius: 50%;
  background: #fff;
  font-style: normal;
  animation: csvDot 1.1s ease-in-out infinite;
}
.csv-dots i:nth-child(2) { animation-delay: 0.14s; }
.csv-dots i:nth-child(3) { animation-delay: 0.28s; }
@keyframes csvDot {
  0%, 60%, 100% { transform: translateY(0);    opacity: 0.6; }
  30%           { transform: translateY(-4px); opacity: 1;   }
}

/* ── 에러 배너 ── */
.csv-error {
  max-width: 720px;
  margin: 14px auto 0;
  padding: 0 20px;
  display: flex;
  align-items: center;
  gap: 8px;
  background: rgba(248, 113, 113, 0.09);
  border: 1px solid rgba(248, 113, 113, 0.22);
  border-radius: 10px;
  color: #f87171;
  font-size: 13px;
  padding: 11px 16px;
}

/* ── 메인 ── */
.csv-main {
  max-width: 720px;
  margin: 24px auto 0;
  padding: 0 20px;
}

/* ── 트랜지션 ── */
.csv-fade-enter-active,
.csv-fade-leave-active { transition: opacity 0.25s ease; }
.csv-fade-enter-from,
.csv-fade-leave-to     { opacity: 0; }
</style>