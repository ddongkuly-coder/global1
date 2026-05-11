import streamlit as st
import feedparser
import re
from collections import Counter
from datetime import datetime

# ─── 페이지 설정 ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="⚔️ 글로벌 분쟁 미디어 비교",
    page_icon="⚔️",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@300;400;600;700&family=Bebas+Neue&display=swap');
html, body, [class*="css"] { font-family: 'Noto Sans KR', sans-serif; }

.stApp {
    background: #09090f;
    background-image:
        radial-gradient(ellipse at 15% 50%, rgba(160,20,20,0.07) 0%, transparent 55%),
        radial-gradient(ellipse at 85% 20%, rgba(20,50,160,0.07) 0%, transparent 55%);
}
[data-testid="stSidebar"] { background: #0c0c14 !important; border-right: 1px solid rgba(255,255,255,0.06); }
[data-testid="stSidebar"] label, [data-testid="stSidebar"] p { color: #aaa !important; }

.main-title {
    font-family:'Bebas Neue',sans-serif; text-align:center;
    font-size:2.8rem; letter-spacing:5px; color:#f0f0f0;
    text-shadow:0 0 40px rgba(200,30,30,0.35); margin-bottom:.2rem;
}
.subtitle { text-align:center; color:#555; font-size:.8rem; letter-spacing:2px; text-transform:uppercase; margin-bottom:2rem; }

.hl-card {
    background:rgba(255,255,255,0.03); border:1px solid rgba(255,255,255,0.07);
    border-radius:8px; padding:.6rem .9rem; margin-bottom:.45rem;
    font-size:.83rem; color:#ccc; line-height:1.55;
}
.hl-date { font-size:.68rem; color:#484848; margin-top:3px; }
.src-badge {
    display:inline-block; font-size:.66rem; padding:1px 7px;
    border-radius:3px; margin-right:6px; font-weight:700; vertical-align:middle;
}
.acard {
    background:#101018; border:1px solid rgba(255,255,255,0.09);
    border-radius:14px; padding:1.3rem; margin-bottom:.7rem;
}
.acard-red  { border-top:3px solid #c0392b; }
.acard-blue { border-top:3px solid #2471a3; }
.acard-gold { border-top:3px solid #d4ac0d; margin-top:1.4rem; }

.card-title { font-size:1rem; font-weight:700; color:#f0f0f0; margin-bottom:.2rem; }
.card-sub   { font-size:.73rem; color:#555; padding-bottom:.7rem; border-bottom:1px solid rgba(255,255,255,0.06); margin-bottom:.9rem; }
.slabel     { font-size:.66rem; color:#555; text-transform:uppercase; letter-spacing:1.5px; margin:.8rem 0 .3rem; }
.scontent   { font-size:.83rem; color:#bbb; line-height:1.65; }

.tone-pill {
    display:inline-block; padding:3px 12px; border-radius:20px;
    font-size:.76rem; font-weight:600;
}
.term-tag {
    display:inline-block; padding:2px 8px; border-radius:4px;
    font-size:.73rem; margin:2px; border:1px solid;
}
.t-red  { color:#e87474; border-color:rgba(200,60,60,.3);  background:rgba(200,60,60,.1); }
.t-blue { color:#74b4e8; border-color:rgba(60,100,200,.3); background:rgba(60,100,200,.1); }
.t-gray { color:#777;    border-color:rgba(255,255,255,.1); background:rgba(255,255,255,.04); }
.t-gold { color:#d4ac0d; border-color:rgba(212,172,13,.3); background:rgba(212,172,13,.08); }

.score-row { margin:.32rem 0; }
.score-lbl { font-size:.73rem; color:#666; display:flex; justify-content:space-between; margin-bottom:2px; }
.score-track { height:5px; background:rgba(255,255,255,.07); border-radius:3px; }
.score-fill  { height:5px; border-radius:3px; }

.diff-item {
    background:rgba(255,255,255,.03); border-left:2px solid rgba(212,172,13,.4);
    border-radius:0 6px 6px 0; padding:.5rem .85rem;
    margin-bottom:.45rem; font-size:.83rem; color:#bbb; line-height:1.6;
}
.info-grid { display:grid; grid-template-columns:1fr 1fr; gap:.9rem; margin-top:.9rem; }
.info-box  { background:rgba(255,255,255,.03); border-radius:8px; padding:.85rem; border:1px solid rgba(255,255,255,.06); }
.tip-box   { background:rgba(212,172,13,.07); border:1px solid rgba(212,172,13,.2); border-radius:8px; padding:.85rem; margin-top:.9rem; font-size:.84rem; color:#d4ac0d; line-height:1.65; }
.hl-quote  { font-style:italic; color:#d4ac0d; font-size:.82rem; line-height:1.6; }

.rss-ok  { color:#2ecc71; font-size:.73rem; }
.rss-err { color:#e74c3c; font-size:.73rem; }
.no-hl   { color:#444; font-size:.82rem; font-style:italic; text-align:center; padding:1.5rem; }

.stButton>button {
    background:linear-gradient(135deg,#7b0000,#b03020) !important;
    color:white !important; border:none !important; border-radius:8px !important;
    font-weight:700 !important; width:100% !important; padding:.6rem 1rem !important;
    letter-spacing:1px !important;
}
.stButton>button:hover { opacity:.85 !important; }
</style>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# 데이터 정의
# ══════════════════════════════════════════════════════════════════════════════
MEDIA_OUTLETS = {
    "CNN (미국)":           {"region":"🇺🇸 미국",   "leaning":"중도진보", "color":"#c0392b",
                             "rss":["http://rss.cnn.com/rss/edition_world.rss",
                                    "http://rss.cnn.com/rss/edition.rss"]},
    "Fox News (미국)":      {"region":"🇺🇸 미국",   "leaning":"보수",    "color":"#e67e22",
                             "rss":["https://feeds.foxnews.com/foxnews/world",
                                    "https://feeds.foxnews.com/foxnews/national"]},
    "BBC (영국)":           {"region":"🇬🇧 영국",   "leaning":"중립",    "color":"#2471a3",
                             "rss":["http://feeds.bbci.co.uk/news/world/rss.xml",
                                    "http://feeds.bbci.co.uk/news/rss.xml"]},
    "Al Jazeera (카타르)":  {"region":"🇶🇦 카타르", "leaning":"중동시각","color":"#27ae60",
                             "rss":["https://www.aljazeera.com/xml/rss/all.xml"]},
    "Reuters (국제)":       {"region":"🌐 국제",    "leaning":"중립",    "color":"#e74c3c",
                             "rss":["https://feeds.reuters.com/reuters/worldNews",
                                    "https://feeds.reuters.com/Reuters/worldNews"]},
    "The Guardian (영국)":  {"region":"🇬🇧 영국",   "leaning":"진보",    "color":"#1e8bc3",
                             "rss":["https://www.theguardian.com/world/rss"]},
    "DW (독일)":            {"region":"🇩🇪 독일",   "leaning":"중립",    "color":"#2980b9",
                             "rss":["https://rss.dw.com/rdf/rss-en-world",
                                    "https://rss.dw.com/rdf/rss-en-all"]},
    "France 24 (프랑스)":   {"region":"🇫🇷 프랑스", "leaning":"중립",    "color":"#2c3e7a",
                             "rss":["https://www.france24.com/en/rss",
                                    "https://www.france24.com/en/world/rss"]},
    "NHK World (일본)":     {"region":"🇯🇵 일본",   "leaning":"중립",    "color":"#8e44ad",
                             "rss":["https://www3.nhk.or.jp/nhkworld/en/news/feeds/"]},
    "AP News (미국)":       {"region":"🇺🇸 미국",   "leaning":"중립",    "color":"#d35400",
                             "rss":["https://apnews.com/index.rss"]},
}

CONFLICT_TOPICS = {
    "🇷🇺 러시아-우크라이나 전쟁": ["russia","ukraine","war","nato","kyiv","zelensky","putin","invasion","troops","missile"],
    "🇵🇸 가자지구 분쟁":          ["gaza","israel","hamas","palestine","ceasefire","hostage","rafah","idf","west bank"],
    "🇹🇼 대만해협 긴장":          ["taiwan","china","strait","pla","taipei","beijing","military drill"],
    "🌊 남중국해 영유권":          ["south china sea","philippines","spratly","paracel","china coast guard","maritime"],
    "🇰🇵 북한 핵·미사일":          ["north korea","dprk","missile","nuclear","kim jong","pyongyang","icbm"],
    "🇮🇷 이란 핵 협상":           ["iran","nuclear deal","iaea","sanctions","tehran","enrichment"],
    "🇦🇫 아프가니스탄 탈레반":      ["afghanistan","taliban","kabul","afghan"],
    "⚔️ 직접 입력":               [],
}

# ══════════════════════════════════════════════════════════════════════════════
# RSS 수집
# ══════════════════════════════════════════════════════════════════════════════
@st.cache_data(ttl=300, show_spinner=False)
def fetch_headlines(media_name: str, keywords: list) -> tuple:
    outlet  = MEDIA_OUTLETS[media_name]
    entries = []
    for url in outlet["rss"]:
        try:
            feed = feedparser.parse(url)
            if feed.entries:
                entries = feed.entries[:60]
                break
        except Exception:
            continue

    if not entries:
        return [], "fetch_failed"

    kw = [k.lower() for k in keywords]
    matched = []
    for e in entries:
        title   = e.get("title", "")
        summary = e.get("summary", "")
        text    = (title + " " + summary).lower()
        if kw and not any(k in text for k in kw):
            continue
        pub = ""
        try:    pub = e.published[:16]
        except: pass
        matched.append({"title": title, "summary": summary[:200], "url": e.get("link",""), "date": pub})
        if len(matched) >= 15:
            break

    if matched:
        return matched, "ok"

    # 키워드 매칭 없으면 최신 10건 반환
    fallback = []
    for e in entries[:10]:
        pub = ""
        try:    pub = e.published[:16]
        except: pass
        fallback.append({"title": e.get("title",""), "summary": e.get("summary","")[:200],
                         "url": e.get("link",""), "date": pub})
    return fallback, "no_match"

# ══════════════════════════════════════════════════════════════════════════════
# 로컬 분석 (API 없음)
# ══════════════════════════════════════════════════════════════════════════════
NEGATIVE_WORDS = ["kill","death","dead","attack","war","bomb","strike","explosion","crisis",
                  "threat","fear","danger","conflict","violence","casualt","civilian","destruct",
                  "massacre","siege","occupation","terror","flee","refugee","wound",
                  "collapse","fail","disaster","catastroph","brutal","horror","devastat"]
POSITIVE_WORDS = ["peace","ceasefire","deal","agreement","negotiat","diplomat","aid","relief",
                  "recover","rebuild","hope","progress","solut","cooperat","support","help"]
URGENCY_WORDS  = ["breaking","urgent","immediate","just in","alert","critical","emergency",
                  "now","today","latest","developing","overnight","hours","escalat","imminent"]

STOPWORDS = {"the","and","for","that","this","with","from","was","are","have","has","its",
             "but","not","will","been","they","their","said","says","over","after","into",
             "amid","more","than","also","about","some","out","who","what","can","all",
             "new","his","her","our","one","two","its","after","before","between"}

def score_headlines(headlines: list, keywords: list) -> dict:
    if not headlines:
        return {"objectivity":50,"negativity":50,"urgency":50,"keyword_density":0,
                "top_words":[],"tone":"불명확","total":0,"matched":0}

    titles    = [h["title"].lower() for h in headlines]
    full_text = " ".join(titles)
    words     = re.findall(r'\b[a-z]{3,}\b', full_text)
    total     = len(headlines)

    neg_count = sum(1 for w in words if any(nw in w for nw in NEGATIVE_WORDS))
    pos_count = sum(1 for w in words if any(pw in w for pw in POSITIVE_WORDS))
    urg_count = sum(1 for t in titles if any(uw in t for uw in URGENCY_WORDS))
    kw_count  = sum(1 for t in titles if keywords and any(k.lower() in t for k in keywords))

    negativity  = min(100, int((neg_count / max(len(words),1)) * 600))
    urgency     = min(100, int((urg_count / max(total,1)) * 120))
    objectivity = max(0, min(100, 80 - negativity // 3 - urgency // 5
                             + (20 if pos_count > neg_count else 0)))

    meaningful = [w for w in words if w not in STOPWORDS and len(w) > 3]
    top_words  = [w for w,_ in Counter(meaningful).most_common(10)]

    if negativity > 60 and urgency > 40:  tone = "경고·위기"
    elif negativity > 50:                 tone = "비판적"
    elif urgency > 40:                    tone = "긴박"
    elif pos_count > neg_count:           tone = "비교적 중립"
    else:                                 tone = "중립·사실 중심"

    return {"objectivity": objectivity, "negativity": negativity, "urgency": urgency,
            "keyword_density": min(100, int(kw_count / max(total,1) * 100)),
            "top_words": top_words, "tone": tone, "total": total, "matched": kw_count}


def extract_framing(headlines: list, keywords: list) -> dict:
    if not headlines:
        return {"actor_words":[], "action_words":[], "victim_words":[], "rep_headline":"—"}

    titles    = [h["title"] for h in headlines]
    full_lower = " ".join(titles).lower()

    actors  = re.findall(r'\b(?:forces?|troops?|military|army|government|minister|president|official|leader|commander|unit|regime|group|rebel|fighter|soldier)\b', full_lower)
    actions = re.findall(r'\b(?:attack(?:ed|s)?|launch(?:ed|es)?|strik(?:e|es|ing)|kill(?:ed|s)?|bomb(?:ed|s)?|fire[sd]?|invad(?:e|es|ed)?|captur(?:e|es|ed)?|seize[sd]?|halt(?:ed|s)?|push(?:ed|es)?|warn(?:ed|s)?|threaten(?:ed|s)?|negotiat(?:e|es|ed)?|accus(?:e|es|ed)?|withdraw|advance|respond(?:ed|s)?)\b', full_lower)
    victims = re.findall(r'\b(?:civilian|children|hospital|school|refuge(?:e|es)?|victim|resident|people|famil(?:y|ies))\b', full_lower)

    kw = [k.lower() for k in keywords]
    scored = sorted(titles, key=lambda t: sum(1 for k in kw if k in t.lower()), reverse=True)

    return {
        "actor_words":  [w for w,_ in Counter(actors).most_common(4)],
        "action_words": [w for w,_ in Counter(actions).most_common(5)],
        "victim_words": [w for w,_ in Counter(victims).most_common(3)],
        "rep_headline": scored[0] if scored else titles[0],
    }


def compare_two(sa, sb, fa, fb, media_a, media_b, keywords) -> dict:
    diffs = []

    dn = sa["negativity"] - sb["negativity"]
    if abs(dn) >= 10:
        more, less = (media_a, media_b) if dn > 0 else (media_b, media_a)
        diffs.append(f"**부정적 표현**: {more}이(가) {less}보다 {abs(dn)}pt 더 높은 부정성 지수를 보입니다.")

    du = sa["urgency"] - sb["urgency"]
    if abs(du) >= 10:
        more, less = (media_a, media_b) if du > 0 else (media_b, media_a)
        diffs.append(f"**긴급성·속보 어조**: {more}이(가) {less}보다 {abs(du)}pt 더 긴박한 표현을 자주 사용합니다.")

    do_ = sa["objectivity"] - sb["objectivity"]
    if abs(do_) >= 8:
        more, less = (media_a, media_b) if do_ > 0 else (media_b, media_a)
        diffs.append(f"**객관성 지수**: {more}이(가) {less}보다 {abs(do_)}pt 더 균형 잡힌 어조를 보입니다.")

    dk = sa["keyword_density"] - sb["keyword_density"]
    if abs(dk) >= 10:
        more, less = (media_a, media_b) if dk > 0 else (media_b, media_a)
        diffs.append(f"**주제 집중도**: {more}이(가) 해당 분쟁 키워드를 {abs(dk)}pt 더 집중적으로 다루고 있습니다.")

    only_a = set(fa.get("action_words",[])) - set(fb.get("action_words",[]))
    only_b = set(fb.get("action_words",[])) - set(fa.get("action_words",[]))
    if only_a or only_b:
        parts = []
        if only_a: parts.append(f"{media_a}에만 등장: {', '.join(only_a)}")
        if only_b: parts.append(f"{media_b}에만 등장: {', '.join(only_b)}")
        diffs.append(f"**사용 동사 차이**: " + " / ".join(parts))

    vic_a, vic_b = len(fa.get("victim_words",[])), len(fb.get("victim_words",[]))
    if abs(vic_a - vic_b) >= 1:
        more = media_a if vic_a > vic_b else media_b
        diffs.append(f"**민간인·피해자 언급**: {more}이(가) 민간인/피해자 관련 단어를 더 많이 포함합니다.")

    if not diffs:
        diffs = ["두 미디어의 헤드라인 수치가 유사하여 통계적 차이가 크지 않습니다.",
                 "개별 헤드라인의 세부 표현에서 시각 차이가 존재할 수 있습니다."]

    common_top = set(sa.get("top_words",[])[:5]) & set(sb.get("top_words",[])[:5])
    common_ground = (f"두 미디어 모두 '{', '.join(list(common_top)[:3])}' 같은 단어를 공통으로 사용합니다."
                     if common_top else "헤드라인 핵심 어휘에서 공통 단어가 일부 확인됩니다.")

    oa, ob = MEDIA_OUTLETS[media_a], MEDIA_OUTLETS[media_b]
    tip = (f"{oa['region']} 기반 {media_a}({oa['leaning']})과 "
           f"{ob['region']} 기반 {media_b}({ob['leaning']})는 "
           "지역·정치적 배경이 다릅니다. 두 매체를 교차 확인하고 Reuters·AP 등 중립 매체도 함께 참고하세요.")

    return {"differences": diffs, "common_ground": common_ground, "reading_tip": tip}

# ══════════════════════════════════════════════════════════════════════════════
# 렌더 헬퍼
# ══════════════════════════════════════════════════════════════════════════════
def score_bar(label, val, color):
    st.markdown(f"""
    <div class="score-row">
      <div class="score-lbl"><span>{label}</span><span>{val}</span></div>
      <div class="score-track">
        <div class="score-fill" style="width:{val}%;background:{color}"></div>
      </div>
    </div>""", unsafe_allow_html=True)


def render_headlines_panel(media_name, headlines, status, color):
    if status == "ok":
        st.markdown(f'<span class="rss-ok">● RSS 수집 완료 ({len(headlines)}건)</span>', unsafe_allow_html=True)
    elif status == "no_match":
        st.markdown(f'<span class="rss-err">● 키워드 매칭 없음 — 최신 헤드라인 표시</span>', unsafe_allow_html=True)
    else:
        st.markdown(f'<span class="rss-err">● RSS 수집 실패</span>', unsafe_allow_html=True)

    if not headlines:
        st.markdown('<div class="no-hl">헤드라인을 불러오지 못했습니다.</div>', unsafe_allow_html=True)
        return
    for h in headlines[:8]:
        st.markdown(f"""
        <div class="hl-card">
          <span class="src-badge" style="background:{color}22;color:{color}">{media_name.split()[0]}</span>
          {h['title']}
          <div class="hl-date">{h['date']}</div>
        </div>""", unsafe_allow_html=True)


def render_analysis_card(media_name, scores, framing, side):
    info  = MEDIA_OUTLETS[media_name]
    color = info["color"]
    css   = "acard-red"  if side == "red"  else "acard-blue"
    tcss  = "t-red"      if side == "red"  else "t-blue"
    icon  = "🔴"          if side == "red"  else "🔵"

    top_html    = "".join(f'<span class="term-tag {tcss}">{t}</span>'   for t in scores.get("top_words",[])[:6])
    action_html = "".join(f'<span class="term-tag t-gold">{t}</span>'   for t in framing.get("action_words",[])[:5])
    victim_html = "".join(f'<span class="term-tag t-gray">{t}</span>'   for t in framing.get("victim_words",[])[:4])
    tone        = scores.get("tone","—")

    st.markdown(f"""
    <div class="acard {css}">
      <div class="card-title">{icon} {media_name}</div>
      <div class="card-sub">{info['region']} · {info['leaning']} · 수집 {scores['total']}건 / 키워드 매칭 {scores['matched']}건</div>

      <div class="slabel">감정 톤</div>
      <span class="tone-pill" style="background:{color}22;color:{color};border:1px solid {color}44">{tone}</span>

      <div class="slabel" style="margin-top:.9rem">자주 등장한 핵심 단어</div>
      {top_html or '<span style="color:#555;font-size:.8rem">추출된 단어 없음</span>'}

      <div class="slabel">주요 행동 동사</div>
      {action_html or '<span style="color:#555;font-size:.8rem">—</span>'}

      <div class="slabel">민간인·피해자 언급</div>
      {victim_html or '<span style="color:#555;font-size:.8rem">—</span>'}

      <div class="slabel">대표 헤드라인</div>
      <div class="hl-quote">「{framing.get("rep_headline","—")}」</div>
    </div>""", unsafe_allow_html=True)

    score_bar("객관성",      scores["objectivity"],     color)
    score_bar("부정성",      scores["negativity"],      color)
    score_bar("긴급성",      scores["urgency"],         color)
    score_bar("주제 집중도", scores["keyword_density"], color)

# ══════════════════════════════════════════════════════════════════════════════
# 사이드바
# ══════════════════════════════════════════════════════════════════════════════
with st.sidebar:
    st.markdown("## ⚙️ 분석 설정")
    st.markdown("---")

    st.markdown("### 📌 분쟁 주제")
    selected = st.selectbox("주제 선택", list(CONFLICT_TOPICS.keys()))

    if selected == "⚔️ 직접 입력":
        custom      = st.text_input("키워드 입력 (영어, 쉼표 구분)", placeholder="예: Sudan, civil war")
        keywords    = [w.strip() for w in custom.split(",") if w.strip()]
        topic_label = custom or "직접 입력"
    else:
        keywords    = CONFLICT_TOPICS[selected]
        topic_label = selected
        st.caption(f"키워드: {', '.join(keywords[:4])}")

    st.markdown("---")
    st.markdown("### 📺 비교 미디어")
    mlist = list(MEDIA_OUTLETS.keys())
    ca, cb = st.columns(2)
    with ca:
        st.markdown("**🔴 A**")
        media_a = st.selectbox("", mlist, index=0, key="ma", label_visibility="collapsed")
    with cb:
        st.markdown("**🔵 B**")
        media_b = st.selectbox("", mlist, index=2, key="mb", label_visibility="collapsed")

    if media_a == media_b:
        st.warning("서로 다른 미디어를 선택하세요")

    st.markdown("---")
    st.success("🔓 API 키 불필요\nRSS 수집 + 로컬 분석")
    go = st.button("🚀 분석 시작", disabled=(media_a == media_b))

# ══════════════════════════════════════════════════════════════════════════════
# 메인 화면
# ══════════════════════════════════════════════════════════════════════════════
st.markdown('<div class="main-title">⚔️ GLOBAL CONFLICT MEDIA LENS</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">RSS 실시간 헤드라인 수집 · API 키 불필요 · 로컬 자동 분석</div>', unsafe_allow_html=True)

if go:
    st.markdown(f"## 📊 {topic_label} &nbsp;·&nbsp; {media_a} vs {media_b}")
    st.markdown("---")

    with st.spinner("📡 RSS 헤드라인 수집 중..."):
        hl_a, st_a = fetch_headlines(media_a, keywords)
        hl_b, st_b = fetch_headlines(media_b, keywords)

    with st.expander("📰 수집된 헤드라인 원문 보기", expanded=False):
        pa, pb = st.columns(2)
        with pa:
            st.markdown(f"**{media_a}**")
            render_headlines_panel(media_a, hl_a, st_a, MEDIA_OUTLETS[media_a]["color"])
        with pb:
            st.markdown(f"**{media_b}**")
            render_headlines_panel(media_b, hl_b, st_b, MEDIA_OUTLETS[media_b]["color"])

    with st.spinner("🔍 헤드라인 분석 중..."):
        scores_a  = score_headlines(hl_a, keywords)
        scores_b  = score_headlines(hl_b, keywords)
        framing_a = extract_framing(hl_a, keywords)
        framing_b = extract_framing(hl_b, keywords)
        compare   = compare_two(scores_a, scores_b, framing_a, framing_b, media_a, media_b, keywords)

    col1, col2 = st.columns(2)
    with col1:
        render_analysis_card(media_a, scores_a, framing_a, "red")
    with col2:
        render_analysis_card(media_b, scores_b, framing_b, "blue")

    diffs_html = "".join(f'<div class="diff-item">▸ {d}</div>' for d in compare["differences"])
    st.markdown(f"""
    <div class="acard acard-gold">
      <div style="font-family:'Bebas Neue',sans-serif;font-size:1.4rem;letter-spacing:2px;color:#d4ac0d;margin-bottom:1rem">
        ⚖ COMPARATIVE ANALYSIS
      </div>
      <div class="slabel">세부 차이점</div>
      {diffs_html}
      <div class="info-grid">
        <div class="info-box">
          <div class="slabel">공통 어휘</div>
          <div style="font-size:.82rem;color:#999;line-height:1.6">{compare['common_ground']}</div>
        </div>
        <div class="info-box">
          <div class="slabel">수집 현황</div>
          <div style="font-size:.82rem;color:#999;line-height:1.6">
            {media_a}: {scores_a['total']}건 수집 / {scores_a['matched']}건 키워드 매칭<br>
            {media_b}: {scores_b['total']}건 수집 / {scores_b['matched']}건 키워드 매칭
          </div>
        </div>
      </div>
      <div class="tip-box">📚 <strong>미디어 리터러시 조언</strong><br>{compare['reading_tip']}</div>
    </div>
    """, unsafe_allow_html=True)

    import plotly.graph_objects as go_plt
    cats   = ["객관성","부정성","긴급성","주제 집중도"]
    keys_s = ["objectivity","negativity","urgency","keyword_density"]
    fig = go_plt.Figure()
    fig.add_trace(go_plt.Bar(name=media_a, x=cats, y=[scores_a[k] for k in keys_s],
                             marker_color=MEDIA_OUTLETS[media_a]["color"], opacity=.85))
    fig.add_trace(go_plt.Bar(name=media_b, x=cats, y=[scores_b[k] for k in keys_s],
                             marker_color=MEDIA_OUTLETS[media_b]["color"], opacity=.85))
    fig.update_layout(
        barmode="group", height=280,
        plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#aaa", family="Noto Sans KR"),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1, font=dict(color="#aaa")),
        yaxis=dict(range=[0,100], gridcolor="rgba(255,255,255,0.05)", color="#555"),
        xaxis=dict(color="#555"),
        margin=dict(t=10,b=10,l=10,r=10),
    )
    st.markdown("<div style='height:.8rem'></div>", unsafe_allow_html=True)
    st.markdown("### 📈 보도 성향 점수 비교")
    st.plotly_chart(fig, use_container_width=True)
    st.caption(f"🕐 분석 시각: {datetime.now().strftime('%Y-%m-%d %H:%M')} | RSS 캐시: 5분")

else:
    st.markdown("""
    <div style="text-align:center;padding:4rem 2rem;color:#444">
      <div style="font-size:3.5rem;margin-bottom:1rem">📡</div>
      <p style="font-size:.95rem;color:#555;line-height:2.2">
        ① 왼쪽에서 <b style="color:#888">분쟁 주제</b> 선택<br>
        ② <b style="color:#888">미디어 2개</b> 선택<br>
        ③ <b style="color:#888">분석 시작</b> 클릭
      </p>
      <p style="font-size:.78rem;color:#333;margin-top:1.5rem">
        🔓 API 키 불필요 · RSS 무료 수집 · 로컬 자동 분석
      </p>
    </div>
    """, unsafe_allow_html=True)
