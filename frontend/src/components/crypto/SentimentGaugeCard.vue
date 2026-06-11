<!--
  재사용 가능한 감성 게이지 카드 컴포넌트.
  주식 파트(Boo)가 동일 컴포넌트를 가져다 쓸 수 있도록 props 기반 설계.

  Props:
    - positiveScore  : Number (0.0 ~ 1.0)
    - neutralScore   : Number (0.0 ~ 1.0)
    - negativeScore  : Number (0.0 ~ 1.0)
    - summary        : String  (한 줄 요약)
    - articles       : Array   (뉴스 목록)
    - analyzedAt     : String  (ISO datetime)
    - isLoading      : Boolean
    - compact        : Boolean (상세 페이지 내 섹션용 축약 모드)
-->
<template>
  <div class="sgc-root" :class="{ 'sgc-compact': compact }">

    <!-- ── 헤더 행 ── -->
    <div class="sgc-header">
      <div class="sgc-header-left">
        <span class="sgc-label">뉴스 감성 분석</span>
        <span v-if="analyzedAt" class="sgc-timestamp">{{ formattedAt }}</span>
      </div>
      <div class="sgc-dominant-chip" :class="dominantClass" v-if="hasData">
        <span class="sgc-dominant-emoji">{{ dominantEmoji }}</span>
        <span class="sgc-dominant-text">{{ dominantLabel }}</span>
        <span class="sgc-dominant-pct">{{ dominantPct }}%</span>
      </div>
    </div>

    <!-- ── 로딩 ── -->
    <div v-if="isLoading" class="sgc-loading">
      <div class="sgc-skeleton" v-for="n in 3" :key="n" />
    </div>

    <!-- ── 데이터 없음 ── -->
    <div v-else-if="!hasData" class="sgc-empty">
      <span class="sgc-empty-icon">📡</span>
      <p>아직 분석된 데이터가 없습니다</p>
    </div>

    <!-- ── 게이지 + 요약 ── -->
    <template v-else>
      <!-- 한 줄 요약 -->
      <p class="sgc-summary">{{ summary }}</p>

      <!-- 게이지 바 3개 -->
      <div class="sgc-gauges">
        <div class="sgc-gauge-row" v-for="row in gaugeRows" :key="row.key">
          <span class="sgc-gauge-icon">{{ row.icon }}</span>
          <span class="sgc-gauge-label" :style="{ color: row.color }">{{ row.label }}</span>
          <div class="sgc-gauge-track">
            <div
              class="sgc-gauge-fill"
              :style="{
                width: animated[row.key] + '%',
                background: row.gradient,
              }"
            >
              <span
                v-if="animated[row.key] > 10"
                class="sgc-gauge-inner-pct"
              >{{ Math.round(animated[row.key]) }}%</span>
            </div>
          </div>
          <span class="sgc-gauge-outer-pct" :style="{ color: row.color }">
            {{ pct(row.score) }}%
          </span>
        </div>
      </div>

      <!-- 뉴스 목록 (compact 모드에서는 숨김 → 독립 페이지에서만 노출) -->
      <template v-if="!compact && articles?.length">
        <div class="sgc-news-divider">
          <span class="sgc-news-divider-label">분석 뉴스 {{ articles.length }}건</span>
        </div>
        <ul class="sgc-news-list">
          <li
            v-for="(article, i) in articles"
            :key="i"
            class="sgc-news-item"
          >
            <a
              :href="article.link"
              target="_blank"
              rel="noopener noreferrer"
              class="sgc-news-link"
            >
              <span class="sgc-news-num">{{ String(i + 1).padStart(2, "0") }}</span>
              <div class="sgc-news-body">
                <p class="sgc-news-title">{{ article.title }}</p>
                <p class="sgc-news-desc" v-if="article.description">{{ article.description }}</p>
              </div>
              <svg class="sgc-news-ext" width="13" height="13" viewBox="0 0 24 24" fill="none"
                stroke="currentColor" stroke-width="2.2">
                <path d="M7 17L17 7M17 7H7M17 7v10"/>
              </svg>
            </a>
          </li>
        </ul>
      </template>

      <!-- compact 모드: "전체 보기" 링크 -->
      <div v-if="compact && viewAllRoute" class="sgc-view-all">
        <router-link :to="viewAllRoute" class="sgc-view-all-link">
          전체 분석 보기
          <svg width="13" height="13" viewBox="0 0 24 24" fill="none"
            stroke="currentColor" stroke-width="2.5">
            <path d="M5 12h14M12 5l7 7-7 7"/>
          </svg>
        </router-link>
      </div>
    </template>

  </div>
</template>

<script setup>
import { ref, computed, watch } from "vue";

const props = defineProps({
  positiveScore: { type: Number, default: 0 },
  neutralScore:  { type: Number, default: 0 },
  negativeScore: { type: Number, default: 0 },
  summary:       { type: String, default: "" },
  articles:      { type: Array,  default: () => [] },
  analyzedAt:    { type: String, default: "" },
  isLoading:     { type: Boolean, default: false },
  compact:       { type: Boolean, default: false },
  viewAllRoute:  { type: [String, Object], default: null },
});

