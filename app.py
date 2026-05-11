import streamlit as st
import anthropic
import feedparser
import json
import re
from datetime import datetime
from urllib.parse import quote

# ─── 페이지 설정 ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="⚔️ 글로벌 분쟁 미디어 시각 비교",
    page_icon="⚔️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─── CSS ───────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@300;400;600;700&family=Bebas+Neue&display=swap');

    html, body, [class*="css"] {
        font-family: 'Noto Sans KR', sans-serif;
    }

    /* 배경 */
    .stApp {
        background: #0a0a0f;
        background-image:
            radial-gradient(ellipse at 20% 50%, rgba(180,20,20,0.07) 0%, transparent 60%),
            radial-gradient(ellipse at 80% 20%, rgba(20,60,180,0.07) 0%, transparent 60%);
    }

    .main-title {
        font-family: 'Bebas Neue', sans-serif;
        text-align: center;
        font-size: 3rem;
        letter-spacing: 4px;
        color: #f0f0f0;
        margin-bottom: 0.2rem;
        text-shadow: 0 0 40px rgba(200,30,30,0.4);
    }
    .subtitle {
        text-align: center;
        color: #666;
        font-size: 0.85rem;
        letter-spacing: 2px;
        text-transform: uppercase;
        margin-bottom: 2.5rem;
    }

    /* 헤드라인 카드 */
    .headline-item {
        background: rgba(255,255,255,0.04);
        border: 1px solid rgba(255,255,255,0.08);
        border-radius: 8px;
        padding: 0.65rem 0.9rem;
        margin-bottom: 0.5rem;
        font-size: 0.84rem;
        color: #ccc;
        line-height: 1.55;
        transition: background 0.2s;
        cursor: default;
    }
    .headline-item:hover {
        background: rgba(255,255,255,0.07);
    }
    .headline-date {
        font-size: 0.7rem;
        color: #555;
        margin-top: 3px;
    }
    .headline-source-badge {
        display: inline-block;
        font-size: 0.68rem;
        padding: 1px 7px;
        border-radius: 3px;
        margin-right: 6px;
        font-weight: 600;
        vertical-align: middle;
    }

    /* 미디어 분석 카드 */
    .analysis-card {
        background: #111118;
        border: 1px solid rgba(255,255,255,0.1);
        border-radius: 14px;
        padding: 1.4rem;
        height: 100%;
    }
    .analysis-card-red  { border-top: 3px solid #c0392b; }
    .analysis-card-blue { border-top: 3px solid #2471a3; }

    .card-header {
        font-size: 1rem;
        font-weight: 700;
        color: #f0f0f0;
        margin-bottom: 0.3rem;
    }
    .card-region {
        font-size: 0.75rem;
        color: #666;
        margin-bottom: 1rem;
        padding-bottom: 0.8rem;
        border-bottom: 1px solid rgba(255,255,255,0.07);
    }
    .section-label {
        font-size: 0.68rem;
        color: #555;
        text-transform: uppercase;
        letter-spacing: 1.5px;
        margin: 0.9rem 0 0.35rem;
    }
    .section-content {
        font-size: 0.84rem;
        color: #bbb;
        line-height: 1.65;
    }

    .tone-pill {
        display: inline-block;
        padding: 3px 12px;
        border-radius: 20px;
        font-size: 0.78rem;
        font-weight: 600;
    }

    .term-tag {
        display: inline-block;
        padding: 3px 9px;
        border-radius: 4px;
        font-size: 0.75rem;
        margin: 2px 2px;
        border: 1px solid;
    }
    .term-used-red    { color: #e87474; border-color: rgba(200,60,60,0.3);  background: rgba(200,60,60,0.1); }
    .term-used-blue   { color: #74b4e8; border-color: rgba(60,100,200,0.3); background: rgba(60,100,200,0.1); }
    .term-avoided     { color: #777;    border-color: rgba(255,255,255,0.1); background: rgba(255,255,255,0.04); }

    /* 점수 바 */
    .score-row { margin: 0.35rem 0; }
    .score-name { font-size: 0.75rem; color: #777; display: flex; justify-content: space-between; margin-bottom: 2px; }
    .score-track { height: 5px; background: rgba(255,255,255,0.07); border-radius: 3px; }
    .score-fill  { height: 5px; border-radius: 3px; }

    /* 비교 박스 */
    .compare-section {
        background: #0e0e18;
        border: 1px solid rgba(255,255,255,0.09);
        border-top: 3px solid #d4ac0d;
        border-radius: 14px;
        padding: 1.5rem;
        margin-top: 1.5rem;
    }
    .compare-title {
        font-family: 'Bebas Neue', sans-serif;
        font-size: 1.4rem;
        letter-spacing: 2px;
        color: #d4ac0d;
        margin-bottom: 1rem;
    }
    .diff-item {
        background: rgba(255,255,255,0.03);
        border-left: 2px solid rgba(212,172,13,0.4);
        padding: 0.55rem 0.9rem;
        margin-bottom: 0.5rem;
        font-size: 0.85rem;
        color: #bbb;
        line-height: 1.6;
        border-radius: 0 6px 6px 0;
    }
    .info-grid {
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 1rem;
        margin-top: 1rem;
    }
    .info-box {
        background: rgba(255,255,255,0.03);
        border-radius: 8px;
        padding: 0.9rem;
        border: 1px solid rgba(255,255,255,0.06);
    }
    .tip-box {
        background: rgba(212,172,13,0.07);
        border: 1px solid rgba(212,172,13,0.2);
        border-radius: 8px;
        padding: 0.9rem;
        margin-top: 1rem;
        font-size: 0.85rem;
        color: #d4ac0d;
        line-height: 1.65;
    }
    .headline-quote {
        font-style: italic;
        color: #d4ac0d;
        font-size: 0.83rem;
        line-height: 1.6;
    }

    /* 사이드바 */
    [data-testid="stSidebar"] {
        background: #0d0d14 !important;
        border-right: 1px solid rgba(255,255,255,0.06);
    }
    [data-testid="stSidebar"] label, [data-testid="stSidebar"] .stMarkdown {
        color: #aaa !important;
    }

    /* 버튼 */
    .stButton > button {
        background: linear-gradient(135deg, #8b0000, #c0392b) !important;
        color: white !important;
        border: none !important;
        border-radius: 8px !important;
        font-weight: 700 !important;
        font-size: 0.95rem !important;
        width: 100% !important;
        padding: 0.6rem 1rem !important;
        letter-spacing: 1px !important;
        transition: opacity 0.2s !important;
    }
    .stButton > button:hover { opacity: 0.85 !important; }

    /* RSS 상태 배지 */
    .rss-ok  { color: #2ecc71; font-size: 0.75rem; }
    .rss-err { color: #e74c3c; font-size: 0.75rem; }

    .no-headlines {
        color: #555;
        font-size: 0.83rem;
        font-style: italic;
        text-align: center;
        padding: 1.5rem;
    }
    .fetch-info {
        font-size: 0.72rem;
        color: #444;
        text-align: right;
        margin-top: 0.3rem;
    }
</style>
""", unsafe_allow_html=True)

# ─── 미디어 데이터 (RSS 포함) ───────────────────────────────────────────────────
MEDIA_OUTLETS = {
    "CNN (미국)": {
        "region": "🇺🇸 미국", "leaning": "중도진보",
        "color_css": "#c0392b", "side_key": "red",
        "rss": [
            "http://rss.cnn.com/rss/edition_world.rss",
            "http://rss.cnn.com/rss/edition.rss",
        ],
    },
    "Fox News (미국)": {
        "region": "🇺🇸 미국", "leaning": "보수",
        "color_css": "#e67e22", "side_key": "red",
        "rss": [
            "https://feeds.foxnews.com/foxnews/world",
            "https://feeds.foxnews.com/foxnews/national",
        ],
    },
    "BBC (영국)": {
        "region": "🇬🇧 영국", "leaning": "중립",
        "color_css": "#2471a3", "side_key": "blue",
        "rss": [
            "http://feeds.bbci.co.uk/news/world/rss.xml",
            "http://feeds.bbci.co.uk/news/rss.xml",
        ],
    },
    "Al Jazeera (카타르)": {
        "region": "🇶🇦 카타르", "leaning": "중동시각",
        "color_css": "#27ae60", "side_key": "blue",
        "rss": [
            "https://www.aljazeera.com/xml/rss/all.xml",
            "https://www.aljazeera.com/programs/newsfeed/rss.xml",
        ],
    },
    "Reuters (국제)": {
        "region": "🌐 국제", "leaning": "중립",
        "color_css": "#e74c3c", "side_key": "red",
        "rss": [
            "https://feeds.reuters.com/reuters/worldNews",
            "https://feeds.reuters.com/Reuters/worldNews",
        ],
    },
    "The Guardian (영국)": {
        "region": "🇬🇧 영국", "leaning": "진보",
        "color_css": "#1e8bc3", "side_key": "blue",
        "rss": [
            "https://www.theguardian.com/world/rss",
            "https://www.theguardian.com/rss",
        ],
    },
    "DW (독일)": {
        "region": "🇩🇪 독일", "leaning": "중립",
        "color_css": "#2980b9", "side_key": "blue",
        "rss": [
            "https://rss.dw.com/rdf/rss-en-world",
            "https://rss.dw.com/rdf/rss-en-all",
        ],
    },
    "NHK World (일본)": {
        "region": "🇯🇵 일본", "leaning": "중립",
        "color_css": "#8e44ad", "side_key": "blue",
        "rss": [
            "https://www3.nhk.or.jp/nhkworld/en/news/feeds/",
        ],
    },
    "France 24 (프랑스)": {
        "region": "🇫🇷 프랑스", "leaning": "중립",
        "color_css": "#2c3e7a", "side_key": "blue",
        "rss": [
            "https://www.france24.com/en/rss",
            "https://www.france24.com/en/world/rss",
        ],
    },
    "AP News (미국)": {
        "region": "🇺🇸 미국", "leaning": "중립",
        "color_css": "#c0392b", "side_key": "red",
        "rss": [
            "https://rsshub.app/apnews/world-news",
            "https://apnews.com/index.rss",
        ],
    },
}

# ─── 분쟁 주제 ─────────────────────────────────────────────────────────────────
CONFLICT_TOPICS = {
    "🇷🇺 러시아-우크라이나 전쟁":   ["Russia Ukraine war", "Ukraine military", "Russia NATO"],
    "🇵🇸 가자지구 분쟁":            ["Gaza Israel Hamas", "Palestine conflict", "Gaza ceasefire"],
    "🇹🇼 대만해협 긴장":            ["Taiwan China military", "Taiwan Strait tension", "Taiwan defense"],
    "🌊 남중국해 영유권":            ["South China Sea dispute", "China Philippines sea", "South China Sea military"],
    "🇰🇵 북한 핵·미사일":            ["North Korea missile", "North Korea nuclear", "DPRK military"],
    "🇮🇷 이란 핵 협상":             ["Iran nuclear deal", "Iran sanctions military", "Iran IAEA"],
    "🇦🇫 아프가니스탄 탈레반":        ["Afghanistan Taliban", "Afghanistan military", "Kabul Taliban"],
    "⚔️ 직접 입력":                  [],
}

# ─── RSS 헤드라인 가져오기 ─────────────────────────────────────────────────────
@st.cache_data(ttl=300, show_spinner=False)
def fetch_headlines(media_name: str, keywords: list[str], max_items: int = 12) -> tuple[list[dict], str]:
    """RSS 피드에서 키워드 관련 헤드라인을 가져옴. (API 키 불필요)"""
    outlet = MEDIA_OUTLETS[media_name]
    all_entries = []

    for rss_url in outlet["rss"]:
        try:
            feed = feedparser.parse(rss_url)
            if feed.entries:
                all_entries.extend(feed.entries[:40])
                break
        except Exception:
            continue

    if not all_entries:
        return [], "fetch_failed"

    filtered = []
    kw_lower = [k.lower() for k in keywords]

    for entry in all_entries:
        title   = entry.get("title", "")
        summary = entry.get("summary", "")
        text    = (title + " " + summary).lower()

        if kw_lower and not any(k in text for k in kw_lower):
            continue

        pub = ""
        if hasattr(entry, "published"):
            try:
                pub = entry.published[:16]
            except Exception:
                pub = ""

        filtered.append({
            "title":   title,
            "summary": summary[:180] if summary else "",
            "url":     entry.get("link", ""),
            "date":    pub,
        })

        if len(filtered) >= max_items:
            break

    status = "ok" if filtered else ("no_match" if all_entries else "fetch_failed")
    return filtered, status


def fetch_all_headlines(media_name: str, keywords: list[str]) -> tuple[list[dict], str]:
    """키워드 매칭 우선, 없으면 최신 헤드라인 반환"""
    headlines, status = fetch_headlines(media_name, keywords)
    if not headlines:
        headlines, status = fetch_headlines(media_name, [])  # 키워드 없이 재시도
        if headlines:
            status = "no_match"
    return headlines, status


# ─── Claude 분석 ───────────────────────────────────────────────────────────────
def build_analysis_prompt(media: str, keyword_topic: str, headlines: list[dict]) -> str:
    info = MEDIA_OUTLETS[media]
    headline_block = "\n".join(
        f"- {h['title']}" for h in headlines[:10]
    ) if headlines else "※ 관련 헤드라인을 가져오지 못했습니다."

    return f"""당신은 국제 미디어 편향성·저널리즘 전문 분석가입니다.

분석 대상:
- 미디어: {media} | 지역: {info['region']} | 성향: {info['leaning']}
- 분쟁 주제: {keyword_topic}

아래는 실제 RSS에서 수집한 이 미디어의 최신 헤드라인입니다:
{headline_block}

위 헤드라인들을 근거로 삼아, 반드시 아래 JSON 형식으로만 응답하세요 (마크다운 코드블록 없이, 순수 JSON):

{{
  "media_name": "{media}",
  "overall_stance": "이 미디어의 해당 분쟁 주제 전반적 입장 (2-3문장, 헤드라인 근거 포함)",
  "framing": "헤드라인에서 드러나는 핵심 프레이밍·내러티브 (2-3문장)",
  "tone": "보도 감정 톤 (예: 비판적, 중립적, 지지적, 경고적, 우려 등)",
  "tone_score": {{
    "objectivity": 0에서100 사이 정수,
    "negativity":  0에서100 사이 정수,
    "urgency":     0에서100 사이 정수,
    "bias_toward_west": 0에서100 사이 정수
  }},
  "key_terms": ["헤드라인에 나타나는 핵심 단어/표현 5개 (영어 원문 가능)"],
  "avoided_terms": ["이 미디어가 회피하는 표현 3개"],
  "representative_headline": "위 헤드라인 중 이 미디어 시각을 가장 잘 보여주는 헤드라인 1개 (그대로 인용)",
  "critical_point": "이 보도 방식에서 주목해야 할 비판적 관찰 포인트 (1-2문장)"
}}"""


def build_compare_prompt(media_a: str, media_b: str, res_a: dict, res_b: dict, topic: str) -> str:
    return f"""국제 미디어 비교 분석 전문가로서, 동일 분쟁 주제({topic})에 대한 두 미디어의 실제 헤드라인 분석을 비교합니다.

{media_a}: 입장={res_a.get('overall_stance','')}, 프레이밍={res_a.get('framing','')}, 톤={res_a.get('tone','')}
{media_b}: 입장={res_b.get('overall_stance','')}, 프레이밍={res_b.get('framing','')}, 톤={res_b.get('tone','')}

반드시 아래 JSON 형식으로만 응답 (마크다운 코드블록 없이):
{{
  "core_difference": "두 미디어의 가장 핵심적 시각 차이 (2-3문장)",
  "differences": [
    "구체적 차이점 1",
    "구체적 차이점 2",
    "구체적 차이점 3",
    "구체적 차이점 4"
  ],
  "common_ground": "두 미디어가 공통적으로 인정하는 부분 (1문장)",
  "information_gap": "각 미디어가 의도적으로 누락할 가능성이 있는 정보 (1-2문장)",
  "reading_tip": "이 두 매체를 같이 읽을 때의 미디어 리터러시 조언 (1-2문장)"
}}"""


def safe_parse(text: str) -> dict:
    text = text.strip()
    for fence in ["```json", "```"]:
        if fence in text:
            parts = text.split(fence)
            if len(parts) >= 3:
                text = parts[1]
            else:
                text = text.replace(fence, "")
    text = text.strip()
    try:
        return json.loads(text)
    except Exception:
        # 중괄호 추출 시도
        match = re.search(r'\{.*\}', text, re.DOTALL)
        if match:
            try:
                return json.loads(match.group())
            except Exception:
                pass
    return {}


def call_claude(client, prompt: str) -> str:
    full = ""
    with client.messages.stream(
        model="claude-sonnet-4-20250514",
        max_tokens=1000,
        messages=[{"role": "user", "content": prompt}],
    ) as stream:
        for chunk in stream.text_stream:
            full += chunk
    return full


# ─── UI 렌더 함수 ──────────────────────────────────────────────────────────────
def render_score_bar(label: str, score: int, color: str):
    st.markdown(f"""
    <div class="score-row">
      <div class="score-name"><span>{label}</span><span style="color:#aaa">{score}</span></div>
      <div class="score-track">
        <div class="score-fill" style="width:{score}%;background:{color}"></div>
      </div>
    </div>
    """, unsafe_allow_html=True)


def render_headlines_panel(media_name: str, headlines: list[dict], status: str, color: str):
    count = len(headlines)
    if status == "ok":
        st.markdown(f'<span class="rss-ok">● RSS 수집 완료 ({count}건)</span>', unsafe_allow_html=True)
    elif status == "no_match":
        st.markdown(f'<span class="rss-err">● 키워드 매칭 없음 — 최신 헤드라인 표시 ({count}건)</span>', unsafe_allow_html=True)
    else:
        st.markdown(f'<span class="rss-err">● RSS 수집 실패</span>', unsafe_allow_html=True)

    if headlines:
        for h in headlines[:8]:
            st.markdown(f"""
            <div class="headline-item">
              <span class="headline-source-badge" style="background:{color}22;color:{color}">{media_name.split(' ')[0]}</span>
              {h['title']}
              <div class="headline-date">{h['date']}</div>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.markdown('<div class="no-headlines">헤드라인을 가져오지 못했습니다.<br>RSS 피드 접속이 차단됐거나 일시적 오류일 수 있습니다.</div>', unsafe_allow_html=True)

    st.markdown(f'<div class="fetch-info">최근 5분 캐시 적용</div>', unsafe_allow_html=True)


def render_analysis_card(result: dict, side: str):
    if not result:
        st.error("분석 결과를 파싱하지 못했습니다.")
        return

    info = MEDIA_OUTLETS.get(result.get("media_name", ""), {})
    color = info.get("color_css", "#888")
    tone_color = "#e87474" if side == "red" else "#74b4e8"

    terms_html = "".join(
        f'<span class="term-tag term-used-{side}">{t}</span>'
        for t in result.get("key_terms", [])
    )
    avoided_html = "".join(
        f'<span class="term-tag term-avoided">{t}</span>'
        for t in result.get("avoided_terms", [])
    )

    scores = result.get("tone_score", {})
    label_icon = "🔴" if side == "red" else "🔵"

    st.markdown(f"""
    <div class="analysis-card analysis-card-{side}">
      <div class="card-header">{label_icon} {result.get('media_name','')}</div>
      <div class="card-region">{info.get('region','')} · {info.get('leaning','')}</div>

      <div class="section-label">전반적 입장</div>
      <div class="section-content">{result.get('overall_stance','')}</div>

      <div class="section-label">보도 프레이밍</div>
      <div class="section-content">{result.get('framing','')}</div>

      <div class="section-label">감정 톤</div>
      <span class="tone-pill" style="background:{tone_color}22;color:{tone_color};border:1px solid {tone_color}44">
        {result.get('tone','')}
      </span>
    </div>
    """, unsafe_allow_html=True)

    # 스코어 바
    if scores:
        st.markdown("<div style='height:0.6rem'></div>", unsafe_allow_html=True)
        render_score_bar("객관성",        scores.get("objectivity", 50),      color)
        render_score_bar("부정성",        scores.get("negativity", 50),       color)
        render_score_bar("긴급성",        scores.get("urgency", 50),          color)
        render_score_bar("서방 편향도",   scores.get("bias_toward_west", 50), color)

    # 용어 + 대표 헤드라인 + 비판 포인트
    rep_hl = result.get("representative_headline", "")
    critical = result.get("critical_point", "")
    st.markdown(f"""
    <div style="margin-top:0.7rem;background:rgba(255,255,255,0.03);
                border-radius:8px;padding:0.9rem;border:1px solid rgba(255,255,255,0.06)">
      <div class="section-label">주요 사용 용어</div>
      {terms_html}
      <div class="section-label" style="margin-top:0.7rem">회피 용어</div>
      {avoided_html}
      <div class="section-label" style="margin-top:0.7rem">대표 헤드라인</div>
      <div class="headline-quote">「{rep_hl}」</div>
      <div class="section-label" style="margin-top:0.7rem">비판적 관찰</div>
      <div style="font-size:0.82rem;color:#e8a87c;line-height:1.6">{critical}</div>
    </div>
    """, unsafe_allow_html=True)


# ─── 사이드바 ──────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## ⚙️ 분석 설정")
    st.markdown("---")

    api_key = st.text_input("🔑 Anthropic API Key", type="password", placeholder="sk-ant-...")
    st.caption("헤드라인 수집은 무료 RSS 사용\nAI 분석에만 API 키가 필요합니다")
    st.markdown("---")

    st.markdown("### 📌 분쟁 주제")
    selected_topic = st.selectbox("주제 선택", list(CONFLICT_TOPICS.keys()))

    if selected_topic == "⚔️ 직접 입력":
        custom_kw = st.text_input("키워드 (영어 권장)", placeholder="예: Sudan civil war")
        keywords  = [w.strip() for w in custom_kw.split(",") if w.strip()] if custom_kw else []
        topic_display = custom_kw or "직접 입력"
    else:
        keywords      = CONFLICT_TOPICS[selected_topic]
        topic_display = selected_topic

    st.markdown("---")

    st.markdown("### 📺 비교 미디어")
    media_list = list(MEDIA_OUTLETS.keys())
    col_a, col_b = st.columns(2)
    with col_a:
        st.markdown("**🔴 A**")
        media_a = st.selectbox("", media_list, index=0, key="sel_a", label_visibility="collapsed")
    with col_b:
        st.markdown("**🔵 B**")
        media_b = st.selectbox("", media_list, index=2, key="sel_b", label_visibility="collapsed")

    if media_a == media_b:
        st.warning("서로 다른 미디어를 선택하세요")

    st.markdown("---")

    can_analyze = bool(api_key) and media_a != media_b and bool(keywords or selected_topic != "⚔️ 직접 입력")
    analyze_btn = st.button("🚀 분석 시작", disabled=not can_analyze)

    if not api_key:
        st.info("API 키를 입력하면\n분석이 활성화됩니다")

# ─── 헤더 ──────────────────────────────────────────────────────────────────────
st.markdown('<div class="main-title">⚔️ GLOBAL CONFLICT MEDIA LENS</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">같은 분쟁 · 다른 시각 — RSS 실시간 헤드라인 + Claude AI 분석</div>', unsafe_allow_html=True)

# ─── 헤드라인 미리보기 (항상 표시) ────────────────────────────────────────────
if keywords or selected_topic != "⚔️ 직접 입력":
    with st.expander(f"📰 실시간 헤드라인 미리보기 — {media_a} vs {media_b}", expanded=False):
        p1, p2 = st.columns(2)
        with p1:
            st.markdown(f"**{media_a}**")
            with st.spinner("RSS 수집 중..."):
                hl_a, st_a = fetch_all_headlines(media_a, keywords)
            render_headlines_panel(media_a, hl_a, st_a, MEDIA_OUTLETS[media_a]["color_css"])
        with p2:
            st.markdown(f"**{media_b}**")
            with st.spinner("RSS 수집 중..."):
                hl_b, st_b = fetch_all_headlines(media_b, keywords)
            render_headlines_panel(media_b, hl_b, st_b, MEDIA_OUTLETS[media_b]["color_css"])

# ─── 분석 실행 ─────────────────────────────────────────────────────────────────
if analyze_btn:
    client = anthropic.Anthropic(api_key=api_key)
    st.markdown("---")
    st.markdown(f"## 📊 {topic_display} &nbsp;·&nbsp; {media_a} vs {media_b}")

    # 헤드라인 수집
    with st.spinner("RSS 헤드라인 수집 중..."):
        hl_a, st_a = fetch_all_headlines(media_a, keywords)
        hl_b, st_b = fetch_all_headlines(media_b, keywords)

    col1, col2 = st.columns(2)
    result_a, result_b = {}, {}

    with col1:
        with st.spinner(f"🔴 {media_a} 분석 중..."):
            raw_a = call_claude(client, build_analysis_prompt(media_a, topic_display, hl_a))
            result_a = safe_parse(raw_a)
        render_analysis_card(result_a, "red")

    with col2:
        with st.spinner(f"🔵 {media_b} 분석 중..."):
            raw_b = call_claude(client, build_analysis_prompt(media_b, topic_display, hl_b))
            result_b = safe_parse(raw_b)
        render_analysis_card(result_b, "blue")

    # 종합 비교
    if result_a and result_b:
        with st.spinner("⚖️ 종합 비교 분석 중..."):
            raw_c   = call_claude(client, build_compare_prompt(media_a, media_b, result_a, result_b, topic_display))
            compare = safe_parse(raw_c)

        if compare:
            diffs_html = "".join(
                f'<div class="diff-item">▸ {d}</div>' for d in compare.get("differences", [])
            )
            st.markdown(f"""
            <div class="compare-section">
              <div class="compare-title">⚖ COMPARATIVE ANALYSIS</div>

              <div class="section-label">핵심 시각 차이</div>
              <div class="section-content" style="color:#e8d5a3;margin-bottom:1rem">
                {compare.get('core_difference','')}
              </div>

              <div class="section-label">세부 차이점</div>
              {diffs_html}

              <div class="info-grid">
                <div class="info-box">
                  <div class="section-label">공통 인식</div>
                  <div style="font-size:0.83rem;color:#999;line-height:1.6">{compare.get('common_ground','')}</div>
                </div>
                <div class="info-box">
                  <div class="section-label">정보 공백 가능성</div>
                  <div style="font-size:0.83rem;color:#999;line-height:1.6">{compare.get('information_gap','')}</div>
                </div>
              </div>

              <div class="tip-box">
                📚 <strong>미디어 리터러시 조언</strong><br>
                {compare.get('reading_tip','')}
              </div>
            </div>
            """, unsafe_allow_html=True)

        # 점수 비교 차트
        import plotly.graph_objects as go

        scores_a = result_a.get("tone_score", {})
        scores_b = result_b.get("tone_score", {})
        cats = ["객관성", "부정성", "긴급성", "서방편향도"]
        keys = ["objectivity", "negativity", "urgency", "bias_toward_west"]

        fig = go.Figure()
        fig.add_trace(go.Bar(
            name=media_a, x=cats, y=[scores_a.get(k, 50) for k in keys],
            marker_color=MEDIA_OUTLETS[media_a]["color_css"], opacity=0.85,
        ))
        fig.add_trace(go.Bar(
            name=media_b, x=cats, y=[scores_b.get(k, 50) for k in keys],
            marker_color=MEDIA_OUTLETS[media_b]["color_css"], opacity=0.85,
        ))
        fig.update_layout(
            barmode="group", height=300,
            plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
            font=dict(color="#aaa", family="Noto Sans KR"),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1,
                        font=dict(color="#aaa")),
            yaxis=dict(range=[0, 100], gridcolor="rgba(255,255,255,0.05)", color="#666"),
            xaxis=dict(color="#666"),
            margin=dict(t=10, b=10, l=10, r=10),
        )
        st.markdown("<div style='height:1rem'></div>", unsafe_allow_html=True)
        st.markdown("### 📈 보도 성향 점수 비교")
        st.plotly_chart(fig, use_container_width=True)

# ─── 초기 안내 ──────────────────────────────────────────────────────────────────
elif not analyze_btn:
    st.markdown("""
    <div style="text-align:center;padding:4rem 2rem;color:#444">
      <div style="font-size:4rem;margin-bottom:1rem">📡</div>
      <p style="font-size:1rem;color:#555;margin-bottom:0.4rem">① <b style="color:#888">API 키</b> 입력 &nbsp;→&nbsp; ② <b style="color:#888">분쟁 주제</b> 선택 &nbsp;→&nbsp; ③ <b style="color:#888">미디어 2개</b> 선택 &nbsp;→&nbsp; ④ 분석 시작</p>
      <p style="font-size:0.8rem;color:#3a3a4a;margin-top:1.5rem">
        헤드라인 수집은 무료 RSS · AI 분석은 Claude Sonnet 4 사용
      </p>
    </div>
    """, unsafe_allow_html=True)
