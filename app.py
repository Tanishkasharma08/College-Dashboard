#!/usr/bin/env python3
"""
ACET College Dashboard - With SQLite Message Storage + Secure Admin Login
"""

import sqlite3
import os
from datetime import datetime
from functools import wraps
from flask import (Flask, render_template_string, request, jsonify,
                   redirect, url_for, session, flash)

app = Flask(__name__)
app.secret_key = 'acet@2026#secretKey!xYz'   # Change in production

DB_PATH = "acet_messages.db"

# ── Admin Credentials (hardcoded for dev — use DB/env in production) ──
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "admin123"

# ── Login Required Decorator ────────────────────────────
def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not session.get('admin_logged_in'):
            return redirect(url_for('admin_login'))
        return f(*args, **kwargs)
    return decorated

# ── Database Setup ──────────────────────────────────────
def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS messages (
            id        INTEGER PRIMARY KEY AUTOINCREMENT,
            name      TEXT    NOT NULL,
            email     TEXT    NOT NULL,
            message   TEXT    NOT NULL,
            received_at TEXT  NOT NULL,
            is_read   INTEGER DEFAULT 0
        )
    ''')
    conn.commit()
    conn.close()

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

# ── HTML Template ───────────────────────────────────────
MAIN_HTML = '''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8"/>
<meta name="viewport" content="width=device-width, initial-scale=1.0"/>
<title>ACET – Aligarh College of Engineering &amp; Technology</title>
<link href="https://fonts.googleapis.com/css2?family=Cormorant+Garamond:wght@400;600;700&family=Plus+Jakarta+Sans:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet"/>
<style>
:root {
  --navy:    #0b1d3a;
  --deep:    #0f2548;
  --mid:     #1b4080;
  --sky:     #2563eb;
  --gold:    #c8961e;
  --amber:   #f0b429;
  --cream:   #fdf8f0;
  --light:   #f3f6fb;
  --white:   #ffffff;
  --text:    #1a2740;
  --muted:   #5a6f8a;
  --border:  #dde5f0;
  --shadow:  0 4px 28px rgba(11,29,58,.10);
  --radius:  14px;
}
*{box-sizing:border-box;margin:0;padding:0}
html{scroll-behavior:smooth}
body{font-family:'Plus Jakarta Sans',sans-serif;background:var(--cream);color:var(--text);min-height:100vh}
a{color:inherit;text-decoration:none}
img{display:block}
nav {
  background:var(--navy);
  position:sticky;top:0;z-index:999;
  box-shadow:0 2px 20px rgba(0,0,0,.35);
}
.nav-inner {
  max-width:1300px;margin:0 auto;
  display:flex;align-items:center;justify-content:space-between;
  padding:0 28px;height:62px;
}
.nav-brand {display:flex;align-items:center;gap:13px}
.nav-emblem {
  width:42px;height:42px;border-radius:50%;
  background:linear-gradient(135deg,var(--gold),var(--amber));
  display:flex;align-items:center;justify-content:center;
  font-family:'Cormorant Garamond',serif;font-size:19px;font-weight:700;color:var(--navy);
  flex-shrink:0;
}
.nav-name {
  font-family:'Cormorant Garamond',serif;font-size:15px;font-weight:700;
  color:#fff;line-height:1.25;
}
.nav-name small {
  display:block;font-family:'Plus Jakarta Sans',sans-serif;
  font-size:9.5px;font-weight:400;color:#8faac8;letter-spacing:.4px;
}
.nav-links {display:flex;gap:1px;flex-wrap:wrap;align-items:center}
.nav-links a {
  color:#9bb5d0;font-size:11.5px;font-weight:500;
  padding:5px 10px;border-radius:6px;transition:.18s;
}
.nav-links a:hover,.nav-links a.active {
  background:rgba(255,255,255,.10);color:#fff;
}
.nav-cta {
  background:linear-gradient(135deg,var(--gold),var(--amber));
  color:var(--navy);border:none;padding:8px 18px;
  border-radius:8px;font-size:12px;font-weight:700;
  cursor:pointer;font-family:'Plus Jakarta Sans',sans-serif;
  transition:.18s;white-space:nowrap;
}
.nav-cta:hover{opacity:.88;transform:translateY(-1px)}
.hero {
  background:linear-gradient(155deg,var(--navy) 0%,var(--deep) 55%,#0d3060 100%);
  padding:80px 28px 64px;position:relative;overflow:hidden;
}
.hero::before {
  content:'';position:absolute;inset:0;
  background:
    radial-gradient(ellipse at 15% 60%,rgba(200,150,30,.09) 0%,transparent 55%),
    radial-gradient(ellipse at 85% 15%,rgba(37,99,235,.07) 0%,transparent 50%);
}
.hero::after {
  content:'';position:absolute;
  bottom:-1px;left:0;right:0;height:56px;
  background:var(--cream);
  clip-path:ellipse(55% 100% at 50% 100%);
}
.hero-inner {max-width:1300px;margin:0 auto;position:relative}
.hero-pill {
  display:inline-flex;align-items:center;gap:8px;
  background:rgba(200,150,30,.14);border:1px solid rgba(200,150,30,.3);
  padding:5px 14px;border-radius:20px;margin-bottom:22px;
}
.hero-pill span {font-size:11.5px;color:var(--amber);font-weight:600;letter-spacing:.5px}
.hero h1 {
  font-family:'Cormorant Garamond',serif;
  font-size:clamp(28px,4.5vw,56px);font-weight:700;
  color:#fff;line-height:1.12;margin-bottom:14px;
}
.hero h1 em {color:var(--amber);font-style:normal}
.hero-sub {font-size:13.5px;color:#8faac8;margin-bottom:10px}
.hero-tags {display:flex;flex-wrap:wrap;gap:10px;margin-top:22px}
.hero-tag {
  background:rgba(255,255,255,.07);
  border:1px solid rgba(255,255,255,.12);
  padding:7px 15px;border-radius:8px;
  font-size:12px;color:#cde;font-weight:500;
}
.hero-stats {
  display:flex;flex-wrap:wrap;gap:16px;margin-top:36px;
}
.stat-box {
  background:rgba(255,255,255,.07);
  border:1px solid rgba(255,255,255,.10);
  border-radius:12px;padding:16px 22px;text-align:center;min-width:110px;
}
.stat-box .num {
  font-family:'Cormorant Garamond',serif;
  font-size:30px;font-weight:700;color:var(--amber);display:block;
}
.stat-box .lbl {font-size:10.5px;color:#8faac8;margin-top:2px}
.sec {padding:60px 28px;max-width:1300px;margin:0 auto}
.sec-alt {background:#edf2f9;padding:60px 28px}
.sec-alt-inner{max-width:1300px;margin:0 auto}
.sec-hd {margin-bottom:36px}
.sec-hd h2 {
  font-family:'Cormorant Garamond',serif;
  font-size:32px;font-weight:700;color:var(--navy);
}
.sec-hd .bar {
  width:48px;height:4px;background:linear-gradient(90deg,var(--gold),var(--amber));
  border-radius:2px;margin:10px 0 8px;
}
.sec-hd p {font-size:13.5px;color:var(--muted)}
.card {
  background:var(--white);border-radius:var(--radius);
  padding:36px;box-shadow:var(--shadow);border:1px solid var(--border);
}
.overview-grid {
  display:grid;
  grid-template-columns:repeat(auto-fill,minmax(240px,1fr));
  gap:18px;
}
.ov-card {
  background:var(--light);border:1px solid var(--border);
  border-radius:12px;padding:22px;
  border-left:4px solid var(--gold);
  transition:.2s;
}
.ov-card:hover{transform:translateY(-3px);box-shadow:0 8px 24px rgba(11,29,58,.09)}
.ov-icon {font-size:26px;margin-bottom:10px}
.ov-card h4 {font-size:14px;font-weight:700;color:var(--navy);margin-bottom:5px}
.ov-card p {font-size:12.5px;color:var(--muted);line-height:1.6}
.dept-grid {
  display:grid;
  grid-template-columns:repeat(auto-fill,minmax(200px,1fr));
  gap:18px;
}
.dept-card {
  background:linear-gradient(145deg,var(--navy) 0%,var(--mid) 100%);
  border-radius:14px;padding:28px 22px;color:#fff;
  cursor:default;transition:.22s;
  border:1px solid rgba(255,255,255,.06);
  position:relative;overflow:hidden;
}
.dept-card::after {
  content:'';position:absolute;
  bottom:-20px;right:-20px;
  width:75px;height:75px;border-radius:50%;
  background:rgba(255,255,255,.04);
}
.dept-card:hover{transform:translateY(-5px);box-shadow:0 16px 40px rgba(11,29,58,.28)}
.dept-icon {font-size:32px;margin-bottom:14px}
.dept-name {
  font-family:'Cormorant Garamond',serif;
  font-size:22px;font-weight:700;
}
.dept-full {font-size:11px;color:#90aecb;margin-top:3px}
.dept-badge {
  display:inline-block;margin-top:10px;
  background:rgba(200,150,30,.18);border:1px solid rgba(200,150,30,.35);
  color:var(--amber);font-size:10px;font-weight:700;
  padding:3px 11px;border-radius:20px;
}
.admit-grid {
  display:grid;
  grid-template-columns:repeat(auto-fill,minmax(260px,1fr));
  gap:18px;margin-bottom:32px;
}
.admit-card {
  background:var(--light);border:1px solid var(--border);
  border-radius:12px;padding:22px;
  border-top:4px solid var(--sky);
}
.admit-card h4 {font-size:16px;font-weight:700;color:var(--navy);margin-bottom:4px}
.admit-dur {font-size:11px;color:var(--sky);font-weight:600;margin-bottom:12px}
.admit-card ul {list-style:none;font-size:12.5px;color:var(--text)}
.admit-card ul li {padding:3px 0 3px 18px;position:relative;}
.admit-card ul li::before {content:'✓';position:absolute;left:0;color:#22c55e;font-weight:700;}
.admit-min {
  display:inline-block;margin-top:12px;
  background:rgba(11,29,58,.07);border-radius:6px;
  padding:4px 11px;font-size:11px;font-weight:700;color:var(--navy);
}
.docs-grid {
  display:grid;
  grid-template-columns:repeat(auto-fill,minmax(185px,1fr));
  gap:9px;margin-top:18px;
}
.doc-item {
  display:flex;align-items:center;gap:8px;
  background:var(--light);border:1px solid var(--border);
  border-radius:8px;padding:9px 13px;font-size:12.5px;color:var(--text);
}
.tbl-wrap {overflow-x:auto}
table {width:100%;border-collapse:collapse;font-size:13.5px}
thead th {
  background:var(--navy);color:#fff;
  padding:13px 18px;text-align:left;
  font-size:12px;font-weight:600;letter-spacing:.3px;
}
thead th:first-child{border-radius:10px 0 0 0}
thead th:last-child{border-radius:0 10px 0 0}
tbody td {padding:12px 18px;border-bottom:1px solid var(--border)}
tbody tr:last-child td {border-bottom:none}
tbody tr:nth-child(even) td {background:#f8fafd}
tbody tr:hover td {background:#f0f5ff}
.td-name {font-weight:700;color:var(--navy)}
.td-na {color:#bbb;font-size:12px}
.td-total {font-weight:700;color:var(--mid)}
.fees-note {font-size:11.5px;color:var(--muted);margin-top:14px}
.cal-grid {
  display:grid;
  grid-template-columns:repeat(auto-fill,minmax(265px,1fr));
  gap:16px;
}
.cal-month {
  background:var(--white);border:1px solid var(--border);
  border-radius:12px;overflow:hidden;
}
.cal-hd {
  background:var(--navy);color:#fff;
  padding:12px 18px;font-weight:700;font-size:13px;
  display:flex;align-items:center;gap:7px;
}
.cal-body {padding:12px 16px}
.cal-row {
  display:flex;gap:10px;align-items:flex-start;
  padding:6px 0;border-bottom:1px solid #eef2f8;font-size:12.5px;
}
.cal-row:last-child {border-bottom:none}
.cal-tag {
  font-size:9.5px;font-weight:700;padding:3px 8px;border-radius:5px;
  white-space:nowrap;flex-shrink:0;font-family:'JetBrains Mono',monospace;
}
.t-hol  {background:#fee2e2;color:#b91c1c}
.t-exam {background:#dbeafe;color:#1d4ed8}
.t-reg  {background:#dcfce7;color:#15803d}
.t-vac  {background:#fef9c3;color:#854d0e}
.tabs {
  display:flex;gap:5px;flex-wrap:wrap;
  background:var(--light);border:1px solid var(--border);
  padding:5px;border-radius:10px;margin-bottom:24px;
}
.tab-btn {
  padding:9px 20px;border:none;background:none;
  border-radius:7px;font-size:13px;font-weight:500;
  cursor:pointer;color:var(--muted);
  font-family:'Plus Jakarta Sans',sans-serif;transition:.18s;
}
.tab-btn.active,.tab-btn:hover {
  background:var(--white);color:var(--navy);font-weight:700;
  box-shadow:0 2px 10px rgba(0,0,0,.08);
}
.tab-panel {display:none}
.tab-panel.active {display:block}
.circ-grid {
  display:grid;
  grid-template-columns:repeat(auto-fill,minmax(280px,1fr));
  gap:16px;
}
.circ-card {
  background:var(--white);border:1px solid var(--border);
  border-radius:12px;padding:20px;position:relative;
  transition:.2s;
}
.circ-card:hover{transform:translateY(-2px);box-shadow:0 8px 24px rgba(11,29,58,.09)}
.circ-badge {
  display:inline-block;font-size:10px;font-weight:700;
  letter-spacing:.4px;padding:3px 11px;border-radius:20px;margin-bottom:9px;
}
.b-notice {background:#dbeafe;color:#1d4ed8}
.b-event  {background:#dcfce7;color:#15803d}
.b-scholar{background:#fef3c7;color:#92400e}
.circ-card h4 {font-size:14.5px;font-weight:700;color:var(--navy);margin-bottom:5px}
.circ-card p  {font-size:12.5px;color:var(--muted);line-height:1.55}
.circ-new {
  position:absolute;top:12px;right:12px;
  background:#ef4444;color:#fff;
  font-size:9px;font-weight:700;
  padding:2px 8px;border-radius:10px;
}
.contact-grid {
  display:grid;grid-template-columns:1fr 1fr;gap:32px;
}
@media(max-width:760px){.contact-grid{grid-template-columns:1fr}}
.cinfo-row {display:flex;gap:14px;align-items:flex-start;margin-bottom:18px}
.cinfo-icon {
  width:44px;height:44px;border-radius:10px;flex-shrink:0;
  background:var(--navy);display:flex;align-items:center;
  justify-content:center;font-size:18px;
}
.cinfo-lbl {font-size:11px;color:var(--muted);font-weight:600;margin-bottom:2px}
.cinfo-val {font-size:13px;color:var(--text);font-weight:500;line-height:1.55}
.map-box {
  background:linear-gradient(135deg,var(--navy),var(--mid));
  border-radius:14px;height:230px;
  display:flex;flex-direction:column;align-items:center;
  justify-content:center;gap:10px;color:#fff;
}
.map-box .map-icon {font-size:42px}
.map-box p {font-size:12px;color:#9bb5d0;text-align:center;padding:0 20px}
footer {
  background:var(--navy);color:#8faac8;
  text-align:center;padding:24px;font-size:12.5px;margin-top:0;
}
footer strong {color:var(--amber)}
.reveal {opacity:0;transform:translateY(20px);transition:.65s ease}
.reveal.visible {opacity:1;transform:none}
@media(max-width:640px){
  .hero{padding:52px 18px 48px}
  .sec{padding:44px 18px}
  .sec-alt{padding:44px 18px}
  .card{padding:22px}
  .hero-stats{gap:10px}
  .stat-box{min-width:90px;padding:12px 14px}
}
</style>
</head>
<body>

<nav>
  <div class="nav-inner">
    <div class="nav-brand">
      <div class="nav-emblem">A</div>
      <div class="nav-name">
        ACET
        <small>Aligarh College of Engineering &amp; Technology</small>
      </div>
    </div>
    <div class="nav-links">
      <a href="#overview">Overview</a>
      <a href="#departments">Departments</a>
      <a href="#admission">Admission</a>
      <a href="#fees">Fees</a>
      <a href="#calendar">Calendar</a>
      <a href="#circulars">Circulars</a>
      <a href="#contact">Contact</a>
      <a href="/admin/login" style="color:var(--amber);border:1px solid rgba(200,150,30,.35);padding:5px 12px;border-radius:6px;font-weight:600;">🔐 Admin</a>
    </div>
    <button class="nav-cta" onclick="document.getElementById('contact').scrollIntoView({behavior:'smooth'})">
      📞 Contact Us
    </button>
  </div>
</nav>

<div class="hero">
  <div class="hero-inner reveal">
    <div class="hero-pill"><span>🏛 AICTE Approved · AKTU Affiliated · Aligarh, U.P.</span></div>
    <h1>ALIGARH COLLEGE OF<br/><em>ENGINEERING &amp; TECHNOLOGY</em></h1>
    <div class="hero-sub">3 KM from Sasni Gate, Mathura Road, Aligarh, Uttar Pradesh</div>
    <div class="hero-tags">
      <div class="hero-tag">✅ Approved by AICTE, New Delhi</div>
      <div class="hero-tag">🎓 Affiliated to AKTU, Lucknow</div>
      <div class="hero-tag">📞 +91 9568200010</div>
      <div class="hero-tag">✉️ mail@acetup.org</div>
    </div>
    <div class="hero-stats">
      <div class="stat-box"><span class="num">5</span><div class="lbl">Departments</div></div>
      <div class="stat-box"><span class="num">1000+</span><div class="lbl">Students</div></div>
      <div class="stat-box"><span class="num">100%</span><div class="lbl">Placement Focus</div></div>
      <div class="stat-box"><span class="num">2026</span><div class="lbl">Academic Year</div></div>
    </div>
  </div>
</div>

<div id="overview" class="sec reveal">
  <div class="sec-hd">
    <h2>College Overview</h2>
    <div class="bar"></div>
    <p>A premier technical institution committed to academic excellence and holistic development</p>
  </div>
  <div class="card">
    <div class="overview-grid">
      <div class="ov-card">
        <div class="ov-icon">🏫</div>
        <h4>Institution</h4>
        <p>Aligarh College of Engineering &amp; Technology (ACET), situated in Aligarh, Uttar Pradesh</p>
      </div>
      <div class="ov-card" style="border-left-color:#2563eb">
        <div class="ov-icon">✅</div>
        <h4>Approved By</h4>
        <p>All India Council for Technical Education (AICTE), New Delhi</p>
      </div>
      <div class="ov-card" style="border-left-color:#7c3aed">
        <div class="ov-icon">🎓</div>
        <h4>Affiliated To</h4>
        <p>Dr. A.P.J. Abdul Kalam Technical University (AKTU), Lucknow</p>
      </div>
      <div class="ov-card" style="border-left-color:#059669">
        <div class="ov-icon">📍</div>
        <h4>Location</h4>
        <p>3 KM from Sasni Gate, Mathura Road, Aligarh, Uttar Pradesh</p>
      </div>
      <div class="ov-card" style="border-left-color:#dc2626">
        <div class="ov-icon">📚</div>
        <h4>Programs Offered</h4>
        <p>MBA · MCA · B.Tech · BBA · BCA — Management &amp; Technology domains</p>
      </div>
      <div class="ov-card" style="border-left-color:#0891b2">
        <div class="ov-icon">🎯</div>
        <h4>Admission Policy</h4>
        <p>Merit-based percentage criteria. No entrance exam required for any program.</p>
      </div>
    </div>
  </div>
</div>

<div class="sec-alt reveal">
<div id="departments" class="sec-alt-inner">
  <div class="sec-hd">
    <h2>Departments</h2>
    <div class="bar"></div>
    <p>5 dynamic programs in Technology and Management</p>
  </div>
  <div class="dept-grid">
    <div class="dept-card">
      <div class="dept-icon">💼</div>
      <div class="dept-name">MBA</div>
      <div class="dept-full">Master of Business Administration</div>
      <div class="dept-badge">2 Years</div>
    </div>
    <div class="dept-card">
      <div class="dept-icon">💻</div>
      <div class="dept-name">MCA</div>
      <div class="dept-full">Master of Computer Applications</div>
      <div class="dept-badge">2 Years</div>
    </div>
    <div class="dept-card">
      <div class="dept-icon">⚙️</div>
      <div class="dept-name">B.Tech</div>
      <div class="dept-full">Bachelor of Technology</div>
      <div class="dept-badge">4 Years</div>
    </div>
    <div class="dept-card">
      <div class="dept-icon">📊</div>
      <div class="dept-name">BBA</div>
      <div class="dept-full">Bachelor of Business Administration</div>
      <div class="dept-badge">3 Years</div>
    </div>
    <div class="dept-card">
      <div class="dept-icon">🖥️</div>
      <div class="dept-name">BCA</div>
      <div class="dept-full">Bachelor of Computer Applications</div>
      <div class="dept-badge">3 Years</div>
    </div>
  </div>
</div>
</div>

<div id="admission" class="sec reveal">
  <div class="sec-hd">
    <h2>Admission Procedure</h2>
    <div class="bar"></div>
    <p>Percentage-based merit admission — No entrance exam required</p>
  </div>
  <div class="card">
    <div style="background:#f0fdf4;border:1px solid #86efac;border-radius:10px;padding:13px 18px;margin-bottom:26px;display:flex;gap:10px;align-items:center">
      <span style="font-size:20px">✅</span>
      <span style="font-size:13px;color:#166534;font-weight:500">
        Admission is <strong>purely percentage-based</strong>. No entrance exam required. Apply directly to the college admission office.
      </span>
    </div>
    <div class="admit-grid">
      <div class="admit-card">
        <h4>MBA</h4>
        <div class="admit-dur">⏱ 2 Years Program</div>
        <ul>
          <li>Graduation in BBA / B.Com / B.A. (Economics)</li>
          <li>B.Sc (Management-related)</li>
        </ul>
        <div class="admit-min">Minimum 50% Marks</div>
      </div>
      <div class="admit-card">
        <h4>MCA</h4>
        <div class="admit-dur">⏱ 2 Years Program</div>
        <ul>
          <li>BCA / B.Sc (CS/IT)</li>
          <li>OR Graduation with Mathematics</li>
        </ul>
        <div class="admit-min">Minimum 50% Marks</div>
      </div>
      <div class="admit-card">
        <h4>B.Tech</h4>
        <div class="admit-dur">⏱ 4 Years Program</div>
        <ul>
          <li>10+2 with Physics, Chemistry, Mathematics</li>
        </ul>
        <div class="admit-min">Minimum 55% Marks</div>
      </div>
      <div class="admit-card">
        <h4>BBA</h4>
        <div class="admit-dur">⏱ 3 Years Program</div>
        <ul>
          <li>10+2 in any stream</li>
        </ul>
        <div class="admit-min">Minimum 45% Marks</div>
      </div>
      <div class="admit-card">
        <h4>BCA</h4>
        <div class="admit-dur">⏱ 3 Years Program</div>
        <ul>
          <li>10+2 with Mathematics or Computer Science</li>
        </ul>
        <div class="admit-min">Minimum 45% Marks</div>
      </div>
    </div>
    <h3 style="font-size:17px;font-weight:700;color:var(--navy);margin-bottom:4px;margin-top:10px">
      📄 Documents Required
    </h3>
    <p style="font-size:12.5px;color:var(--muted);margin-bottom:4px">
      Carry originals + self-attested photocopies at the time of admission
    </p>
    <div class="docs-grid">
      <div class="doc-item">📋 10th Marksheet</div>
      <div class="doc-item">📋 12th Marksheet</div>
      <div class="doc-item">📋 Graduation Marksheet (if applicable)</div>
      <div class="doc-item">📜 Transfer Certificate</div>
      <div class="doc-item">📜 Migration Certificate</div>
      <div class="doc-item">🪪 Aadhaar Card</div>
      <div class="doc-item">🖼️ 4 Passport Size Photos</div>
      <div class="doc-item">📜 Character Certificate</div>
    </div>
  </div>
</div>

<div class="sec-alt reveal">
<div id="fees" class="sec-alt-inner">
  <div class="sec-hd">
    <h2>Fees Structure</h2>
    <div class="bar"></div>
    <p>Year-wise fee breakup for all programs (2026–27)</p>
  </div>
  <div class="card">
    <div class="tbl-wrap">
      <table>
        <thead>
          <tr>
            <th>Department</th><th>Year 1</th><th>Year 2</th><th>Year 3</th><th>Year 4</th><th>Total Fees</th>
          </tr>
        </thead>
        <tbody>
          <tr>
            <td class="td-name">MBA</td><td>₹ 85,000</td><td>₹ 80,000</td>
            <td class="td-na">—</td><td class="td-na">—</td><td class="td-total">₹ 1,65,000</td>
          </tr>
          <tr>
            <td class="td-name">MCA</td><td>₹ 90,000</td><td>₹ 85,000</td>
            <td class="td-na">—</td><td class="td-na">—</td><td class="td-total">₹ 1,75,000</td>
          </tr>
          <tr>
            <td class="td-name">B.Tech</td><td>₹ 1,10,000</td><td>₹ 1,05,000</td>
            <td>₹ 1,00,000</td><td>₹ 1,00,000</td><td class="td-total">₹ 4,15,000</td>
          </tr>
          <tr>
            <td class="td-name">BBA</td><td>₹ 60,000</td><td>₹ 55,000</td>
            <td>₹ 55,000</td><td class="td-na">—</td><td class="td-total">₹ 1,70,000</td>
          </tr>
          <tr>
            <td class="td-name">BCA</td><td>₹ 65,000</td><td>₹ 60,000</td>
            <td>₹ 60,000</td><td class="td-na">—</td><td class="td-total">₹ 1,85,000</td>
          </tr>
        </tbody>
      </table>
    </div>
    <p class="fees-note">
      * Fees are subject to revision. Amounts include tuition, examination, and other charges.
      Contact the admission office for the latest details.
    </p>
  </div>
</div>
</div>

<div id="calendar" class="sec reveal">
  <div class="sec-hd">
    <h2>Academic Calendar 2026</h2>
    <div class="bar"></div>
    <p>Uniform schedule for all departments — exams, holidays &amp; vacations color-coded</p>
  </div>
  <div style="display:flex;gap:14px;flex-wrap:wrap;margin-bottom:22px;font-size:12px">
    <span style="display:flex;align-items:center;gap:5px"><span class="cal-tag t-hol" style="font-size:10px">HOL</span> Holiday</span>
    <span style="display:flex;align-items:center;gap:5px"><span class="cal-tag t-exam" style="font-size:10px">EXAM</span> Examination</span>
    <span style="display:flex;align-items:center;gap:5px"><span class="cal-tag t-reg" style="font-size:10px">OPEN</span> College Opens</span>
    <span style="display:flex;align-items:center;gap:5px"><span class="cal-tag t-vac" style="font-size:10px">VAC</span> Vacation</span>
  </div>
  <div class="cal-grid">
    <div class="cal-month">
      <div class="cal-hd">📅 January 2026</div>
      <div class="cal-body">
        <div class="cal-row"><span class="cal-tag t-hol">01 Jan</span><span>New Year Holiday</span></div>
        <div class="cal-row"><span class="cal-tag t-reg">05 Jan</span><span>College Reopens</span></div>
        <div class="cal-row"><span class="cal-tag t-hol">26 Jan</span><span>Republic Day</span></div>
      </div>
    </div>
    <div class="cal-month">
      <div class="cal-hd">📅 March 2026</div>
      <div class="cal-body">
        <div class="cal-row"><span class="cal-tag t-hol">04 Mar</span><span>Holi</span></div>
        <div class="cal-row"><span class="cal-tag t-exam">10–18 Mar</span><span>📌 1st Sessional Exam</span></div>
        <div class="cal-row"><span class="cal-tag t-hol">21 Mar</span><span>Eid-ul-Fitr</span></div>
        <div class="cal-row"><span class="cal-tag t-hol">26 Mar</span><span>Ram Navami</span></div>
      </div>
    </div>
    <div class="cal-month">
      <div class="cal-hd">📅 April 2026</div>
      <div class="cal-body">
        <div class="cal-row"><span class="cal-tag t-hol">03 Apr</span><span>Good Friday</span></div>
        <div class="cal-row"><span class="cal-tag t-exam">15–22 Apr</span><span>📌 2nd Sessional Exam</span></div>
      </div>
    </div>
    <div class="cal-month">
      <div class="cal-hd">📅 May 2026</div>
      <div class="cal-body">
        <div class="cal-row"><span class="cal-tag t-exam">10–31 May</span><span>📌 University Exams</span></div>
        <div class="cal-row"><span class="cal-tag t-hol">27 May</span><span>Bakrid</span></div>
      </div>
    </div>
    <div class="cal-month">
      <div class="cal-hd">📅 June 2026</div>
      <div class="cal-body">
        <div class="cal-row"><span class="cal-tag t-vac">01–30 Jun</span><span>🌴 Summer Vacation</span></div>
      </div>
    </div>
    <div class="cal-month">
      <div class="cal-hd">📅 July 2026</div>
      <div class="cal-body">
        <div class="cal-row"><span class="cal-tag t-reg">05 Jul</span><span>College Reopens</span></div>
      </div>
    </div>
    <div class="cal-month">
      <div class="cal-hd">📅 September 2026</div>
      <div class="cal-body">
        <div class="cal-row"><span class="cal-tag t-exam">10–18 Sep</span><span>📌 3rd Sessional Exam</span></div>
      </div>
    </div>
    <div class="cal-month">
      <div class="cal-hd">📅 October 2026</div>
      <div class="cal-body">
        <div class="cal-row"><span class="cal-tag t-hol">02 Oct</span><span>Gandhi Jayanti</span></div>
        <div class="cal-row"><span class="cal-tag t-hol">20 Oct</span><span>Dussehra</span></div>
        <div class="cal-row"><span class="cal-tag t-exam">20–28 Oct</span><span>📌 4th Sessional Exam</span></div>
      </div>
    </div>
    <div class="cal-month">
      <div class="cal-hd">📅 November 2026</div>
      <div class="cal-body">
        <div class="cal-row"><span class="cal-tag t-vac">07–11 Nov</span><span>🪔 Diwali Break (5 Days)</span></div>
        <div class="cal-row"><span class="cal-tag t-hol">15 Nov</span><span>Chhath Puja</span></div>
        <div class="cal-row"><span class="cal-tag t-hol">24 Nov</span><span>Guru Nanak Jayanti</span></div>
      </div>
    </div>
    <div class="cal-month">
      <div class="cal-hd">📅 December 2026</div>
      <div class="cal-body">
        <div class="cal-row"><span class="cal-tag t-exam">01–20 Dec</span><span>📌 University Exams</span></div>
        <div class="cal-row"><span class="cal-tag t-hol">25 Dec</span><span>Christmas</span></div>
      </div>
    </div>
  </div>
</div>

<div class="sec-alt reveal">
<div id="circulars" class="sec-alt-inner">
  <div class="sec-hd">
    <h2>Circular &amp; Notices</h2>
    <div class="bar"></div>
    <p>Official notices and upcoming events from the administration</p>
  </div>
  <div class="card">
    <div class="tabs">
      <button class="tab-btn active" onclick="switchTab('tab-notices',this)">📋 Notices</button>
      <button class="tab-btn" onclick="switchTab('tab-events',this)">🎉 Events</button>
      <button class="tab-btn" onclick="switchTab('tab-scholar',this)">🏅 Scholarship</button>
    </div>
    <div class="tab-panel active" id="tab-notices">
      <div class="circ-grid">
        <div class="circ-card">
          <div class="circ-new">NEW</div>
          <span class="circ-badge b-notice">NOTICE</span>
          <h4>📄 Result Declaration</h4>
          <p>University examination results have been declared. Students may check results on the AKTU portal using their roll number.</p>
        </div>
        <div class="circ-card">
          <span class="circ-badge b-notice">NOTICE</span>
          <h4>📅 Sessional Date Sheet</h4>
          <p>Date sheet for the upcoming sessional examinations has been released. Students are advised to prepare accordingly.</p>
        </div>
        <div class="circ-card">
          <span class="circ-badge b-notice">NOTICE</span>
          <h4>🎓 University Date Sheet</h4>
          <p>The university has published the end-semester examination schedule. All students must note their individual subject dates.</p>
        </div>
        <div class="circ-card">
          <span class="circ-badge b-notice">NOTICE</span>
          <h4>🏖️ Holiday Notice</h4>
          <p>As per the academic calendar, official holiday dates have been announced. Please refer to the Academic Calendar section for details.</p>
        </div>
        <div class="circ-card">
          <div class="circ-new">OPEN</div>
          <span class="circ-badge b-notice">NOTICE</span>
          <h4>📢 Admission Notice 2026–27</h4>
          <p>Admissions are now open for MBA, MCA, B.Tech, BBA &amp; BCA programs for the session 2026–27. Apply at the admission office.</p>
        </div>
      </div>
    </div>
    <div class="tab-panel" id="tab-events">
      <div class="circ-grid">
        <div class="circ-card">
          <div class="circ-new">UPCOMING</div>
          <span class="circ-badge b-event">EVENT</span>
          <h4>🎊 Annual Function</h4>
          <p>The grand Annual Function of ACET celebrating student achievements, cultural performances, and prize distribution ceremony.</p>
        </div>
        <div class="circ-card">
          <span class="circ-badge b-event">EVENT</span>
          <h4>💡 Technical Fest</h4>
          <p>An inter-college technical festival featuring project exhibitions, coding competitions, hackathons, and expert talks from industry leaders.</p>
        </div>
        <div class="circ-card">
          <span class="circ-badge b-event">EVENT</span>
          <h4>🏆 Sports Meet</h4>
          <p>Annual inter-department sports meet with competitions in cricket, volleyball, badminton, athletics, and indoor games.</p>
        </div>
        <div class="circ-card">
          <span class="circ-badge b-event">EVENT</span>
          <h4>🔧 Workshop</h4>
          <p>Hands-on workshops conducted by industry professionals covering emerging technologies and professional skill development.</p>
        </div>
        <div class="circ-card">
          <span class="circ-badge b-event">EVENT</span>
          <h4>🎤 Seminar</h4>
          <p>Guest lectures and seminars by eminent academicians and industry experts open to all students across departments.</p>
        </div>
        <div class="circ-card">
          <div class="circ-new">UPCOMING</div>
          <span class="circ-badge b-event">EVENT</span>
          <h4>🎭 Cultural Fest</h4>
          <p>A vibrant cultural festival celebrating diversity through dance, music, drama, poetry, and art competitions across all departments.</p>
        </div>
      </div>
    </div>

    <!-- SCHOLARSHIP TAB -->
    <div class="tab-panel" id="tab-scholar">
      <!-- Scholarship highlight banner -->
      <div style="background:linear-gradient(135deg,#fffbeb,#fef3c7);border:1px solid #fcd34d;
                  border-radius:12px;padding:16px 22px;margin-bottom:22px;
                  display:flex;align-items:center;gap:14px;">
        <span style="font-size:32px">🏅</span>
        <div>
          <div style="font-size:14px;font-weight:700;color:#92400e;">Scholarship Programs — Session 2026–27</div>
          <div style="font-size:12.5px;color:#a16207;margin-top:3px;">
            Financial assistance available for meritorious and economically weaker students.
            Contact the Admission Office for more details.
          </div>
        </div>
      </div>
      <div class="circ-grid">

        <div class="circ-card">
          <div class="circ-new">OPEN</div>
          <span class="circ-badge b-scholar">SCHOLARSHIP</span>
          <h4>🥇 Merit Scholarship</h4>
          <p>Students who scored 75% or above in their previous academic year are eligible for a 25% waiver on tuition fees. Applicable to all programs.</p>
          <div style="margin-top:10px;display:flex;gap:8px;flex-wrap:wrap">
            <span style="background:#f0fdf4;border:1px solid #86efac;color:#166534;
                         font-size:10.5px;font-weight:700;padding:3px 10px;border-radius:6px;">75%+ Marks</span>
            <span style="background:#eff6ff;border:1px solid #bfdbfe;color:#1d4ed8;
                         font-size:10.5px;font-weight:700;padding:3px 10px;border-radius:6px;">25% Fee Waiver</span>
          </div>
        </div>

        <div class="circ-card">
          <div class="circ-new">OPEN</div>
          <span class="circ-badge b-scholar">SCHOLARSHIP</span>
          <h4>💰 Need-Based Financial Aid</h4>
          <p>Special financial assistance for economically weaker students belonging to EWS or BPL category. Family income certificate and BPL card are required.</p>
          <div style="margin-top:10px;display:flex;gap:8px;flex-wrap:wrap">
            <span style="background:#fef3c7;border:1px solid #fcd34d;color:#92400e;
                         font-size:10.5px;font-weight:700;padding:3px 10px;border-radius:6px;">EWS / BPL</span>
            <span style="background:#f0fdf4;border:1px solid #86efac;color:#166534;
                         font-size:10.5px;font-weight:700;padding:3px 10px;border-radius:6px;">Up to 50% Aid</span>
          </div>
        </div>

        <div class="circ-card">
          <span class="circ-badge b-scholar">SCHOLARSHIP</span>
          <h4>👧 Girl Student Scholarship</h4>
          <p>As part of the women empowerment initiative, all female students admitted to any program at ACET are entitled to a special fee concession.</p>
          <div style="margin-top:10px;display:flex;gap:8px;flex-wrap:wrap">
            <span style="background:#fdf4ff;border:1px solid #e9d5ff;color:#7c3aed;
                         font-size:10.5px;font-weight:700;padding:3px 10px;border-radius:6px;">All Programs</span>
            <span style="background:#f0fdf4;border:1px solid #86efac;color:#166534;
                         font-size:10.5px;font-weight:700;padding:3px 10px;border-radius:6px;">10% Concession</span>
          </div>
        </div>

        <div class="circ-card">
          <span class="circ-badge b-scholar">SCHOLARSHIP</span>
          <h4>🪖 Defence / Ex-Serviceman Ward</h4>
          <p>Children of serving or retired personnel from the Indian Army, Navy, or Air Force are eligible for a special scholarship. Original service certificate is mandatory.</p>
          <div style="margin-top:10px;display:flex;gap:8px;flex-wrap:wrap">
            <span style="background:#eff6ff;border:1px solid #bfdbfe;color:#1d4ed8;
                         font-size:10.5px;font-weight:700;padding:3px 10px;border-radius:6px;">Defence Ward</span>
            <span style="background:#f0fdf4;border:1px solid #86efac;color:#166534;
                         font-size:10.5px;font-weight:700;padding:3px 10px;border-radius:6px;">15% Fee Waiver</span>
          </div>
        </div>

        <div class="circ-card">
          <span class="circ-badge b-scholar">SCHOLARSHIP</span>
          <h4>👨‍👩‍👦 Sibling Concession</h4>
          <p>If two or more siblings from the same family are enrolled simultaneously at ACET, both will receive a fee concession. Apply at the admission counter.</p>
          <div style="margin-top:10px;display:flex;gap:8px;flex-wrap:wrap">
            <span style="background:#fef3c7;border:1px solid #fcd34d;color:#92400e;
                         font-size:10.5px;font-weight:700;padding:3px 10px;border-radius:6px;">2+ Siblings</span>
            <span style="background:#f0fdf4;border:1px solid #86efac;color:#166534;
                         font-size:10.5px;font-weight:700;padding:3px 10px;border-radius:6px;">10% Each</span>
          </div>
        </div>

        <div class="circ-card">
          <div class="circ-new">NEW</div>
          <span class="circ-badge b-scholar">SCHOLARSHIP</span>
          <h4>🏛️ UP Govt. Scholarship (SC/ST/OBC)</h4>
          <p>Students belonging to SC, ST, and OBC categories can apply under the Uttar Pradesh Government Scholarship Scheme. Apply online at: scholarship.up.gov.in</p>
          <div style="margin-top:10px;display:flex;gap:8px;flex-wrap:wrap">
            <span style="background:#fdf4ff;border:1px solid #e9d5ff;color:#7c3aed;
                         font-size:10.5px;font-weight:700;padding:3px 10px;border-radius:6px;">SC / ST / OBC</span>
            <span style="background:#eff6ff;border:1px solid #bfdbfe;color:#1d4ed8;
                         font-size:10.5px;font-weight:700;padding:3px 10px;border-radius:6px;">Govt. Funded</span>
          </div>
        </div>

      </div>

      <!-- How to apply box -->
      <div style="margin-top:24px;background:var(--light);border:1px solid var(--border);
                  border-radius:12px;padding:22px;">
        <h4 style="font-size:15px;font-weight:700;color:var(--navy);margin-bottom:14px;">
          📋 How to Apply for Scholarship
        </h4>
        <div style="display:grid;grid-template-columns:repeat(auto-fill,minmax(200px,1fr));gap:12px;font-size:12.5px;color:var(--text);">
          <div style="display:flex;gap:10px;align-items:flex-start;">
            <span style="background:var(--navy);color:#fff;border-radius:50%;width:22px;height:22px;
                         display:flex;align-items:center;justify-content:center;font-size:11px;font-weight:700;flex-shrink:0;">1</span>
            <span>Collect the Scholarship Application Form from the Admission Office</span>
          </div>
          <div style="display:flex;gap:10px;align-items:flex-start;">
            <span style="background:var(--navy);color:#fff;border-radius:50%;width:22px;height:22px;
                         display:flex;align-items:center;justify-content:center;font-size:11px;font-weight:700;flex-shrink:0;">2</span>
            <span>Attach required documents — marksheets, income certificate, category certificate</span>
          </div>
          <div style="display:flex;gap:10px;align-items:flex-start;">
            <span style="background:var(--navy);color:#fff;border-radius:50%;width:22px;height:22px;
                         display:flex;align-items:center;justify-content:center;font-size:11px;font-weight:700;flex-shrink:0;">3</span>
            <span>Submit the form before the last date: <strong>31 August 2026</strong></span>
          </div>
          <div style="display:flex;gap:10px;align-items:flex-start;">
            <span style="background:var(--gold);color:#fff;border-radius:50%;width:22px;height:22px;
                         display:flex;align-items:center;justify-content:center;font-size:11px;font-weight:700;flex-shrink:0;">✓</span>
            <span>Upon approval, the fee concession will be automatically adjusted in your account</span>
          </div>
        </div>
      </div>

    </div>
</div>
</div>

<!-- ═══════════════ CONTACT ═══════════════ -->
<div id="contact" class="sec reveal">
  <div class="sec-hd">
    <h2>Contact Us</h2>
    <div class="bar"></div>
    <p>Reach us for admissions, academic queries, or general information</p>
  </div>
  <div class="card">
    <div class="contact-grid">
      <div>
        <div class="cinfo-row">
          <div class="cinfo-icon">📍</div>
          <div>
            <div class="cinfo-lbl">ADDRESS</div>
            <div class="cinfo-val">
              Aligarh College of Engineering and Technology<br/>
              3 KM from Sasni Gate, Mathura Road,<br/>
              Aligarh, Uttar Pradesh
            </div>
          </div>
        </div>
        <div class="cinfo-row">
          <div class="cinfo-icon">✉️</div>
          <div>
            <div class="cinfo-lbl">EMAIL</div>
            <div class="cinfo-val">
              <a href="mailto:mail@acetup.org" style="color:var(--sky)">mail@acetup.org</a>
            </div>
          </div>
        </div>
        <div class="cinfo-row">
          <div class="cinfo-icon">📞</div>
          <div>
            <div class="cinfo-lbl">MOBILE NUMBERS</div>
            <div class="cinfo-val" style="font-family:'JetBrains Mono',monospace;font-size:12.5px;line-height:1.9">
              +91 95682 00010<br/>+91 95682 00062<br/>+91 95682 00063<br/>
              +91 95682 00064<br/>+91 95682 00065<br/>+91 95682 00071<br/>+91 95682 00077
            </div>
          </div>
        </div>
        <div class="cinfo-row">
          <div class="cinfo-icon">🕐</div>
          <div>
            <div class="cinfo-lbl">OFFICE HOURS</div>
            <div class="cinfo-val">Monday – Saturday: 9:00 AM – 5:00 PM</div>
          </div>
        </div>
      </div>
      <div>
        <div class="map-box">
          <div class="map-icon">🗺️</div>
          <div style="font-size:15px;font-weight:700">ACET, Aligarh</div>
          <p>3 KM from Sasni Gate, Mathura Road, Aligarh, Uttar Pradesh</p>
          <a href="https://maps.google.com/?q=Aligarh+College+of+Engineering+Technology+Aligarh"
             target="_blank"
             style="margin-top:8px;background:rgba(255,255,255,.12);border:1px solid rgba(255,255,255,.2);
                    color:#fff;padding:8px 18px;border-radius:8px;font-size:12px;font-weight:600;
                    display:inline-block;transition:.18s">
            📍 Open in Google Maps
          </a>
        </div>
        <!-- ══ QUICK MESSAGE FORM (SQLite-backed) ══ -->
        <div style="margin-top:20px;background:var(--light);border:1px solid var(--border);
                    border-radius:12px;padding:22px">
          <h4 style="font-size:15px;font-weight:700;color:var(--navy);margin-bottom:14px">
            📨 Quick Message
          </h4>
          <div style="display:flex;flex-direction:column;gap:10px">
            <input id="qName" type="text" placeholder="Your Name"
              style="width:100%;padding:10px 13px;border:1px solid var(--border);border-radius:8px;
                     font-size:13px;font-family:'Plus Jakarta Sans',sans-serif;outline:none"/>
            <input id="qEmail" type="email" placeholder="Your Email"
              style="width:100%;padding:10px 13px;border:1px solid var(--border);border-radius:8px;
                     font-size:13px;font-family:'Plus Jakarta Sans',sans-serif;outline:none"/>
            <textarea id="qMsg" rows="3" placeholder="Your message..."
              style="width:100%;padding:10px 13px;border:1px solid var(--border);border-radius:8px;
                     font-size:13px;font-family:'Plus Jakarta Sans',sans-serif;outline:none;resize:vertical"></textarea>
            <button id="sendBtn" onclick="sendMsg()"
              style="background:var(--navy);color:#fff;border:none;padding:11px;border-radius:8px;
                     font-size:13px;font-weight:600;cursor:pointer;font-family:'Plus Jakarta Sans',sans-serif;
                     transition:.18s">
              Send Message →
            </button>
            <div id="qSuccess" style="display:none;background:#f0fdf4;border:1px solid #86efac;
                 border-radius:8px;padding:11px;text-align:center;font-size:13px;color:#166534;font-weight:600">
              ✅ Message saved! We will get back to you soon.
            </div>
            <div id="qError" style="display:none;background:#fef2f2;border:1px solid #fca5a5;
                 border-radius:8px;padding:11px;text-align:center;font-size:13px;color:#b91c1c;font-weight:600">
              ❌ Error sending message. Please try again.
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</div>

<footer>
  <strong>ALIGARH COLLEGE OF ENGINEERING &amp; TECHNOLOGY</strong><br/>
  3 KM from Sasni Gate, Mathura Road, Aligarh · mail@acetup.org · +91 9568200010<br/>
  <span style="font-size:11px;margin-top:6px;display:block">
    Approved by AICTE, New Delhi &nbsp;|&nbsp; Affiliated to AKTU, Lucknow
    &nbsp;|&nbsp; <a href="/admin/login" style="color:var(--amber)">🔐 Admin Panel</a>
  </span>
</footer>

<script>
function switchTab(id, btn) {
  btn.closest('.card').querySelectorAll('.tab-panel').forEach(p => p.classList.remove('active'));
  btn.closest('.tabs').querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
  document.getElementById(id).classList.add('active');
  btn.classList.add('active');
}

// ── Send message via AJAX → Flask → SQLite
async function sendMsg() {
  const n = document.getElementById('qName').value.trim();
  const e = document.getElementById('qEmail').value.trim();
  const m = document.getElementById('qMsg').value.trim();
  if (!n || !e || !m) { alert('Please fill all fields.'); return; }

  const btn = document.getElementById('sendBtn');
  btn.textContent = 'Sending...';
  btn.disabled = true;

  try {
    const res = await fetch('/api/send-message', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({name: n, email: e, message: m})
    });
    const data = await res.json();
    if (data.success) {
      document.getElementById('qSuccess').style.display = 'block';
      document.getElementById('qName').value = '';
      document.getElementById('qEmail').value = '';
      document.getElementById('qMsg').value = '';
      setTimeout(() => document.getElementById('qSuccess').style.display = 'none', 4000);
    } else {
      document.getElementById('qError').style.display = 'block';
      setTimeout(() => document.getElementById('qError').style.display = 'none', 4000);
    }
  } catch(err) {
    document.getElementById('qError').style.display = 'block';
    setTimeout(() => document.getElementById('qError').style.display = 'none', 4000);
  }

  btn.textContent = 'Send Message →';
  btn.disabled = false;
}

const observer = new IntersectionObserver(entries => {
  entries.forEach(e => { if (e.isIntersecting) e.target.classList.add('visible'); });
}, { threshold: 0.08 });
document.querySelectorAll('.reveal').forEach(el => observer.observe(el));

const SECS = ['overview','departments','admission','fees','calendar','circulars','contact'];
window.addEventListener('scroll', () => {
  let cur = '';
  SECS.forEach(id => {
    const el = document.getElementById(id);
    if (el && el.getBoundingClientRect().top <= 80) cur = id;
  });
  document.querySelectorAll('.nav-links a').forEach(a => {
    a.classList.toggle('active', a.getAttribute('href') === '#' + cur);
  });
});
</script>
</body>
</html>'''

# ── Admin Panel HTML ────────────────────────────────────
ADMIN_HTML = '''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8"/>
<meta name="viewport" content="width=device-width, initial-scale=1.0"/>
<title>ACET – Admin: Messages</title>
<link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet"/>
<style>
:root {
  --navy:#0b1d3a;--mid:#1b4080;--gold:#c8961e;--amber:#f0b429;
  --cream:#fdf8f0;--light:#f3f6fb;--white:#fff;--text:#1a2740;
  --muted:#5a6f8a;--border:#dde5f0;--sky:#2563eb;
}
*{box-sizing:border-box;margin:0;padding:0}
body{font-family:'Plus Jakarta Sans',sans-serif;background:var(--cream);color:var(--text);min-height:100vh}
.topbar{
  background:var(--navy);padding:0 32px;height:60px;
  display:flex;align-items:center;justify-content:space-between;
  box-shadow:0 2px 16px rgba(0,0,0,.3);
}
.topbar-left{display:flex;align-items:center;gap:14px}
.topbar h1{font-size:16px;font-weight:700;color:#fff}
.topbar small{font-size:11px;color:#8faac8}
.back-btn{
  background:rgba(255,255,255,.1);color:#fff;border:1px solid rgba(255,255,255,.2);
  padding:7px 16px;border-radius:7px;font-size:12px;font-weight:600;
  cursor:pointer;text-decoration:none;transition:.18s;
}
.back-btn:hover{background:rgba(255,255,255,.18)}
.container{max-width:1100px;margin:0 auto;padding:36px 24px}
.stats-row{display:flex;gap:16px;flex-wrap:wrap;margin-bottom:32px}
.stat-card{
  background:var(--white);border:1px solid var(--border);
  border-radius:12px;padding:18px 24px;flex:1;min-width:150px;
  box-shadow:0 2px 12px rgba(11,29,58,.07);
}
.stat-card .num{
  font-size:32px;font-weight:700;color:var(--navy);display:block;line-height:1;
}
.stat-card .lbl{font-size:11.5px;color:var(--muted);margin-top:4px}
.stat-card.unread .num{color:#dc2626}
.section-hd{
  display:flex;align-items:center;justify-content:space-between;
  margin-bottom:20px;
}
.section-hd h2{font-size:20px;font-weight:700;color:var(--navy)}
.del-all-btn{
  background:#fef2f2;color:#b91c1c;border:1px solid #fca5a5;
  padding:7px 16px;border-radius:7px;font-size:12px;font-weight:600;
  cursor:pointer;transition:.18s;
}
.del-all-btn:hover{background:#fee2e2}
.msg-table{width:100%;border-collapse:collapse;background:var(--white);
           border-radius:12px;overflow:hidden;
           box-shadow:0 2px 16px rgba(11,29,58,.08);border:1px solid var(--border)}
.msg-table thead th{
  background:var(--navy);color:#fff;padding:13px 18px;
  text-align:left;font-size:11.5px;font-weight:600;letter-spacing:.3px;
}
.msg-table tbody td{
  padding:14px 18px;border-bottom:1px solid var(--border);
  font-size:13px;vertical-align:top;
}
.msg-table tbody tr:last-child td{border-bottom:none}
.msg-table tbody tr:hover td{background:#f5f8ff}
.msg-table tbody tr.unread td{background:#fffbf0}
.td-id{font-family:'JetBrains Mono',monospace;font-size:11px;color:var(--muted)}
.td-name{font-weight:700;color:var(--navy)}
.td-email a{color:var(--sky);font-size:12px}
.td-msg{max-width:320px;color:var(--text);line-height:1.55}
.td-time{font-family:'JetBrains Mono',monospace;font-size:11px;color:var(--muted);white-space:nowrap}
.unread-dot{
  display:inline-block;width:8px;height:8px;background:#ef4444;
  border-radius:50%;margin-right:6px;vertical-align:middle;
}
.read-btn{
  background:var(--light);color:var(--navy);border:1px solid var(--border);
  padding:4px 12px;border-radius:6px;font-size:11px;font-weight:600;
  cursor:pointer;transition:.18s;white-space:nowrap;
}
.read-btn:hover{background:#dbeafe;color:var(--sky)}
.del-btn{
  background:#fef2f2;color:#b91c1c;border:1px solid #fca5a5;
  padding:4px 12px;border-radius:6px;font-size:11px;font-weight:600;
  cursor:pointer;transition:.18s;margin-left:4px;white-space:nowrap;
}
.del-btn:hover{background:#fee2e2}
.empty-state{
  text-align:center;padding:60px 20px;color:var(--muted);
  background:var(--white);border-radius:12px;border:1px solid var(--border);
}
.empty-state .icon{font-size:48px;margin-bottom:12px}
.empty-state p{font-size:14px}
.logout-btn{
  background:#fef2f2;color:#b91c1c;border:1px solid #fca5a5;
  padding:7px 16px;border-radius:7px;font-size:12px;font-weight:600;
  cursor:pointer;text-decoration:none;transition:.18s;
}
.logout-btn:hover{background:#fee2e2}
</style>
</head>
<body>

<div class="topbar">
  <div class="topbar-left">
    <div style="width:36px;height:36px;border-radius:50%;background:linear-gradient(135deg,#c8961e,#f0b429);
                display:flex;align-items:center;justify-content:center;font-weight:700;color:#0b1d3a;font-size:16px">A</div>
    <div>
      <h1>ACET Admin — Messages</h1>
      <small>Contact form inbox · SQLite database · Logged in as <strong style="color:var(--amber)">admin</strong></small>
    </div>
  </div>
  <div style="display:flex;gap:10px;align-items:center">
    <a href="/" class="back-btn">← Back to Website</a>
    <a href="/admin/logout" class="logout-btn">🚪 Logout</a>
  </div>
</div>

<div class="container">
  <div class="stats-row">
    <div class="stat-card">
      <span class="num">{{ total }}</span>
      <div class="lbl">Total Messages</div>
    </div>
    <div class="stat-card unread">
      <span class="num">{{ unread }}</span>
      <div class="lbl">Unread Messages</div>
    </div>
    <div class="stat-card">
      <span class="num">{{ read }}</span>
      <div class="lbl">Read Messages</div>
    </div>
  </div>

  <div class="section-hd">
    <h2>📬 All Messages</h2>
    {% if messages %}
    <button class="del-all-btn" onclick="if(confirm('Sare messages delete kar dein?')) window.location='/admin/delete-all'">
      🗑️ Sab Delete Karo
    </button>
    {% endif %}
  </div>

  {% if messages %}
  <table class="msg-table">
    <thead>
      <tr>
        <th>#</th>
        <th>Name</th>
        <th>Email</th>
        <th>Message</th>
        <th>Received At</th>
        <th>Actions</th>
      </tr>
    </thead>
    <tbody>
      {% for msg in messages %}
      <tr class="{{ 'unread' if not msg['is_read'] else '' }}">
        <td class="td-id">
          {% if not msg['is_read'] %}<span class="unread-dot"></span>{% endif %}
          #{{ msg['id'] }}
        </td>
        <td class="td-name">{{ msg['name'] }}</td>
        <td class="td-email"><a href="mailto:{{ msg['email'] }}">{{ msg['email'] }}</a></td>
        <td class="td-msg">{{ msg['message'] }}</td>
        <td class="td-time">{{ msg['received_at'] }}</td>
        <td>
          {% if not msg['is_read'] %}
          <button class="read-btn" onclick="markRead({{ msg['id'] }}, this)">✓ Read</button>
          {% endif %}
          <button class="del-btn" onclick="deleteMsg({{ msg['id'] }}, this)">🗑</button>
        </td>
      </tr>
      {% endfor %}
    </tbody>
  </table>
  {% else %}
  <div class="empty-state">
    <div class="icon">📭</div>
    <p>Abhi koi message nahi aaya hai.<br/>Contact form se message aane par yahan dikhega.</p>
  </div>
  {% endif %}
</div>

<script>
async function markRead(id, btn) {
  const res = await fetch('/admin/mark-read/' + id, {method:'POST'});
  const data = await res.json();
  if (data.success) {
    btn.closest('tr').classList.remove('unread');
    const dot = btn.closest('tr').querySelector('.unread-dot');
    if (dot) dot.remove();
    btn.remove();
    location.reload();
  }
}

async function deleteMsg(id, btn) {
  if (!confirm('Is message ko delete kar dein?')) return;
  const res = await fetch('/admin/delete/' + id, {method:'POST'});
  const data = await res.json();
  if (data.success) {
    btn.closest('tr').style.opacity = '0';
    btn.closest('tr').style.transition = '.3s';
    setTimeout(() => { btn.closest('tr').remove(); location.reload(); }, 300);
  }
}
</script>
</body>
</html>'''


# ── Login Page HTML ─────────────────────────────────────
LOGIN_HTML = '''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8"/>
<meta name="viewport" content="width=device-width, initial-scale=1.0"/>
<title>ACET Admin — Login</title>
<link href="https://fonts.googleapis.com/css2?family=Cormorant+Garamond:wght@400;600;700&family=Plus+Jakarta+Sans:wght@300;400;500;600;700&display=swap" rel="stylesheet"/>
<style>
:root{--navy:#0b1d3a;--mid:#1b4080;--gold:#c8961e;--amber:#f0b429;--cream:#fdf8f0;--sky:#2563eb;--border:#dde5f0;}
*{box-sizing:border-box;margin:0;padding:0}
body{
  font-family:"Plus Jakarta Sans",sans-serif;
  background:linear-gradient(155deg,var(--navy) 0%,#0f2548 55%,#0d3060 100%);
  min-height:100vh;display:flex;align-items:center;justify-content:center;
}
.login-wrap{
  background:#fff;border-radius:20px;padding:48px 44px;
  width:100%;max-width:420px;
  box-shadow:0 24px 80px rgba(0,0,0,.35);
  position:relative;overflow:hidden;
}
.login-wrap::before{
  content:"";position:absolute;top:-40px;right:-40px;
  width:130px;height:130px;border-radius:50%;
  background:linear-gradient(135deg,var(--gold),var(--amber));
  opacity:.12;
}
.login-logo{
  display:flex;align-items:center;justify-content:center;gap:12px;margin-bottom:28px;
}
.login-emblem{
  width:52px;height:52px;border-radius:50%;
  background:linear-gradient(135deg,var(--gold),var(--amber));
  display:flex;align-items:center;justify-content:center;
  font-family:"Cormorant Garamond",serif;font-size:22px;font-weight:700;color:var(--navy);
}
.login-title{
  font-family:"Cormorant Garamond",serif;font-size:22px;
  font-weight:700;color:var(--navy);line-height:1.2;
}
.login-title small{
  display:block;font-family:"Plus Jakarta Sans",sans-serif;
  font-size:10.5px;color:#8faac8;font-weight:400;letter-spacing:.5px;margin-top:2px;
}
h2{
  font-family:"Cormorant Garamond",serif;font-size:26px;
  font-weight:700;color:var(--navy);margin-bottom:6px;text-align:center;
}
.sub{font-size:12.5px;color:#8faac8;text-align:center;margin-bottom:28px}
.field{margin-bottom:16px}
.field label{
  display:block;font-size:11.5px;font-weight:700;color:var(--navy);
  letter-spacing:.4px;margin-bottom:6px;
}
.field input{
  width:100%;padding:12px 15px;
  border:1.5px solid var(--border);border-radius:9px;
  font-size:13.5px;font-family:"Plus Jakarta Sans",sans-serif;
  outline:none;transition:.18s;color:#1a2740;background:#f9fbff;
}
.field input:focus{border-color:var(--sky);background:#fff;box-shadow:0 0 0 3px rgba(37,99,235,.1)}
.login-btn{
  width:100%;padding:13px;
  background:linear-gradient(135deg,var(--navy),var(--mid));
  color:#fff;border:none;border-radius:9px;
  font-size:14px;font-weight:700;cursor:pointer;
  font-family:"Plus Jakarta Sans",sans-serif;
  transition:.2s;margin-top:6px;letter-spacing:.3px;
}
.login-btn:hover{opacity:.88;transform:translateY(-1px);box-shadow:0 8px 24px rgba(11,29,58,.25)}
.error-box{
  background:#fef2f2;border:1px solid #fca5a5;
  border-radius:9px;padding:11px 15px;
  font-size:12.5px;color:#b91c1c;font-weight:600;
  text-align:center;margin-bottom:18px;
  display:flex;align-items:center;justify-content:center;gap:7px;
}
.back-link{
  text-align:center;margin-top:20px;font-size:12px;color:#8faac8;
}
.back-link a{color:var(--sky);font-weight:600;text-decoration:none}
.back-link a:hover{text-decoration:underline}
.cred-hint{
  background:#f0f9ff;border:1px solid #bae6fd;border-radius:8px;
  padding:10px 14px;font-size:11.5px;color:#0369a1;margin-top:14px;
  text-align:center;line-height:1.7;
}
</style>
</head>
<body>
<div class="login-wrap">
  <div class="login-logo">
    <div class="login-emblem">A</div>
    <div class="login-title">
      ACET Admin
      <small>ALIGARH COLLEGE OF ENGINEERING &amp; TECHNOLOGY</small>
    </div>
  </div>
  <h2>🔐 Admin Login</h2>
  <p class="sub">Sirf authorized admin hi yahan enter kar sakte hain</p>

  {% if error %}
  <div class="error-box">❌ {{ error }}</div>
  {% endif %}

  <form method="POST" action="/admin/login">
    <div class="field">
      <label>USERNAME</label>
      <input type="text" name="username" placeholder="Enter username" autocomplete="username" required/>
    </div>
    <div class="field">
      <label>PASSWORD</label>
      <input type="password" name="password" placeholder="Enter password" autocomplete="current-password" required/>
    </div>
    <button type="submit" class="login-btn">Login to Admin Panel →</button>
  </form>

  <div class="cred-hint">
    🧪 <strong>Dev Credentials:</strong><br/>
    Username: <strong>admin</strong> &nbsp;|&nbsp; Password: <strong>admin123</strong>
  </div>

  <div class="back-link">
    <a href="/">← Back to ACET Website</a>
  </div>
</div>
</body>
</html>'''


# ══════════════════════════════════════════════════════
#  ROUTES
# ══════════════════════════════════════════════════════

@app.route('/')
def home():
    return render_template_string(MAIN_HTML)


# ── Contact form API ────────────────────────────────────
@app.route('/api/send-message', methods=['POST'])
def send_message():
    """Receive form data and store in SQLite"""
    data    = request.get_json()
    name    = data.get('name', '').strip()
    email   = data.get('email', '').strip()
    message = data.get('message', '').strip()

    if not name or not email or not message:
        return jsonify({'success': False, 'error': 'All fields required'}), 400

    now = datetime.now().strftime('%d %b %Y, %I:%M %p')
    try:
        conn = get_db()
        conn.execute(
            'INSERT INTO messages (name, email, message, received_at) VALUES (?, ?, ?, ?)',
            (name, email, message, now)
        )
        conn.commit()
        conn.close()
        return jsonify({'success': True, 'message': 'Message stored successfully'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


# ── Admin Login ─────────────────────────────────────────
@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    # Already logged in → go straight to dashboard
    if session.get('admin_logged_in'):
        return redirect(url_for('admin_messages'))

    error = None
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()

        if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
            session['admin_logged_in'] = True
            session['admin_user']      = username
            return redirect(url_for('admin_messages'))
        else:
            error = 'Galat username ya password. Dobara try karein.'

    return render_template_string(LOGIN_HTML, error=error)


# ── Admin Logout ────────────────────────────────────────
@app.route('/admin/logout')
def admin_logout():
    session.clear()
    return redirect(url_for('admin_login'))


# ── Admin Dashboard (protected) ─────────────────────────
@app.route('/admin/messages')
@login_required
def admin_messages():
    """Admin panel — view all messages (login required)"""
    conn     = get_db()
    messages = conn.execute('SELECT * FROM messages ORDER BY id DESC').fetchall()
    total    = len(messages)
    unread   = sum(1 for m in messages if not m['is_read'])
    read     = total - unread
    conn.close()
    return render_template_string(ADMIN_HTML,
                                  messages=messages,
                                  total=total,
                                  unread=unread,
                                  read=read)


# ── Mark read ───────────────────────────────────────────
@app.route('/admin/mark-read/<int:msg_id>', methods=['POST'])
@login_required
def mark_read(msg_id):
    try:
        conn = get_db()
        conn.execute('UPDATE messages SET is_read = 1 WHERE id = ?', (msg_id,))
        conn.commit()
        conn.close()
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


# ── Delete single ───────────────────────────────────────
@app.route('/admin/delete/<int:msg_id>', methods=['POST'])
@login_required
def delete_message(msg_id):
    try:
        conn = get_db()
        conn.execute('DELETE FROM messages WHERE id = ?', (msg_id,))
        conn.commit()
        conn.close()
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


# ── Delete all ──────────────────────────────────────────
@app.route('/admin/delete-all')
@login_required
def delete_all():
    conn = get_db()
    conn.execute('DELETE FROM messages')
    conn.commit()
    conn.close()
    return redirect(url_for('admin_messages'))


if __name__ == '__main__':
    init_db()
    print("\n" + "="*58)
    print("  ACET Dashboard — Secure Admin Login + SQLite")
    print("="*58)
    print("  🌐 Website:       http://127.0.0.1:5000/")
    print("  🔐 Admin Login:   http://127.0.0.1:5000/admin/login")
    print("  📬 Dashboard:     http://127.0.0.1:5000/admin/messages")
    print("  🗄️  Database:      acet_messages.db (auto-created)")
    print("  👤 Username:      admin")
    print("  🔑 Password:      admin123")
    print("="*58 + "\n")
    app.run(debug=True)
