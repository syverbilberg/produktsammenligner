"""All CSS for the app, styled after the subscription calculator:
solid navy header, light grey page, white rounded cards with an icon
box, grey priority chips and a dark-green full-width action button."""

CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
:root {
  --navy: #0d1a56; --page: #f5f6f9; --card: #ffffff; --line: #e1e4ea; --text: #15172b;
  --muted: #5d6275; --chip: #eceef2; --field: #f7f8fa;
  --green: #00733e; --green-dark: #015e33; --green-soft: #eaf5ee;
  --amber-soft: #fff6e5; --amber: #8a5a00;
}
html, body, .stApp { background: var(--page); color: var(--text); font-family: 'Inter', sans-serif; }
.stApp { overflow-x: hidden; }
.stApp :is(p, h1, h2, h3, h4, td, th, li, a, label, button, input, div) { font-family: 'Inter', sans-serif; }
#MainMenu, footer, header[data-testid="stHeader"], [data-testid="stToolbar"] { display: none !important; }
.block-container { padding-top: 0 !important; padding-bottom: 3rem; max-width: 1400px; }

/* ---------- header ---------- */
.ps-header {
  margin: -1.2rem calc(50% - 50vw) 28px; padding: 18px max(24px, calc(50vw - 690px));
  background: var(--navy);
  display: flex; align-items: center; gap: 22px; color: #fff;
}
.ps-burger { width: 26px; display: grid; gap: 5px; }
.ps-burger span { height: 2.5px; background: #fff; border-radius: 2px; display: block; }
.ps-mark { width: 40px; height: 40px; border-radius: 10px; background: rgba(255,255,255,.1);
           display: grid; place-items: center; }
.ps-title { font-size: 1.45rem; font-weight: 700; line-height: 1.2; }
.ps-subtitle { font-size: .98rem; opacity: .72; margin-top: 2px; }

/* ---------- cards ---------- */
div[class*="st-key-card"] {
  background: var(--card); border: 1px solid var(--line) !important; border-radius: 18px !important;
  box-shadow: 0 1px 2px rgba(16,24,40,.05), 0 4px 14px rgba(16,24,40,.04);
  padding: 22px 24px !important;
}
.ps-card-head { display: flex; align-items: center; gap: 14px; margin-bottom: 6px; }
.ps-icon { width: 42px; height: 42px; border-radius: 11px; background: #eef0f4; color: #2a2e45;
           display: grid; place-items: center; flex: none; }
.ps-card-title { font-size: 1.4rem; font-weight: 700; color: var(--text); margin: 0; }

/* ---------- inputs ---------- */
.stTextInput label p { font-weight: 700 !important; font-size: 1.02rem !important; color: var(--text); }
.stTextInput input {
  background: var(--field) !important; border-radius: 10px !important; height: 54px;
  font-size: 1.08rem !important; color: var(--text);
}
.stTextInput div[data-baseweb="input"] { border-radius: 10px !important; border-color: #dadde4 !important; }

/* ---------- buttons ---------- */
.stButton button[kind="primary"], [data-testid="stBaseButton-primary"] {
  background: var(--green) !important;
  border: none !important; color: #fff !important; border-radius: 12px !important;
  min-height: 60px; font-size: 1.2rem !important; font-weight: 800 !important; letter-spacing: .2px;
  box-shadow: 0 6px 16px rgba(0,115,62,.22);
}
.stButton button[kind="primary"] p { font-size: 1.2rem !important; font-weight: 800 !important; }
.stButton button[kind="primary"]:hover { background: var(--green-dark) !important; }
.stButton button[kind="secondary"], [data-testid="stBaseButton-secondary"] {
  background: #fff !important; border: 1px solid #d9dce3 !important; border-radius: 10px !important;
  color: var(--text) !important; font-weight: 700 !important;
}

/* ---------- chips & priority controls ---------- */
.ps-chips { display: flex; flex-wrap: wrap; gap: 8px; margin: 6px 0 4px 56px; }
.ps-chip { background: var(--chip); border-radius: 999px; padding: 6px 14px; font-size: .92rem; color: #2a2e45; }
.ps-chip b { font-weight: 700; }
.ps-chip.off { opacity: .55; }
.ps-dim-label { font-weight: 700; margin: 12px 0 4px; }
[data-testid="stButtonGroup"] button { border-radius: 999px !important; }

/* ---------- fetched product tile ---------- */
.ps-tile { display: flex; gap: 12px; align-items: center; background: var(--field); border: 1px solid var(--line);
           border-radius: 12px; padding: 10px 12px; margin: -4px 0 12px; }
.ps-tile img { width: 48px; height: 48px; object-fit: contain; background: #fff; border-radius: 8px; }
.ps-tile .name { font-weight: 700; font-size: .95rem; }
.ps-tile .meta { color: var(--muted); font-size: .85rem; }

/* ---------- results ---------- */
.ps-empty { text-align: center; color: var(--muted); padding: 60px 20px; }
.ps-empty .big { font-size: 1.15rem; font-weight: 700; color: var(--text); margin-bottom: 6px; }
.ps-steps { display: flex; justify-content: center; gap: 26px; margin-top: 18px; font-size: .92rem; }
.ps-steps span b { display: inline-grid; place-items: center; width: 24px; height: 24px; border-radius: 50%;
                   background: #e2e5eb; margin-right: 6px; font-size: .8rem; }
.ps-verdict { background: var(--green-soft); border-left: 4px solid var(--green); border-radius: 10px;
              padding: 14px 16px; margin: 8px 0 4px; line-height: 1.55; }
.ps-warning { background: var(--amber-soft); color: var(--amber); border-radius: 10px; padding: 10px 14px;
              margin: 8px 0; font-size: .93rem; }
.ps-products { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 14px; margin-top: 14px; }
div.st-key-add_product .stButton button { border: 1.5px dashed #c9cdd6 !important; background: #fafbfc !important; min-height: 48px; }
div[class*="st-key-remove_"] .stButton button { border: none !important; background: transparent !important; color: #8a8fa0 !important; padding: 0 !important; min-height: 54px; font-size: 1.1rem; }
.ps-product { border: 1px solid var(--line); border-radius: 14px; padding: 16px; position: relative; background: #fff; }
.ps-product.best { border: 2px solid var(--green); }
.ps-badge { display: inline-grid; place-items: center; width: 28px; height: 28px; border-radius: 8px;
            background: var(--navy); color: #fff; font-weight: 800; }
.ps-best { position: absolute; top: 14px; right: 14px; background: var(--green); color: #fff; font-size: .78rem;
           font-weight: 700; padding: 4px 10px; border-radius: 999px; }
.ps-product img { width: 100%; height: 130px; object-fit: contain; margin: 10px 0; }
.ps-product .name { font-weight: 700; line-height: 1.3; }
.ps-product .name a { color: var(--text); text-decoration: none; }
.ps-product .price { font-size: 1.5rem; font-weight: 800; margin: 6px 0 2px; }
.ps-product .meta { color: var(--muted); font-size: .86rem; }
.ps-product .summary { font-size: .93rem; line-height: 1.5; margin-top: 10px; }
.ps-table-wrap { overflow-x: auto; margin-top: 8px; }
.ps-table { width: 100%; border-collapse: collapse; font-size: .93rem; border: none !important; display: table !important; }
.ps-table th, .ps-table td { border-left: none !important; border-right: none !important; border-top: none !important; background: transparent !important; }
.ps-table th { text-align: left; color: var(--muted); font-weight: 600; font-size: .82rem; text-transform: uppercase;
               letter-spacing: .4px; padding: 10px 10px; border-bottom: 1px solid var(--line); }
.ps-table td { padding: 11px 10px; border-bottom: 1px solid #f0f1f4; vertical-align: top; }
.ps-table td.spec { font-weight: 700; }
.ps-table td.win { color: var(--green); font-weight: 700; }
.ps-table td.missing { color: #9aa0ae; font-style: italic; }
.ps-source { display: block; font-size: .74rem; font-weight: 500; color: #9aa0ae; font-style: italic; }
.ps-table td.why { color: var(--muted); font-size: .87rem; }
.ps-pill { display: inline-block; min-width: 28px; text-align: center; padding: 2px 9px; border-radius: 999px;
           font-weight: 800; font-size: .82rem; background: var(--green-soft); color: var(--green); }
.ps-pill.none { background: var(--chip); color: var(--muted); font-weight: 600; }


/* ---------- tabs (works with both old and new Streamlit tab markup) ---------- */
[data-testid="stTabs"] [role="tablist"] { gap: 6px; background: #e2e5eb; padding: 5px; border-radius: 12px;
  width: fit-content; margin-bottom: 18px; border: none !important; }
[data-testid="stTabs"] [role="tab"] { height: 42px; padding: 0 22px; border-radius: 9px; background: transparent;
  display: flex; align-items: center; cursor: pointer; border: none !important; }
[data-testid="stTabs"] [role="tab"] p { font-size: 1rem; font-weight: 700; color: var(--muted); }
[data-testid="stTabs"] [role="tab"][aria-selected="true"] { background: #fff !important; box-shadow: 0 1px 3px rgba(16,24,40,.12); }
[data-testid="stTabs"] [role="tab"][aria-selected="true"] p { color: var(--text); }
[data-testid="stTabs"] .react-aria-SelectionIndicator,
[data-testid="stTabs"] [data-baseweb="tab-highlight"], [data-testid="stTabs"] [data-baseweb="tab-border"] { display: none !important; }

/* ---------- features tab ---------- */
.ps-minis { display: grid; grid-template-columns: repeat(auto-fit, minmax(240px, 1fr)); gap: 14px; margin-bottom: 18px; }
.ps-mini { display: flex; gap: 14px; align-items: center; background: #fff; border: 1px solid var(--line);
  border-radius: 16px; padding: 14px 16px; box-shadow: 0 1px 2px rgba(16,24,40,.05); }
.ps-mini img, .ps-noimg { width: 64px; height: 64px; object-fit: contain; border-radius: 10px; background: var(--field); flex: none; }
.ps-mini .name { font-weight: 700; color: var(--text); text-decoration: none; margin-left: 6px; }
.ps-mini .price { font-size: 1.2rem; font-weight: 800; margin-top: 2px; }
.ps-rating { color: #b7791f; font-size: .86rem; font-weight: 600; }
.ps-badge.sm { width: 22px; height: 22px; border-radius: 6px; font-size: .78rem; display: inline-grid; vertical-align: 1px; }
.ps-yes { display: inline-grid; place-items: center; width: 24px; height: 24px; border-radius: 50%;
  background: var(--green-soft); color: var(--green); font-weight: 800; }
.ps-no { display: inline-grid; place-items: center; width: 24px; height: 24px; border-radius: 50%;
  background: #fdecec; color: #b42318; font-weight: 800; font-size: .8rem; }
.ps-detail { display: block; font-size: .76rem; color: var(--amber); margin-top: 2px; }
.ps-warning.big { font-size: 1rem; line-height: 1.5; padding: 14px 16px; }
.ps-ovs { display: grid; grid-template-columns: repeat(auto-fit, minmax(260px, 1fr)); gap: 14px; }
.ps-ov { border: 1px solid var(--line); border-radius: 14px; padding: 16px; }
.ps-ov .head { display: flex; gap: 14px; align-items: center; margin-bottom: 6px; }
.ps-ov .head img, .ps-ov .ps-noimg { width: 72px; height: 72px; object-fit: contain; border-radius: 10px; background: var(--field); flex: none; }
.ps-ov .name { font-weight: 700; color: var(--text); text-decoration: none; margin-left: 6px; }
.ps-ov .meta { color: var(--muted); font-size: .85rem; margin-top: 2px; }
.ps-ov .price { font-size: 1.25rem; font-weight: 800; }
.ps-ovtable { width: 100%; border-collapse: collapse; font-size: .9rem; border: none !important; }
.ps-ovtable td { padding: 6px 4px; border: none !important; border-bottom: 1px solid #f0f1f4 !important; background: transparent !important; }
.ps-ovtable td:first-child { color: var(--muted); width: 48%; }
.ps-ovlist { margin: 0; padding-left: 0; list-style: none; font-size: .9rem; }
.ps-ovlist li { padding: 2px 0 2px 18px; position: relative; break-inside: avoid; }
.ps-ovlist li::before { content: "✓"; position: absolute; left: 0; color: var(--green); font-weight: 800; }
.ps-hint { color: var(--muted); font-size: .8rem; margin-top: 8px; }
.ps-sub { font-size: .78rem; text-transform: uppercase; letter-spacing: .4px; font-weight: 700; color: var(--muted); margin: 10px 0 4px; }
.ps-sub.good { color: var(--green); } .ps-sub.bad { color: #b42318; }
.ps-included { margin-top: 12px; padding-top: 10px; border-top: 1px solid var(--line); font-size: .92rem; line-height: 1.7; }
.ps-usecase { display: flex; gap: 14px; padding: 14px 0; border-bottom: 1px solid #f0f1f4; }
.ps-usecase:last-child { border-bottom: none; }
.ps-usecase .title { font-weight: 700; margin-bottom: 4px; display: flex; flex-wrap: wrap; gap: 8px; align-items: center; }
.ps-usecase .facts { color: #3b4054; font-size: .93rem; line-height: 1.5; }
.ps-pcs { display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 14px; }
.ps-pc { border: 1px solid var(--line); border-radius: 14px; padding: 14px 16px; }
.ps-pc .head { font-weight: 700; display: flex; gap: 8px; align-items: center; }
.ps-pc ul { margin: 0 0 4px; padding-left: 0; list-style: none; font-size: .92rem; line-height: 1.45; }
.ps-pc li { padding: 3px 0 3px 22px; position: relative; }
.ps-pc ul.good li::before { content: "✓"; position: absolute; left: 2px; color: var(--green); font-weight: 800; }
.ps-pc ul.bad li::before { content: "–"; position: absolute; left: 4px; color: #b42318; font-weight: 800; }
.ps-pc li.none { color: var(--muted); }
.ps-choose { background: var(--green-soft); border-left: 4px solid var(--green); border-radius: 10px;
  padding: 12px 14px; margin: 8px 0; line-height: 1.5; }

@media (max-width: 760px) {
  .ps-products { grid-template-columns: 1fr; }
  .ps-chips { margin-left: 0; }
}
</style>
"""