// ── 퍼센트 변환 (0.0~1.0 → 0~100) ──
const pct = (score) => Math.round((score ?? 0) * 100);

const hasData = computed(
  () => props.positiveScore + props.neutralScore + props.negativeScore > 0
);

// ── 게이지 행 정의 ──
const gaugeRows = computed(() => [
  {
    key: "positive",
    label: "긍정",
    icon: "😊",
    score: props.positiveScore,
    color: "#4ade80",
    gradient: "linear-gradient(90deg, #166534 0%, #4ade80 100%)",
  },
  {
    key: "neutral",
    label: "중립",
    icon: "😐",
    score: props.neutralScore,
    color: "#94a3b8",
    gradient: "linear-gradient(90deg, #334155 0%, #94a3b8 100%)",
  },
  {
    key: "negative",
    label: "부정",
    icon: "😰",
    score: props.negativeScore,
    color: "#f87171",
    gradient: "linear-gradient(90deg, #7f1d1d 0%, #f87171 100%)",
  },
]);

// ── 애니메이션 ──
const animated = ref({ positive: 0, neutral: 0, negative: 0 });

function runAnimation() {
  const targets = {
    positive: pct(props.positiveScore),
    neutral:  pct(props.neutralScore),
    negative: pct(props.negativeScore),
  };
  animated.value = { positive: 0, neutral: 0, negative: 0 };

  const DURATION = 750;
  const STEP = 16;
  let elapsed = 0;

  const timer = setInterval(() => {
    elapsed += STEP;
    const progress = Math.min(elapsed / DURATION, 1);
    const ease = 1 - Math.pow(1 - progress, 3); // ease-out-cubic

    animated.value = {
      positive: targets.positive * ease,
      neutral:  targets.neutral  * ease,
      negative: targets.negative * ease,
    };

    if (progress >= 1) clearInterval(timer);
  }, STEP);
}

// 데이터 변경 시 자동 실행
watch(
  () => [props.positiveScore, props.neutralScore, props.negativeScore],
  (vals) => {
    if (vals.some((v) => v > 0)) runAnimation();
  },
  { immediate: true }
);

// ── 도미넌트 계산 ──
const dominant = computed(() => {
  const scores = {
    positive: props.positiveScore,
    neutral:  props.neutralScore,
    negative: props.negativeScore,
  };
  return Object.entries(scores).reduce(
    (a, b) => (b[1] > a[1] ? b : a),
    ["neutral", 0]
  )[0];
});

const dominantClass = computed(
  () => ({ positive: "sgc-chip-pos", neutral: "sgc-chip-neu", negative: "sgc-chip-neg" }[dominant.value]
));
const dominantEmoji = computed(
  () => ({ positive: "😊", neutral: "😐", negative: "😰" }[dominant.value])
);
const dominantLabel = computed(
  () => ({ positive: "긍정 우세", neutral: "중립", negative: "부정 우세" }[dominant.value])
);
const dominantPct = computed(() =>
  pct({ positive: props.positiveScore, neutral: props.neutralScore, negative: props.negativeScore }[dominant.value])
);

// ── 타임스탬프 포맷 ──
const formattedAt = computed(() => {
  if (!props.analyzedAt) return "";
  try {
    return new Date(props.analyzedAt).toLocaleString("ko-KR", {
      month: "short", day: "numeric", hour: "2-digit", minute: "2-digit",
    });
  } catch {
    return "";
  }
});
</script>

<style scoped>
/* ── 루트 ── */
.sgc-root {
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 18px;
  padding: 22px 22px 20px;
  font-family: "Inter", "Pretendard", -apple-system, sans-serif;
}
.sgc-compact {
  border-radius: 14px;
  padding: 18px;
}

/* ── 헤더 ── */
.sgc-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 14px;
  gap: 10px;
}
.sgc-header-left {
  display: flex;
  flex-direction: column;
  gap: 2px;
}
.sgc-label {
  font-size: 11px;
  font-weight: 700;
  letter-spacing: 0.1em;
  text-transform: uppercase;
  color: #5a6080;
}
.sgc-timestamp {
  font-size: 11px;
  color: #3d4260;
}

/* ── 도미넌트 칩 ── */
.sgc-dominant-chip {
  display: flex;
  align-items: center;
  gap: 5px;
  border-radius: 20px;
  padding: 5px 12px 5px 8px;
  font-size: 12px;
  font-weight: 700;
  flex-shrink: 0;
}
.sgc-chip-pos {
  background: rgba(74, 222, 128, 0.1);
  border: 1px solid rgba(74, 222, 128, 0.22);
  color: #4ade80;
}
.sgc-chip-neu {
  background: rgba(148, 163, 184, 0.1);
  border: 1px solid rgba(148, 163, 184, 0.22);
  color: #94a3b8;
}
.sgc-chip-neg {
  background: rgba(248, 113, 113, 0.1);
  border: 1px solid rgba(248, 113, 113, 0.22);
  color: #f87171;
}
.sgc-dominant-emoji { font-size: 14px; }
.sgc-dominant-pct   { opacity: 0.8; margin-left: 2px; }

