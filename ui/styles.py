MAIN_CSS = """
<style>
:root { --tg-blue:#1E88E5; --tg-cyan:#00D4FF; --tg-muted:#9DB4C8; }
.stApp {
    background:
        radial-gradient(circle at 10% 10%, rgba(30,136,229,.15), transparent 28%),
        radial-gradient(circle at 90% 5%,  rgba(0,212,255,.09),  transparent 25%),
        linear-gradient(160deg, #071426 0%, #081A30 52%, #06101F 100%);
    color: #EAF6FF;
}
.block-container { max-width:1180px; padding-top:.25rem; padding-bottom:3rem; }

/* ── Hero ── */
.tg-hero {
    width:100%; max-width:900px; margin:0 auto; padding:8px 0 18px;
    display:flex; flex-direction:column; align-items:center;
    text-align:center; background:transparent; border:0; box-shadow:none;
}
.tg-logo {
    display:block;
    width:clamp(260px,28vw,360px); max-width:80vw; height:auto;
    margin:0 auto; padding:0; border:0; border-radius:0; background:transparent;
    box-shadow:none; object-fit:contain;
    filter:drop-shadow(0 0 20px rgba(0,212,255,.30));
}
.tg-tagline {
    width:100%; margin:8px auto 0; color:#BDEFFF;
    font-size:clamp(1.05rem,2.2vw,1.35rem); font-weight:700; text-align:center;
}
.tg-method {
    width:100%; margin:5px auto 0; color:#C8EEFF;
    font-size:clamp(.88rem,1.7vw,1.02rem); font-weight:500; text-align:center;
}

/* ── Feature cards ── */
.tg-feature-grid {
    display:grid; grid-template-columns:repeat(3,minmax(0,1fr));
    width:100%; max-width:1080px; gap:12px; margin:6px auto 16px;
    align-items:stretch;
}
.tg-feature-card {
    padding:14px 16px; border-radius:14px;
    background:linear-gradient(145deg,rgba(20,48,80,.75),rgba(8,27,49,.75));
    border:1px solid rgba(0,212,255,.15); box-shadow:0 8px 22px rgba(0,0,0,.20);
}
.tg-feature-icon { font-size:1.35rem; line-height:1; }
.tg-feature-card h3 { color:#EAF6FF; margin:7px 0 4px; font-size:1rem; font-weight:700; }
.tg-feature-card p  { color:var(--tg-muted); margin:0; line-height:1.50; font-size:.88rem; }

/* ── Form container ── */
.tg-section-heading { margin:6px 0 3px; color:#fff; font-size:1.45rem; font-weight:750; }
.tg-section-note    { color:var(--tg-muted); margin-bottom:14px; font-size:.92rem; }
div[data-testid="stVerticalBlockBorderWrapper"] {
    background:rgba(12,31,55,.76); border:1px solid rgba(0,212,255,.18)!important;
    border-radius:18px!important; box-shadow:0 14px 36px rgba(0,0,0,.24);
}

/* ── Inputs ── */
div[data-testid="stTextInput"] input,
div[data-testid="stTextArea"] textarea {
    border-radius:10px!important; border:1px solid rgba(0,212,255,.28)!important;
    background:rgba(3,15,30,.80)!important; color:#fff!important;
    font-size:1rem!important;
    transition:border-color .20s ease,box-shadow .20s ease!important;
}
div[data-testid="stTextInput"] input:focus,
div[data-testid="stTextArea"] textarea:focus {
    border-color:var(--tg-cyan)!important;
    box-shadow:0 0 0 3px rgba(0,212,255,.12)!important;
}

/* ── Primary button ── */
.stButton>button {
    width:100%; border-radius:11px;
    background:linear-gradient(100deg,#1565C0,#1E88E5,#00B8D4);
    color:#fff!important; font-weight:700; padding:.80rem 1.4rem; font-size:1rem;
    border:1px solid rgba(0,212,255,.32); box-shadow:0 8px 22px rgba(30,136,229,.28);
    transition:transform .18s ease,box-shadow .18s ease,filter .18s ease;
}
.stButton>button:hover {
    transform:translateY(-2px);
    box-shadow:0 14px 30px rgba(0,212,255,.26);
    filter:brightness(1.07);
}

/* ── Secondary button (Check Another News) ── */
button[data-testid="baseButton-secondary"] {
    background: transparent !important;
    border: 1px solid rgba(0,212,255,.28) !important;
    color: rgba(234,246,255,.75) !important;
    box-shadow: none !important;
    font-weight: 600 !important;
    font-size: .96rem !important;
}
button[data-testid="baseButton-secondary"]:hover {
    background: rgba(0,212,255,.07) !important;
    border-color: rgba(0,212,255,.48) !important;
    color: #EAF6FF !important;
    box-shadow: none !important;
    transform: none !important;
    filter: none !important;
}

/* ── Result card ── */
.result-box {
    padding:24px 20px; border-radius:18px; color:#fff; text-align:center;
    margin:22px 0 14px;
    border:1px solid rgba(255,255,255,.16); box-shadow:0 16px 42px rgba(0,0,0,.30);
}
.result-icon  { font-size:2.2rem; margin-bottom:4px; }
.result-box h2 { margin:4px 0 2px; font-size:1rem; font-weight:600;
                 opacity:.75; letter-spacing:.05em; text-transform:uppercase; }
.result-box h1 { margin:2px 0 6px; font-size:clamp(1.8rem,4.5vw,2.8rem); font-weight:800; }
.result-box h3 { margin:0 auto 4px; max-width:680px;
                 font-size:.97rem; font-weight:450; line-height:1.55; opacity:.90; }

/* ── Expanders ── */
details {
    background:rgba(12,31,55,.70)!important;
    border:1px solid rgba(0,212,255,.13)!important;
    border-radius:12px!important; margin:6px 0;
}
details summary { color:#DDF7FF!important; font-weight:650!important; font-size:.97rem; }

/* ── Circular indicators ── */
.tg-indicators {
    display:flex; justify-content:center; gap:28px; margin:16px auto 10px;
    flex-wrap:wrap; align-items:flex-start;
}
.tg-indicator-item {
    display:flex; flex-direction:column; align-items:center; gap:5px; min-width:108px;
}
.tg-ind-label {
    font-size:.72rem; font-weight:700; text-transform:uppercase; letter-spacing:.07em;
    color:rgba(255,255,255,.68); text-align:center;
}
.tg-circle-wrap  { position:relative; width:100px; height:100px; }
.tg-circle-inner {
    position:absolute; top:0; left:0; right:0; bottom:0;
    display:flex; flex-direction:column; align-items:center; justify-content:center;
}
.tg-circle-pct  { font-size:1.15rem; font-weight:800; color:#fff; line-height:1; }
.tg-circle-sub  {
    font-size:.76rem; color:rgba(255,255,255,.82); text-align:center;
    max-width:120px; line-height:1.30; font-weight:600;
}
.tg-circle-cat  { font-size:.69rem; color:rgba(255,255,255,.54); text-align:center; max-width:120px; }

/* ── Decision basis note ── */
.tg-decision-basis {
    margin:12px auto 2px; max-width:680px; font-size:.91rem;
    color:rgba(255,255,255,.88); line-height:1.60; text-align:center;
    padding:10px 18px; background:rgba(0,0,0,.18); border-radius:10px;
    border:1px solid rgba(255,255,255,.11);
}
.tg-pct-note {
    margin:6px auto 0; max-width:580px; font-size:.80rem;
    color:rgba(255,255,255,.50); text-align:center; line-height:1.4;
}

/* ── Footer ── */
.tg-proof-note {
    margin:28px 0 0; padding:12px 16px; text-align:center; color:#9DB4C8;
    background:rgba(12,31,55,.50); border:1px solid rgba(0,212,255,.10); border-radius:12px;
    font-size:.90rem;
}
.footer {
    text-align:center; color:#8EA9BF; font-size:13px; line-height:1.8; margin-top:20px;
    padding-top:18px; border-top:1px solid rgba(0,212,255,.10);
}

/* ── Mobile ── */
@media (max-width:760px) {
    .block-container { padding:.1rem .75rem 2rem; }
    .tg-feature-grid { grid-template-columns:1fr; gap:10px; }
    .tg-hero { padding:4px 0 12px; }
    .tg-logo { width:clamp(200px,55vw,280px); max-width:75vw; }
    .tg-indicators { gap:18px; }
    .result-box { padding:18px 14px; }
}
@media (max-width:480px) {
    .tg-circle-wrap { width:84px; height:84px; }
    .tg-circle-pct  { font-size:.98rem; }
    .tg-ind-label   { font-size:.68rem; }
}
</style>
"""
