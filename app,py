# app.py
import streamlit as st
import anthropic
import json
import time

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
    @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@400;600;700&display=swap');
    html, body, [class*="css"] { font-family: 'Noto Sans KR', sans-serif; }

    .main-title {
        text-align: center;
        font-size: 2.2rem;
        font-weight: 700;
        background: linear-gradient(135deg, #1a1a2e, #16213e, #0f3460);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.3rem;
    }
    .subtitle {
        text-align: center;
        color: #666;
        font-size: 0.95rem;
        margin-bottom: 2rem;
    }
    .media-card {
        background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
        border-radius: 16px;
        padding: 1.5rem;
        color: white;
        height: 100%;
        box-shadow: 0 8px 32px rgba(0,0,0,0.2);
    }
    .media-card h3 {
        font-size: 1.1rem;
        font-weight: 700;
        border-bottom: 2px solid rgba(255,255,255,0.15);
        padding-bottom: 0.5rem;
        margin-bottom: 1rem;
    }
    .media-card-left { border-top: 4px solid #e74c3c; }
    .media-card-right { border-top: 4px solid #3498db; }

    .tag {
        display: inline-block;
        padding: 3px 10px;
        border-radius: 20px;
        font-size: 0.78rem;
        margin: 3px 2px;
    }
    .tag-red   { background: rgba(231,76,60,0.25);  color: #ff6b6b; border: 1px solid rgba(231,76,60,0.4); }
    .tag-blue  { background: rgba(52,152,219,0.25); color: #74b9ff; border: 1px solid rgba(52,152,219,0.4); }
    .tag-gray  { background: rgba(255,255,255,0.1); color: #ccc;    border: 1px solid rgba(255,255,255,0.2); }

    .score-bar-wrap { margin: 0.4rem 0; }
    .score-label { font-size: 0.82rem; color: #aaa; margin-bottom: 2px; }
    .score-bar { height: 8px; border-radius: 4px; background: rgba(255,255,255,0.1); }
    .score-fill-red  { height: 8px; border-radius: 4px; background: linear-gradient(90deg,#e74c3c,#ff6b6b); }
    .score-fill-blue { height: 8px; border-radius: 4px; background: linear-gradient(90deg,#3498db,#74b9ff); }

    .compare-box {
        background: linear-gradient(135deg, #0f3460 0%, #16213e 100%);
        border-radius: 16px;
        padding: 1.5rem;
        color: white;
        margin-top: 1.5rem;
        box-shadow: 0 8px 32px rgba(0,0,0,0.2);
        border-top: 4px solid #f39c12;
    }
    .compare-box h3 { font-size: 1.05rem; font-weight: 700; margin-bottom: 1rem; }
    .diff-item {
        background: rgba(255,255,255,0.06);
        border-left: 3px solid #f39c12;
        border-radius: 0 8px 8px 0;
        padding: 0.6rem 0.9rem;
        margin-bottom: 0.6rem;
        font-size: 0.88rem;
        line-height: 1.6;
    }
    .stButton>button {
        background: linear-gradient(135deg, #e74c3c, #c0392b);
        color: white;
        border: none;
        border-radius: 10px;
        padding: 0.6rem 2.5rem;
        font-size: 1rem;
        font-weight: 700;
        width: 100%;
        cursor: pointer;
        transition: opacity 0.2s;
    }
    .stButton>button:hover { opacity: 0.85; }
    .keyword-badge {
        display: inline-block;
        background: linear-gradient(135deg,#e74c3c,#c0392b);
        color: white;
        padding: 4px 14px;
        border-radius: 20px;
        font-size: 0.85rem;
        font-weight: 600;
        margin-bottom: 1.2rem;
    }
    .section-title {
        font-size: 0.78rem;
        color: rgba(255,255,255,0.5);
        text-transform: uppercase;
        letter-spacing: 1px;
        margin: 1rem 0 0.4rem;
    }
</style>
""", unsafe_allow_html=True)

# ─── 데이터 ────────────────────────────────────────────────────────────────────
MEDIA_OUTLETS = {
    "CNN (미국)":           {"region": "🇺🇸 미국", "leaning": "중도진보", "color": "#e74c3c"},
    "Fox News (미국)":      {"region": "🇺🇸 미국", "leaning": "보수",     "color": "#e67e22"},
    "BBC (영국)":           {"region": "🇬🇧 영국", "leaning": "중립",     "color": "#3498db"},
    "Al Jazeera (카타르)":  {"region": "🇶🇦 카타르","leaning": "중동시각", "color": "#27ae60"},
    "RT (러시아)":          {"region": "🇷🇺 러시아","leaning": "친러",     "color": "#8e44ad"},
    "CGTN (중국)":          {"region": "🇨🇳 중국", "leaning": "친중",     "color": "#c0392b"},
    "NYT (미국)":           {"region": "🇺🇸 미국", "leaning": "중도진보", "color": "#2980b9"},
    "조선일보 (한국)":       {"region": "🇰🇷 한국", "leaning": "보수",     "color": "#e74c3c"},
    "한겨레 (한국)":         {"region": "🇰🇷 한국", "leaning": "진보",     "color": "#27ae60"},
    "Sputnik (러시아)":     {"region": "🇷🇺 러시아","leaning": "친러",     "color": "#6c3483"},
}

CONFLICT_TOPICS = {
    "🇷🇺 러시아-우크라이나 전쟁": "러시아 우크라이나 전쟁 군사 작전 NATO",
    "🇵🇸 가자지구 분쟁":         "이스라엘 하마스 가자지구 팔레스타인 군사 작전",
    "🇹🇼 대만해협 긴장":         "대만 중국 군사 긴장 해협 분쟁",
    "🌊 남중국해 영유권":        "남중국해 영유권 분쟁 군사 중국 미국",
    "🇰🇵 북한 핵·미사일 도발":   "북한 핵 미사일 도발 한반도 안보",
    "🇮🇷 이란 핵 협상":          "이란 핵 협상 제재 중동 군사 긴장",
    "⚔️ 직접 입력":             "",
}

# ─── 제목 ──────────────────────────────────────────────────────────────────────
st.markdown('<div class="main-title">⚔️ 글로벌 분쟁 미디어 시각 비교 분석</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">같은 분쟁을 세계 주요 언론은 어떻게 다르게 보도할까? — Claude AI 실시간 분석</div>', unsafe_allow_html=True)

# ─── 사이드바 ──────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## ⚙️ 분석 설정")
    st.markdown("---")

    # API 키
    api_key = st.text_input("🔑 Anthropic API Key", type="password", placeholder="sk-ant-...")
    st.markdown("---")

    # 토픽 선택
    st.markdown("### 📌 분쟁 주제 선택")
    selected_topic = st.selectbox("분쟁 주제", list(CONFLICT_TOPICS.keys()))

    if selected_topic == "⚔️ 직접 입력":
        custom_keyword = st.text_input("키워드 직접 입력", placeholder="예: 아프가니스탄 탈레반")
        keyword = custom_keyword
    else:
        keyword = CONFLICT_TOPICS[selected_topic]
        st.caption(f"🔎 검색 키워드: `{keyword}`")

    st.markdown("---")

    # 미디어 선택
    st.markdown("### 📺 비교할 미디어 선택")
    media_list = list(MEDIA_OUTLETS.keys())

    col_a, col_b = st.columns(2)
    with col_a:
        st.markdown("**🔴 미디어 A**")
        media_a = st.selectbox("", media_list, index=0, key="media_a", label_visibility="collapsed")
    with col_b:
        st.markdown("**🔵 미디어 B**")
        media_b = st.selectbox("", media_list, index=2, key="media_b", label_visibility="collapsed")

    if media_a == media_b:
        st.warning("⚠️ 서로 다른 미디어를 선택하세요.")

    st.markdown("---")

    # 분석 깊이
    st.markdown("### 🔬 분석 깊이")
    depth = st.radio("", ["빠른 분석", "심층 분석"], index=0, horizontal=True, label_visibility="collapsed")

    st.markdown("---")
    analyze_btn = st.button("🚀 비교 분석 시작", disabled=(not api_key or media_a == media_b or not keyword))

# ─── 분석 함수 ──────────────────────────────────────────────────────────────────
def build_prompt(media: str, keyword: str, depth: str) -> str:
    detail = "간결하게 핵심만" if depth == "빠른 분석" else "상세하게"
    info = MEDIA_OUTLETS[media]
    return f"""당신은 미디어 편향성 및 국제 저널리즘 전문 분석가입니다.

분석 대상:
- 미디어: {media} ({info['region']}, 성향: {info['leaning']})
- 주제/키워드: {keyword}

다음 항목을 {detail} 분석하여 반드시 아래 JSON 형식으로만 응답하세요 (마크다운 코드블록 없이 순수 JSON):

{{
  "media_name": "{media}",
  "overall_stance": "해당 미디어의 이 사안에 대한 전반적 입장 (2-3문장)",
  "framing": "이 미디어가 사용할 핵심 프레이밍/내러티브 (2-3문장)",
  "tone": "보도 감정 톤 (예: 비판적, 중립적, 지지적, 경고적 등)",
  "tone_score": {{
    "objectivity": 0~100 사이 숫자,
    "negativity": 0~100 사이 숫자,
    "urgency": 0~100 사이 숫자,
    "national_interest_bias": 0~100 사이 숫자
  }},
  "key_terms": ["이 미디어가 주로 사용할 단어/표현 5개"],
  "avoided_terms": ["이 미디어가 피할 단어/표현 3개"],
  "typical_sources": ["주로 인용할 소식통 3가지"],
  "key_differences_preview": "다른 미디어와 비교해 가장 두드러질 차이점 (1-2문장)",
  "example_headline": "이 미디어 스타일로 작성한 예시 헤드라인 (한국어)",
  "critical_point": "이 보도에서 가장 중요한 비판적 관찰 포인트"
}}"""

def build_compare_prompt(media_a: str, media_b: str, result_a: dict, result_b: dict, keyword: str) -> str:
    return f"""미디어 분석 전문가로서, 동일한 주제({keyword})에 대한 두 미디어의 보도 성향 비교 분석 결과를 제공하세요.

미디어 A ({media_a}):
- 입장: {result_a.get('overall_stance','')}
- 프레이밍: {result_a.get('framing','')}
- 톤: {result_a.get('tone','')}
- 핵심 용어: {result_a.get('key_terms',[])}

미디어 B ({media_b}):
- 입장: {result_b.get('overall_stance','')}
- 프레이밍: {result_b.get('framing','')}
- 톤: {result_b.get('tone','')}
- 핵심 용어: {result_b.get('key_terms',[])}

반드시 아래 JSON 형식으로만 응답 (마크다운 코드블록 없이):
{{
  "core_difference": "두 미디어의 가장 핵심적인 시각 차이 (2-3문장)",
  "differences": [
    "구체적 차이점 1",
    "구체적 차이점 2",
    "구체적 차이점 3",
    "구체적 차이점 4"
  ],
  "common_ground": "두 미디어가 공통적으로 동의할 부분",
  "information_gap": "각 미디어가 의도적으로 누락할 가능성이 있는 정보",
  "reading_tip": "독자에게 주는 미디어 리터러시 조언 (1-2문장)"
}}"""

def safe_parse(text: str) -> dict:
    text = text.strip()
    # 마크다운 코드블록 제거
    for fence in ["```json", "```"]:
        if fence in text:
            text = text.split(fence)[-2] if text.count(fence) >= 2 else text.replace(fence, "")
    try:
        return json.loads(text.strip())
    except Exception:
        return {}

def call_claude(client, prompt: str) -> str:
    full = ""
    with client.messages.stream(
        model="claude-sonnet-4-20250514",
        max_tokens=1000,
        messages=[{"role": "user", "content": prompt}],
    ) as stream:
        for text in stream.text_stream:
            full += text
    return full

def render_score_bar(label: str, score: int, color_class: str):
    st.markdown(f"""
    <div class="score-bar-wrap">
      <div class="score-label">{label} <span style="float:right;color:#eee;font-weight:600">{score}</span></div>
      <div class="score-bar">
        <div class="score-fill-{color_class}" style="width:{score}%"></div>
      </div>
    </div>
    """, unsafe_allow_html=True)

def render_media_card(result: dict, side: str):
    tags_html = "".join(
        f'<span class="tag tag-{"red" if side=="left" else "blue"}">{t}</span>'
        for t in result.get("key_terms", [])
    )
    avoided_html = "".join(
        f'<span class="tag tag-gray">{t}</span>'
        for t in result.get("avoided_terms", [])
    )
    sources_html = "".join(
        f'<li style="font-size:0.83rem;color:#bbb;margin-bottom:3px">{s}</li>'
        for s in result.get("typical_sources", [])
    )
    scores = result.get("tone_score", {})
    color = "red" if side == "left" else "blue"

    html = f"""
    <div class="media-card media-card-{side}">
      <h3>{'🔴' if side=='left' else '🔵'} {result.get('media_name','')}</h3>
      <div class="keyword-badge">📌 {keyword[:30]}</div>

      <div class="section-title">전반적 입장</div>
      <p style="font-size:0.87rem;color:#ddd;line-height:1.65">{result.get('overall_stance','')}</p>

      <div class="section-title">보도 프레이밍</div>
      <p style="font-size:0.87rem;color:#ddd;line-height:1.65">{result.get('framing','')}</p>

      <div class="section-title">감정 톤 &nbsp;<span style="background:rgba(255,255,255,0.15);padding:2px 8px;border-radius:10px;font-size:0.8rem">{result.get('tone','')}</span></div>
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)

    # 스코어 바는 st 컴포넌트로
    if scores:
        with st.container():
            st.markdown(f"""
            <div style="background:rgba(255,255,255,0.04);border-radius:0 0 12px 12px;
                        padding:0.8rem 1.2rem;margin-top:-8px">
            """, unsafe_allow_html=True)
            render_score_bar("객관성", scores.get("objectivity", 50), color)
            render_score_bar("부정성", scores.get("negativity", 50), color)
            render_score_bar("긴급성", scores.get("urgency", 50), color)
            render_score_bar("자국이익 편향", scores.get("national_interest_bias", 50), color)
            st.markdown("</div>", unsafe_allow_html=True)

    st.markdown(f"""
    <div class="media-card" style="margin-top:0.5rem;border-radius:12px;padding:1rem 1.2rem;background:rgba(255,255,255,0.04)">
      <div class="section-title">주요 사용 용어</div>
      {tags_html}
      <div class="section-title" style="margin-top:0.8rem">회피 용어</div>
      {avoided_html}
      <div class="section-title" style="margin-top:0.8rem">주요 인용 소식통</div>
      <ul style="padding-left:1rem;margin:0">{sources_html}</ul>
      <div class="section-title" style="margin-top:0.8rem">예상 헤드라인</div>
      <p style="font-size:0.85rem;color:#f1c40f;font-style:italic;line-height:1.6">
        「{result.get('example_headline','')}」
      </p>
      <div class="section-title">비판적 관찰 포인트</div>
      <p style="font-size:0.83rem;color:#e8a87c;line-height:1.6">{result.get('critical_point','')}</p>
    </div>
    """, unsafe_allow_html=True)

# ─── 메인 분석 실행 ────────────────────────────────────────────────────────────
if analyze_btn:
    client = anthropic.Anthropic(api_key=api_key)

    st.markdown("---")
    st.markdown(f"## 📊 **{selected_topic}** — {media_a} vs {media_b} 비교 분석")

    col1, col2 = st.columns(2)
    result_a, result_b = {}, {}

    with col1:
        with st.spinner(f"🔴 {media_a} 분석 중..."):
            raw_a = call_claude(client, build_prompt(media_a, keyword, depth))
            result_a = safe_parse(raw_a)
        if result_a:
            render_media_card(result_a, "left")
        else:
            st.error("분석 결과를 파싱하지 못했습니다.")

    with col2:
        with st.spinner(f"🔵 {media_b} 분석 중..."):
            raw_b = call_claude(client, build_prompt(media_b, keyword, depth))
            result_b = safe_parse(raw_b)
        if result_b:
            render_media_card(result_b, "right")
        else:
            st.error("분석 결과를 파싱하지 못했습니다.")

    # 비교 분석
    if result_a and result_b:
        with st.spinner("🔍 종합 비교 분석 중..."):
            raw_c = call_claude(client, build_compare_prompt(media_a, media_b, result_a, result_b, keyword))
            compare = safe_parse(raw_c)

        if compare:
            diffs_html = "".join(
                f'<div class="diff-item">• {d}</div>' for d in compare.get("differences", [])
            )
            st.markdown(f"""
            <div class="compare-box">
              <h3>⚖️ 종합 비교 분석</h3>

              <div class="section-title" style="color:rgba(255,255,255,0.5)">핵심 시각 차이</div>
              <p style="color:#f1c40f;font-size:0.9rem;line-height:1.65;margin-bottom:1rem">
                {compare.get('core_difference','')}
              </p>

              <div class="section-title" style="color:rgba(255,255,255,0.5)">세부 차이점</div>
              {diffs_html}

              <div style="display:grid;grid-template-columns:1fr 1fr;gap:1rem;margin-top:1rem">
                <div style="background:rgba(255,255,255,0.05);border-radius:10px;padding:0.9rem">
                  <div class="section-title">공통 인식</div>
                  <p style="font-size:0.84rem;color:#aaa;line-height:1.6;margin:0">
                    {compare.get('common_ground','')}
                  </p>
                </div>
                <div style="background:rgba(255,255,255,0.05);border-radius:10px;padding:0.9rem">
                  <div class="section-title">정보 공백 가능성</div>
                  <p style="font-size:0.84rem;color:#aaa;line-height:1.6;margin:0">
                    {compare.get('information_gap','')}
                  </p>
                </div>
              </div>

              <div style="margin-top:1rem;background:rgba(243,156,18,0.12);border-radius:10px;
                          padding:0.9rem;border:1px solid rgba(243,156,18,0.3)">
                <div class="section-title">📚 미디어 리터러시 조언</div>
                <p style="font-size:0.87rem;color:#f39c12;line-height:1.65;margin:0">
                  {compare.get('reading_tip','')}
                </p>
              </div>
            </div>
            """, unsafe_allow_html=True)

        # 시각화 차트
        st.markdown("### 📈 보도 성향 점수 비교")
        import pandas as pd
        import plotly.graph_objects as go

        scores_a = result_a.get("tone_score", {})
        scores_b = result_b.get("tone_score", {})
        categories = ["객관성", "부정성", "긴급성", "자국이익 편향"]
        keys      = ["objectivity", "negativity", "urgency", "national_interest_bias"]

        vals_a = [scores_a.get(k, 50) for k in keys]
        vals_b = [scores_b.get(k, 50) for k in keys]

        fig = go.Figure()
        fig.add_trace(go.Bar(name=media_a, x=categories, y=vals_a,
                             marker_color="#e74c3c", opacity=0.85))
        fig.add_trace(go.Bar(name=media_b, x=categories, y=vals_b,
                             marker_color="#3498db", opacity=0.85))
        fig.update_layout(
            barmode="group",
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
            font=dict(color="#333"),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
            height=320,
            margin=dict(t=20, b=20, l=20, r=20),
            yaxis=dict(range=[0, 100], gridcolor="rgba(0,0,0,0.1)"),
        )
        st.plotly_chart(fig, use_container_width=True)

# ─── 초기 안내 ──────────────────────────────────────────────────────────────────
else:
    st.markdown("""
    <div style="text-align:center;padding:3rem 1rem;color:#888">
      <div style="font-size:3rem">⚔️</div>
      <h3 style="color:#444;margin:1rem 0 0.5rem">사용 방법</h3>
      <p>① 왼쪽 사이드바에서 <b>API 키</b>를 입력하세요</p>
      <p>② <b>분쟁 주제</b>를 선택하세요 (러-우크라이나, 가자지구 등)</p>
      <p>③ 비교할 <b>미디어 2개</b>를 선택하세요 (예: CNN vs RT)</p>
      <p>④ <b>비교 분석 시작</b> 버튼을 누르세요</p>
      <br>
      <p style="font-size:0.85rem;color:#aaa">
        🤖 Claude AI가 각 미디어의 보도 프레이밍, 감정 톤, 핵심 용어, 편향성을 실시간으로 분석합니다
      </p>
    </div>
    """, unsafe_allow_html=True)