/* ── 요약 ── */
.sgc-summary {
  margin: 0 0 16px;
  font-size: 13px;
  line-height: 1.55;
  color: #9aa0bf;
  font-style: italic;
}

/* ── 게이지 ── */
.sgc-gauges {
  display: flex;
  flex-direction: column;
  gap: 10px;
}
.sgc-gauge-row {
  display: flex;
  align-items: center;
  gap: 9px;
}
.sgc-gauge-icon  { font-size: 15px; flex-shrink: 0; }
.sgc-gauge-label {
  font-size: 12px;
  font-weight: 600;
  width: 30px;
  flex-shrink: 0;
}
.sgc-gauge-track {
  flex: 1;
  height: 26px;
  background: rgba(255, 255, 255, 0.05);
  border-radius: 7px;
  overflow: hidden;
}
.sgc-gauge-fill {
  height: 100%;
  border-radius: 7px;
  display: flex;
  align-items: center;
  justify-content: flex-end;
  padding-right: 8px;
  min-width: 0;
  transition: width 16ms linear;
}
.sgc-gauge-inner-pct {
  font-size: 11px;
  font-weight: 700;
  color: rgba(255, 255, 255, 0.9);
  white-space: nowrap;
}
.sgc-gauge-outer-pct {
  font-size: 12px;
  font-weight: 700;
  width: 34px;
  text-align: right;
  flex-shrink: 0;
}

/* ── 뉴스 목록 ── */
.sgc-news-divider {
  margin: 20px 0 10px;
  display: flex;
  align-items: center;
  gap: 10px;
}
.sgc-news-divider::before,
.sgc-news-divider::after {
  content: "";
  flex: 1;
  height: 1px;
  background: rgba(255, 255, 255, 0.06);
}
.sgc-news-divider-label {
  font-size: 10px;
  font-weight: 700;
  letter-spacing: 0.1em;
  text-transform: uppercase;
  color: #3d4260;
  white-space: nowrap;
}
.sgc-news-list {
  list-style: none;
  margin: 0;
  padding: 0;
  display: flex;
  flex-direction: column;
  gap: 1px;
}
.sgc-news-link {
  display: flex;
  align-items: flex-start;
  gap: 10px;
  padding: 10px 8px;
  border-radius: 10px;
  text-decoration: none;
  color: inherit;
  transition: background 0.12s;
}
.sgc-news-link:hover { background: rgba(255, 255, 255, 0.045); }
.sgc-news-num {
  font-size: 10px;
  font-weight: 800;
  color: #5b6aff;
  padding-top: 2px;
  flex-shrink: 0;
  font-variant-numeric: tabular-nums;
  letter-spacing: 0.02em;
}
.sgc-news-body { flex: 1; min-width: 0; }
.sgc-news-title {
  margin: 0 0 3px;
  font-size: 13px;
  font-weight: 600;
  color: #c8cce0;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
.sgc-news-desc {
  margin: 0;
  font-size: 11px;
  color: #4e5470;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
  line-height: 1.5;
}
.sgc-news-ext {
  color: #3d4260;
  flex-shrink: 0;
  margin-top: 3px;
}

/* ── 전체 보기 링크 ── */
.sgc-view-all {
  margin-top: 16px;
  text-align: right;
}
.sgc-view-all-link {
  display: inline-flex;
  align-items: center;
  gap: 5px;
  font-size: 12px;
  font-weight: 600;
  color: #5b6aff;
  text-decoration: none;
  transition: opacity 0.15s;
}
.sgc-view-all-link:hover { opacity: 0.75; }

/* ── 로딩 스켈레톤 ── */
.sgc-loading {
  display: flex;
  flex-direction: column;
  gap: 10px;
  padding: 4px 0;
}
.sgc-skeleton {
  height: 26px;
  border-radius: 7px;
  background: linear-gradient(90deg, rgba(255,255,255,0.04) 25%, rgba(255,255,255,0.08) 50%, rgba(255,255,255,0.04) 75%);
  background-size: 200% 100%;
  animation: shimmer 1.4s infinite;
}
.sgc-skeleton:nth-child(1) { width: 100%; }
.sgc-skeleton:nth-child(2) { width: 75%; }
.sgc-skeleton:nth-child(3) { width: 55%; }
@keyframes shimmer {
  0%   { background-position: 200% 0; }
  100% { background-position: -200% 0; }
}

/* ── 빈 상태 ── */
.sgc-empty {
  text-align: center;
  padding: 20px 0 6px;
}
.sgc-empty-icon { font-size: 32px; display: block; margin-bottom: 8px; }
.sgc-empty p {
  margin: 0;
  font-size: 13px;
  color: #3d4260;
}
</style>