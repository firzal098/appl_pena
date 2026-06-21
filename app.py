import streamlit as st
import json
import os
import datetime
import pandas as pd
import altair as alt

# --- KONFIGURASI HALAMAN ---
st.set_page_config(
    page_title="Pena - Gamified Productivity & Budgeting Portal",
    page_icon="✒️",
    layout="wide",
    initial_sidebar_state="expanded"
)

DB_PATH = "pena_database.json"

# --- DEKORASI CSS KUSTOM UNTUK DARK MODE PREMIUM ---
st.markdown("""
<style>
    /* Mengubah font utama dan latar belakang */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Outfit:wght@400;500;600;700;800&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }
    
    .stApp {
        background-color: #0f111a;
        color: #f1f5f9;
    }
    
    /* Ganti gaya sidebar */
    [data-testid="stSidebar"] {
        background-color: #121420;
        border-right: 1px solid #2e3248;
    }
    
    /* Card/Kartu Visual Premium */
    .card {
        background-color: #161824;
        border: 1px solid #2e3248;
        border-radius: 12px;
        padding: 20px;
        margin-bottom: 16px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.4);
    }
    
    .card-title {
        font-family: 'Outfit', sans-serif;
        font-size: 1.15rem;
        font-weight: 700;
        color: #f1f5f9;
        margin-bottom: 12px;
        display: flex;
        align-items: center;
        gap: 8px;
    }
    
    /* Progress Bar EXP Kustom */
    .exp-bar-bg {
        background-color: #1e2238;
        border-radius: 8px;
        height: 16px;
        width: 100%;
        margin-top: 8px;
        overflow: hidden;
    }
    
    .exp-bar-fill {
        background: linear-gradient(90deg, #f59e0b, #fbbf24);
        height: 100%;
        border-radius: 8px;
        transition: width 0.5s ease-out;
    }
    
    /* Alert / Alarm Overbudget */
    .alert-banner {
        background-color: rgba(239, 68, 68, 0.08);
        border: 1px solid #ef4444;
        color: #f87171;
        padding: 12px 16px;
        border-radius: 8px;
        font-size: 0.9rem;
        font-weight: bold;
        margin-bottom: 16px;
        display: flex;
        align-items: center;
        gap: 8px;
    }
    
    /* Podium untuk Leaderboard */
    .podium-container {
        display: flex;
        justify-content: center;
        align-items: flex-end;
        gap: 16px;
        margin-bottom: 24px;
        padding: 20px;
        background: linear-gradient(180deg, #1f2235, #121420);
        border: 1px solid #2e3248;
        border-radius: 12px;
    }
    
    .podium-card {
        background-color: #161824;
        border: 1.5px solid #2e3248;
        border-radius: 8px;
        padding: 16px;
        text-align: center;
        flex: 1;
        max-width: 160px;
        box-shadow: 0 4px 10px rgba(0,0,0,0.3);
        display: flex;
        flex-direction: column;
        justify-content: space-between;
        align-items: center;
        box-sizing: border-box;
    }
    
    .podium-rank1 {
        border-color: #f59e0b;
        min-height: 220px;
        background: rgba(245, 158, 11, 0.03);
    }
    
    .podium-rank2 {
        border-color: #64748b;
        min-height: 195px;
    }
    
    .podium-rank3 {
        border-color: #b45309;
        min-height: 175px;
    }
    
    .avatar-circle {
        width: 40px;
        height: 40px;
        border-radius: 50%;
        background-color: #1f2235;
        border: 2px solid #64748b;
        display: flex;
        align-items: center;
        justify-content: center;
        margin: 0 auto 10px auto;
        font-weight: bold;
        color: #f1f5f9;
    }
    
    .avatar-rank1 {
        border-color: #f59e0b;
        width: 48px;
        height: 48px;
        font-size: 1.1rem;
    }
    
    /* Checklist Tugas */
    .task-item {
        background-color: #161824;
        border: 1px solid #2e3248;
        border-radius: 8px;
        padding: 12px 16px;
        margin-bottom: 10px;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }
    
    .badge {
        background-color: rgba(99, 102, 241, 0.1);
        border: 1px solid #6366f1;
        color: #818cf8;
        padding: 2px 8px;
        border-radius: 12px;
        font-size: 0.75rem;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

# --- DATABASE INTI & LOGIKAN PERSISTENSI JSON ---
def load_db():
    if not os.path.exists(DB_PATH):
        # Inisialisasi Database Bawaan
        default_db = {
            "users": {
                "firzal@pena.com": {
                    "name": "Firzal Akbar Ramadhan",
                    "password": "123",
                    "level": 18,
                    "exp": 450,
                    "streak": 5,
                    "budget_limit": 1500000.0,
                    "reminders_enabled": True,
                    "reminder_time": "19:30"
                },
                "rian@pena.com": {
                    "name": "Rian M.",
                    "password": "123",
                    "level": 25,
                    "exp": 850,
                    "streak": 14,
                    "budget_limit": 2000000.0,
                    "reminders_enabled": True,
                    "reminder_time": "19:00"
                },
                "amel@pena.com": {
                    "name": "Amel",
                    "password": "123",
                    "level": 15,
                    "exp": 120,
                    "streak": 3,
                    "budget_limit": 1000000.0,
                    "reminders_enabled": False,
                    "reminder_time": "20:00"
                },
                "budi@pena.com": {
                    "name": "Budi Hartono",
                    "password": "123",
                    "level": 12,
                    "exp": 200,
                    "streak": 2,
                    "budget_limit": 1200000.0,
                    "reminders_enabled": True,
                    "reminder_time": "19:30"
                },
                "sarah@pena.com": {
                    "name": "Sarah Wijaya",
                    "password": "123",
                    "level": 10,
                    "exp": 500,
                    "streak": 1,
                    "budget_limit": 1500000.0,
                    "reminders_enabled": True,
                    "reminder_time": "18:30"
                },
                "dimas@pena.com": {
                    "name": "Dimas Pratama",
                    "password": "123",
                    "level": 9,
                    "exp": 900,
                    "streak": 0,
                    "budget_limit": 800000.0,
                    "reminders_enabled": False,
                    "reminder_time": "20:30"
                }
            },
            "activities": [
                {"email": "firzal@pena.com", "title": "Jogging Pagi", "category": "Olahraga", "status": "completed", "exp_rewarded": 50, "date": "2026-06-21"},
                {"email": "firzal@pena.com", "title": "Kuliah APPL", "category": "Akademik", "status": "pending", "exp_rewarded": 50, "date": "2026-06-21"},
                {"email": "firzal@pena.com", "title": "Mengerjakan Freelance", "category": "Kerja", "status": "pending", "exp_rewarded": 50, "date": "2026-06-21"},
                {"email": "firzal@pena.com", "title": "Belajar Piano", "category": "Hobi", "status": "pending", "exp_rewarded": 50, "date": "2026-06-21"}
            ],
            "categories": [
                {"email": "firzal@pena.com", "name": "Olahraga", "color": "#6366f1"},
                {"email": "firzal@pena.com", "name": "Akademik", "color": "#f59e0b"},
                {"email": "firzal@pena.com", "name": "Kerja", "color": "#10b981"},
                {"email": "firzal@pena.com", "name": "Hobi", "color": "#ec4899"}
            ],
            "finances": [
                {"email": "firzal@pena.com", "type": "Sink", "amount": 50000.0, "category": "Makanan & Minuman", "description": "Makan malam nasi goreng", "date": "2026-06-21"},
                {"email": "firzal@pena.com", "type": "Sink", "amount": 800000.0, "category": "Kebutuhan Akademik", "description": "Beli Buku Referensi", "date": "2026-06-20"},
                {"email": "firzal@pena.com", "type": "Sink", "amount": 400000.0, "category": "Transportasi", "description": "Isi Saldo MRT", "date": "2026-06-19"},
                {"email": "firzal@pena.com", "type": "Gain", "amount": 1500000.0, "category": "Lain-lain", "description": "Uang Saku Bulanan", "date": "2026-06-01"}
            ],
            "user_badges": [
                {"email": "firzal@pena.com", "badge": "Pemula", "unlocked_at": "2026-06-01"},
                {"email": "firzal@pena.com", "badge": "Disiplin", "unlocked_at": "2026-06-10"},
                {"email": "firzal@pena.com", "badge": "Hemat", "unlocked_at": "2026-06-15"}
            ]
        }
        with open(DB_PATH, "w") as f:
            json.dump(default_db, f, indent=4)
            
    with open(DB_PATH, "r") as f:
        return json.load(f)

def save_db(db):
    with open(DB_PATH, "w") as f:
        json.dump(db, f, indent=4)

db = load_db()

# --- INITIALIZE SESSION STATES ---
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "user_email" not in st.session_state:
    st.session_state.user_email = ""

# --- AUTENTIKASI: LOGIN / REGISTER ---
def render_login_page():
    st.markdown("<div style='height: 40px;'></div>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown("""
        <div style='text-align: center; margin-bottom: 24px;'>
            <h1 style="font-family: 'Outfit', sans-serif; font-weight: 800; font-size: 3rem; background: linear-gradient(135deg, #6366f1, #ec4899); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">Pena</h1>
            <p style='color: #8f9bb3; font-size: 1.1rem;'>Gamified Productivity & Personal Finance Manager</p>
        </div>
        """, unsafe_allow_html=True)
        
        tab_login, tab_register = st.tabs(["🔒 Masuk Ke Akun", "👤 Daftar Baru"])
        
        with tab_login:
            email = st.text_input("Alamat Email", key="login_email")
            password = st.text_input("Kata Sandi", type="password", key="login_pass")
            
            if st.button("Masuk", use_container_width=True):
                if email in db["users"] and db["users"][email]["password"] == password:
                    st.session_state.logged_in = True
                    st.session_state.user_email = email
                    st.toast(f"Selamat datang kembali, {db['users'][email]['name']}! 👋")
                    st.rerun()
                else:
                    st.error("Email atau password salah. Coba lagi.")
                    
        with tab_register:
            reg_name = st.text_input("Nama Lengkap")
            reg_email = st.text_input("Alamat Email")
            reg_password = st.text_input("Kata Sandi Baru", type="password")
            reg_budget = st.number_input("Limit Anggaran Bulanan (Rp)", min_value=10000.0, value=1500000.0, step=50000.0)
            
            if st.button("Daftar Sekarang", use_container_width=True):
                if not reg_name or not reg_email or not reg_password:
                    st.warning("Mohon lengkapi semua kolom.")
                elif reg_email in db["users"]:
                    st.error("Alamat email sudah terdaftar.")
                else:
                    # Tambah user baru ke DB
                    db["users"][reg_email] = {
                        "name": reg_name,
                        "password": reg_password,
                        "level": 1,
                        "exp": 0,
                        "streak": 0,
                        "budget_limit": reg_budget,
                        "reminders_enabled": True,
                        "reminder_time": "19:30"
                    }
                    # Inisialisasi kategori bawaan
                    default_cats = [
                        {"email": reg_email, "name": "Olahraga", "color": "#6366f1"},
                        {"email": reg_email, "name": "Akademik", "color": "#f59e0b"},
                        {"email": reg_email, "name": "Kerja", "color": "#10b981"},
                        {"email": reg_email, "name": "Hobi", "color": "#ec4899"}
                    ]
                    db["categories"].extend(default_cats)
                    # Inisialisasi lencana pertama
                    db["user_badges"].append({
                        "email": reg_email,
                        "badge": "Pemula",
                        "unlocked_at": datetime.date.today().strftime("%Y-%m-%d")
                    })
                    save_db(db)
                    
                    st.success("Akun berhasil dibuat! Silakan masuk pada tab login.")

if not st.session_state.logged_in:
    render_login_page()
else:
    # --- PROSES MAIN APP ---
    email = st.session_state.user_email
    user = db["users"][email]
    
    # Kategori khusus user
    user_cats = [c["name"] for c in db["categories"] if c["email"] == email]
    cat_colors = {c["name"]: c["color"] for c in db["categories"] if c["email"] == email}
    
    # --- SIMULASI PENGINGAT / REMINDER ---
    today_str = datetime.date.today().strftime("%Y-%m-%d")
    user_today_tasks = [t for t in db["activities"] if t["email"] == email and t["date"] == today_str]
    pending_tasks = [t for t in user_today_tasks if t["status"] == "pending"]
    
    # --- MENAMBAH SIDEBAR & STATS ---
    st.sidebar.markdown(f"""
    <div style='text-align: center; padding-bottom: 20px;'>
        <div class="avatar-circle avatar-rank1">{user['name'][:2].upper()}</div>
        <h3 style="margin-bottom: 0px; font-family: 'Outfit';">{user['name']}</h3>
        <p style='color: #8f9bb3; font-size: 0.85rem;'>{email}</p>
        <span class="badge" style="background-color: rgba(245,158,11,0.15); border-color: #f59e0b; color: #f59e0b;">Lv. {user['level']}</span>
    </div>
    """, unsafe_allow_html=True)
    
    menu = st.sidebar.radio(
        "Menu Utama Aplikasi",
        ["🏠 Beranda (Dashboard)", "📝 Tracker Harian", "💰 Manajemen Keuangan", "📊 Grafik & Laporan", "🏆 Leaderboard Global", "⚙️ Pengaturan Akun"]
    )
    
    if st.sidebar.button("Keluar Akun", use_container_width=True):
        st.session_state.logged_in = False
        st.session_state.user_email = ""
        st.rerun()
        
    st.sidebar.markdown("""
    <div style='text-align: center; margin-top: 80px; font-size: 0.75rem; color: #8f9bb3;'>
        Pena Prototype v1.0<br>
        Tugas Kelompok APPL
    </div>
    """, unsafe_allow_html=True)

    # --- 1. BERANDA TAB (HOME / DASHBOARD) ---
    if menu == "🏠 Beranda (Dashboard)":
        st.title("🏠 Dashboard Utama - Pena")
        
        # Simulasi Push Notifikasi Lokal
        if user["reminders_enabled"] and len(pending_tasks) > 0:
            st.markdown(f"""
            <div class="alert-banner">
                🔔 <strong>Simulasi Pengingat:</strong> Kamu memiliki {len(pending_tasks)} aktivitas yang belum diselesaikan hari ini! 
                Jangan biarkan streak harianmu putus.
            </div>
            """, unsafe_allow_html=True)
            
        col_stats1, col_stats2, col_stats3 = st.columns(3)
        
        with col_stats1:
            st.markdown(f"""
            <div class="card">
                <div class="card-title">🔥 Daily Streak</div>
                <h1 style='color: #ec4899; font-size: 2.8rem; margin: 0;'>{user['streak']} Hari</h1>
                <p style='color: #8f9bb3; font-size: 0.85rem; margin-top: 5px;'>Konsistensi catat berturut-turut</p>
            </div>
            """, unsafe_allow_html=True)
            
        with col_stats2:
            # Hitung EXP %
            exp_target = user["level"] * 100
            exp_pct = min(100, int((user["exp"] / exp_target) * 100))
            
            st.markdown(f"""
            <div class="card">
                <div class="card-title">🎖️ Level & Progress EXP</div>
                <h2 style='margin:0; font-family: Outfit;'>Level {user['level']}</h2>
                <p style='color: #8f9bb3; font-size: 0.85rem; margin: 0;'>{user['exp']} / {exp_target} EXP</p>
                <div class="exp-bar-bg">
                    <div class="exp-bar-fill" style="width: {exp_pct}%;"></div>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
        with col_stats3:
            # Hitung Keuangan Bulan Ini
            month_str = datetime.date.today().strftime("%Y-%m")
            user_sinks = [f for f in db["finances"] if f["email"] == email and f["type"] == "Sink" and f["date"].startswith(month_str)]
            user_gains = [f for f in db["finances"] if f["email"] == email and f["type"] == "Gain" and f["date"].startswith(month_str)]
            total_spent = sum([f["amount"] for f in user_sinks])
            total_gain = sum([f["amount"] for f in user_gains])
            remaining_budget = user["budget_limit"] - total_spent + total_gain
            
            budget_color = "#ef4444" if remaining_budget < 0 else "#10b981" if remaining_budget > 0.2 * user["budget_limit"] else "#f59e0b"
            
            st.markdown(f"""
            <div class="card">
                <div class="card-title">💰 Sisa Anggaran Bulan Ini</div>
                <h1 style='color: {budget_color}; font-size: 2.2rem; margin: 0;'>Rp {remaining_budget:,.0f}</h1>
                <p style='color: #8f9bb3; font-size: 0.85rem; margin-top: 5px;'>Limit Bulanan: Rp {user['budget_limit']:,.0f}</p>
            </div>
            """, unsafe_allow_html=True)
            
        # Milestone Lencana yang Terbuka
        st.subheader("🏅 Lencana Milestone Kamu")
        user_badges_names = [b["badge"] for b in db["user_badges"] if b["email"] == email]
        
        col_b1, col_b2, col_b3, col_b4 = st.columns(4)
        badges_list = [
            ("🏅", "Pemula", "Pertama kali bergabung dengan Pena.", "Pemula" in user_badges_names, "#f59e0b"),
            ("🏆", "Disiplin", "Pertahankan streak mencatat 3 hari.", "Disiplin" in user_badges_names, "#10b981"),
            ("💎", "Hemat", "Sisa saldo keuangan bulan ini > 20% limit.", "Hemat" in user_badges_names, "#6366f1"),
            ("👑", "Master", "Capai tingkat Level 20.", "Master" in user_badges_names, "#a855f7")
        ]
        
        for idx, (icon, name, desc, unlocked, color) in enumerate(badges_list):
            with [col_b1, col_b2, col_b3, col_b4][idx]:
                if unlocked:
                    st.markdown(f"""
                    <div class="card" style="border-color: {color}; text-align: center; background: rgba(99,102,241,0.02);">
                        <div style="font-size: 2.2rem; margin-bottom: 5px;">{icon}</div>
                        <h4 style="margin: 0; color: {color};">{name}</h4>
                        <p style="color: #8f9bb3; font-size: 0.75rem; margin-top: 5px; height: 35px;">{desc}</p>
                    </div>
                    """, unsafe_allow_html=True)
                    if st.button(f"Bagikan Lencana {name}", key=f"share_{name}"):
                        st.toast(f"📢 Lencana '{name}' berhasil dibagikan ke Media Sosial Anda!")
                        st.balloons()
                else:
                    st.markdown(f"""
                    <div class="card" style="opacity: 0.4; text-align: center;">
                        <div style="font-size: 2.2rem; margin-bottom: 5px;">🔒</div>
                        <h4 style="margin: 0; color: #8f9bb3;">{name} (Terkunci)</h4>
                        <p style="color: #8f9bb3; font-size: 0.75rem; margin-top: 5px; height: 35px;">{desc}</p>
                    </div>
                    """, unsafe_allow_html=True)
                    st.button("Terkunci", key=f"share_locked_{idx}", disabled=True)

    # --- 2. TRACKER TAB ---
    elif menu == "📝 Tracker Harian":
        st.title("📝 Pelacakan Aktivitas Harian")
        
        col_track1, col_track2 = st.columns([2, 1])
        
        with col_track1:
            st.subheader("Checklist Kegiatan Hari Ini")
            
            if len(user_today_tasks) == 0:
                st.info("Kamu belum menambahkan kegiatan apa pun untuk hari ini. Gunakan form di sebelah kanan!")
            else:
                for idx, task in enumerate(user_today_tasks):
                    is_completed = (task["status"] == "completed")
                    
                    # Simulasikan item
                    col_chk, col_lbl, col_badge, col_exp = st.columns([1, 7, 2, 2])
                    
                    with col_chk:
                        # Buat checkbox interaktif
                        checked = st.checkbox("", value=is_completed, key=f"chk_{idx}")
                        
                        # Deteksi Perubahan Centang
                        if checked != is_completed:
                            # Cari index di db global
                            global_idx = [i for i, t in enumerate(db["activities"]) if t["email"] == email and t["date"] == today_str][idx]
                            
                            if checked:
                                db["activities"][global_idx]["status"] = "completed"
                                # Tambah EXP
                                user["exp"] += 50
                                st.toast(f"Hebat! +50 EXP didapat dari '{task['title']}'! 🎉")
                                
                                # Cek Level Up
                                exp_needed = user["level"] * 100
                                if user["exp"] >= exp_needed:
                                    user["level"] += 1
                                    user["exp"] -= exp_needed
                                    st.success(f"🎊 SELAMAT! Kamu naik ke Level {user['level']}! 🎊")
                                    st.balloons()
                                    
                                    # Pemicu Unlock Lencana Master jika Lv 20
                                    if user["level"] >= 20 and "Master" not in [b["badge"] for b in db["user_badges"] if b["email"] == email]:
                                        db["user_badges"].append({"email": email, "badge": "Master", "unlocked_at": today_str})
                                        st.toast("👑 Lencana 'Master' Berhasil Terbuka!")
                                        
                                # Update Streak (jika hari ini pertama kali centang)
                                completed_today = [t for t in db["activities"] if t["email"] == email and t["date"] == today_str and t["status"] == "completed"]
                                if len(completed_today) == 1: # Baru satu yang kelar hari ini
                                    user["streak"] += 1
                                    st.toast(f"Streak-mu naik menjadi {user['streak']} hari berturut-turut! 🔥")
                                    
                                    # Pemicu Unlock Lencana Disiplin jika streak >= 3
                                    if user["streak"] >= 3 and "Disiplin" not in [b["badge"] for b in db["user_badges"] if b["email"] == email]:
                                        db["user_badges"].append({"email": email, "badge": "Disiplin", "unlocked_at": today_str})
                                        st.toast("🏆 Lencana 'Disiplin' Berhasil Terbuka!")
                            else:
                                db["activities"][global_idx]["status"] = "pending"
                                user["exp"] = max(0, user["exp"] - 50)
                                st.toast("Status kegiatan diubah menjadi pending. -50 EXP.")
                                
                            save_db(db)
                            st.rerun()
                            
                    with col_lbl:
                        label_style = f"<span style='color: #8f9bb3; text-decoration: line-through; font-weight: bold;'>{task['title']}</span>" if is_completed else f"<span style='color: #f1f5f9; font-weight: bold;'>{task['title']}</span>"
                        st.markdown(label_style, unsafe_allow_html=True)
                        
                    with col_badge:
                        color = cat_colors.get(task["category"], "#6366f1")
                        st.markdown(f"<span class='badge' style='border-color: {color}; color: {color}; background-color: rgba(0,0,0,0);'>{task['category']}</span>", unsafe_allow_html=True)
                        
                    with col_exp:
                        st.markdown("<span style='color: #f59e0b; font-size: 0.9rem; font-weight: bold;'>+50 EXP</span>", unsafe_allow_html=True)
                        
                    st.markdown("<hr style='margin: 8px 0; border-color: #1e2230;' />", unsafe_allow_html=True)
                    
        with col_track2:
            st.subheader("Tambah Kegiatan")
            new_title = st.text_input("Judul Kegiatan", placeholder="Contoh: Belajar APPL...")
            new_cat = st.selectbox("Pilih Kategori", user_cats)
            
            if st.button("Tambah Kegiatan", use_container_width=True):
                if not new_title:
                    st.warning("Judul kegiatan wajib diisi.")
                else:
                    new_task_item = {
                        "email": email,
                        "title": new_title,
                        "category": new_cat,
                        "status": "pending",
                        "exp_rewarded": 50,
                        "date": today_str
                    }
                    db["activities"].append(new_task_item)
                    save_db(db)
                    st.success(f"Kegiatan '{new_title}' berhasil ditambahkan!")
                    st.rerun()
                    
            st.markdown("<br><hr style='border-color: #2e3248;' /><br>", unsafe_allow_html=True)
            
            st.subheader("Kelola Kategori Kustom")
            new_cat_name = st.text_input("Nama Kategori Baru", placeholder="Contoh: Spiritual...")
            new_cat_color = st.color_picker("Pilih Warna Label", "#a855f7")
            
            if st.button("Tambah Kategori", use_container_width=True):
                if not new_cat_name:
                    st.warning("Nama kategori wajib diisi.")
                elif new_cat_name in user_cats:
                    st.error("Kategori sudah terdaftar.")
                else:
                    db["categories"].append({
                        "email": email,
                        "name": new_cat_name,
                        "color": new_cat_color
                    })
                    save_db(db)
                    st.success(f"Kategori '{new_cat_name}' berhasil ditambahkan!")
                    st.rerun()

    # --- 3. KEUANGAN TAB ---
    elif menu == "💰 Manajemen Keuangan":
        st.title("💰 Kontrol Anggaran & Keuangan")
        
        # Ambil total pengeluaran bulan ini
        month_str = datetime.date.today().strftime("%Y-%m")
        user_sinks = [f for f in db["finances"] if f["email"] == email and f["type"] == "Sink" and f["date"].startswith(month_str)]
        user_gains = [f for f in db["finances"] if f["email"] == email and f["type"] == "Gain" and f["date"].startswith(month_str)]
        total_spent = sum([f["amount"] for f in user_sinks])
        total_gain = sum([f["amount"] for f in user_gains])
        remaining_budget = user["budget_limit"] - total_spent + total_gain
        
        # Peringatan Overbudget real-time
        if remaining_budget < 0:
            st.markdown(f"""
            <div class="alert-banner" style="background-color: rgba(239, 68, 68, 0.12); border-color: #ef4444; color: #f87171;">
                ⚠️ <strong>PERINGATAN OVERBUDGET:</strong> Pengeluaranmu bulan ini sudah melampaui limit anggaran! 
                Belanja berlebih sebesar Rp {abs(remaining_budget):,.0f}. Kendalikan keuanganmu!
            </div>
            """, unsafe_allow_html=True)
        elif remaining_budget < 0.1 * user["budget_limit"]:
            st.markdown(f"""
            <div class="alert-banner" style="background-color: rgba(245, 158, 11, 0.12); border-color: #f59e0b; color: #fcd34d;">
                ⚠️ <strong>PERINGATAN LIMIT:</strong> Anggaran belanjamu kritis! Sisa Rp {remaining_budget:,.0f} kurang dari 10% limit.
            </div>
            """, unsafe_allow_html=True)
            
        col_fin1, col_fin2 = st.columns([1, 1])
        
        with col_fin1:
            st.markdown(f"""
            <div class="card" style="background: linear-gradient(135deg, #1f2235, #121420);">
                <div class="card-title">💳 Ringkasan Anggaran Bulanan</div>
                <p style="margin: 0; color: #8f9bb3; font-size: 0.9rem;">Limit Anggaran Bulanan</p>
                <h3 style="margin: 5px 0 15px 0;">Rp {user['budget_limit']:,.0f}</h3>
                <p style="margin: 0; color: #8f9bb3; font-size: 0.9rem;">Total Pengeluaran Bulan Ini (Sink)</p>
                <h3 style="margin: 5px 0 15px 0; color: #ef4444;">Rp {total_spent:,.0f}</h3>
                <hr style="border-color: #2e3248;" />
                <p style="margin: 0; color: #8f9bb3; font-size: 0.9rem;">Sisa Anggaran Belanja</p>
                <h2 style="margin: 5px 0 0 0; color: {'#ef4444' if remaining_budget < 0 else '#10b981'};">Rp {remaining_budget:,.0f}</h2>
            </div>
            """, unsafe_allow_html=True)
            
            st.subheader("Catat Transaksi Baru")
            fin_type = st.radio("Tipe Transaksi", ["Pengeluaran (Sink)", "Pemasukan (Gain)"], horizontal=True)
            fin_amount = st.number_input("Nominal Transaksi (Rupiah)", min_value=500.0, value=25000.0, step=1000.0)
            fin_cat = st.selectbox("Kategori Keuangan", ["Makanan & Minuman", "Transportasi", "Kebutuhan Akademik", "Hobi & Hiburan", "Lain-lain"])
            fin_desc = st.text_input("Keterangan Singkat", placeholder="Contoh: Nasi goreng makan malam...")
            fin_date = st.date_input("Tanggal Transaksi", datetime.date.today())
            
            # Simulasi peringatan instan sebelum simpan
            if fin_type == "Pengeluaran (Sink)" and (remaining_budget - fin_amount) < 0:
                st.warning("⚠️ Perhatian: Menyimpan transaksi ini akan membuat anggaranmu melampaui limit bulanan!")
                
            if st.button("Simpan Catatan Transaksi", use_container_width=True):
                if not fin_desc:
                    st.warning("Keterangan transaksi wajib diisi.")
                else:
                    new_tx = {
                        "email": email,
                        "type": "Sink" if "Pengeluaran" in fin_type else "Gain",
                        "amount": float(fin_amount),
                        "category": fin_cat,
                        "description": fin_desc,
                        "date": fin_date.strftime("%Y-%m-%d")
                    }
                    db["finances"].append(new_tx)
                    
                    # Unlock Badge Hemat jika di akhir bulan sisa > 20% budget (milestone trigger check)
                    if "Hemat" not in [b["badge"] for b in db["user_badges"] if b["email"] == email]:
                        # Cek simulasi lencana
                        adjusted_budget = remaining_budget - fin_amount if "Pengeluaran" in fin_type else remaining_budget + fin_amount
                        if adjusted_budget > 0.2 * user["budget_limit"]:
                            db["user_badges"].append({
                                "email": email,
                                "badge": "Hemat",
                                "unlocked_at": today_str
                            })
                            st.toast("💎 Lencana 'Hemat' Berhasil Terbuka!")
                            
                    save_db(db)
                    st.success("Transaksi keuangan berhasil disimpan!")
                    st.rerun()
                    
        with col_fin2:
            st.subheader("Riwayat Transaksi Keuangan")
            user_tx = [f for f in db["finances"] if f["email"] == email]
            user_tx.sort(key=lambda x: x["date"], reverse=True)
            
            if len(user_tx) == 0:
                st.info("Belum ada riwayat transaksi dicatat.")
            else:
                for tx in user_tx[:8]: # Tampilkan 8 transaksi terbaru
                    tx_color = "#ef4444" if tx["type"] == "Sink" else "#10b981"
                    sign = "-" if tx["type"] == "Sink" else "+"
                    
                    col_t1, col_t2 = st.columns([7, 3])
                    with col_t1:
                        st.markdown(f"**{tx['description']}**<br><span style='color: #8f9bb3; font-size: 0.8rem;'>{tx['date']} | {tx['category']}</span>", unsafe_allow_html=True)
                    with col_t2:
                        st.markdown(f"<h4 style='color: {tx_color}; text-align: right; margin: 0;'>{sign} Rp {tx['amount']:,.0f}</h4>", unsafe_allow_html=True)
                        
                    st.markdown("<hr style='margin: 8px 0; border-color: #1e2230;' />", unsafe_allow_html=True)

    # --- 4. GRAPH & LAPORAN ---
    elif menu == "📊 Grafik & Laporan":
        st.title("📊 Laporan Analitik & Grafik")
        
        tab_lap_act, tab_lap_fin = st.tabs(["📝 Kinerja Konsistensi Aktivitas", "💰 Analisis Alokasi Pengeluaran"])
        
        with tab_lap_act:
            st.subheader("Tren Konsistensi Harian (7 Hari Terakhir)")
            # Konstruksi data mockup konsistensi
            dates = [(datetime.date.today() - datetime.timedelta(days=i)).strftime("%Y-%m-%d") for i in range(6, -1, -1)]
            completion_rates = []
            
            for d in dates:
                tasks_on_day = [t for t in db["activities"] if t["email"] == email and t["date"] == d]
                if len(tasks_on_day) == 0:
                    # Mock defaults untuk melengkapi grafik visual jika user baru
                    completion_rates.append(50.0) # default baseline
                else:
                    done_tasks = [t for t in tasks_on_day if t["status"] == "completed"]
                    rate = (len(done_tasks) / len(tasks_on_day)) * 100
                    completion_rates.append(rate)
                    
            chart_data = pd.DataFrame({
                "Tanggal": [datetime.datetime.strptime(d, "%Y-%m-%d").strftime("%d %b") for d in dates],
                "Konsistensi (%)": completion_rates
            })
            
            # Buat Line Chart premium dengan Altair
            line_chart = alt.Chart(chart_data).mark_line(
                color="#6366f1", strokeWidth=4, point=True
            ).encode(
                x=alt.X("Tanggal", sort=None),
                y=alt.Y("Konsistensi (%)", scale=alt.Scale(domain=[0, 100])),
                tooltip=["Tanggal", "Konsistensi (%)"]
            ).properties(
                height=350
            )
            
            st.altair_chart(line_chart, use_container_width=True)
            st.info("💡 Tips Konsistensi: Selesaikan minimal 1 aktivitas harian untuk mempertahankan Daily Streak-mu!")
            
        with tab_lap_fin:
            st.subheader("Alokasi Pengeluaran Berdasarkan Kategori")
            
            user_sinks = [f for f in db["finances"] if f["email"] == email and f["type"] == "Sink"]
            
            if len(user_sinks) == 0:
                st.info("Belum ada pengeluaran dicatat bulan ini.")
            else:
                df_fin = pd.DataFrame(user_sinks)
                df_grouped = df_fin.groupby("category")["amount"].sum().reset_index()
                
                # Buat Donut Chart premium dengan Altair
                donut_chart = alt.Chart(df_grouped).mark_arc(innerRadius=60).encode(
                    theta=alt.Theta(field="amount", type="quantitative"),
                    color=alt.Color(field="category", type="nominal", scale=alt.Scale(
                        range=["#6366f1", "#10b981", "#f59e0b", "#ec4899", "#a855f7", "#06b6d4"]
                    )),
                    tooltip=[alt.Tooltip("category", title="Kategori"), alt.Tooltip("amount", title="Total Belanja (Rp)", format=",.0f")]
                ).properties(
                    height=350
                )
                
                st.altair_chart(donut_chart, use_container_width=True)
                
                # List Rincian Anggaran Kategori
                st.subheader("Rincian Belanja Per Kategori")
                for _, row in df_grouped.iterrows():
                    col_cat1, col_cat2 = st.columns([7, 3])
                    with col_cat1:
                        st.write(row["category"])
                    with col_cat2:
                        st.markdown(f"<h5 style='text-align: right; margin:0;'>Rp {row['amount']:,.0f}</h5>", unsafe_allow_html=True)
                    st.markdown("<hr style='margin: 5px 0; border-color: #1e2230;' />", unsafe_allow_html=True)

    # --- 5. PAPAN PERINGKAT (LEADERBOARD & GALLERY) ---
    elif menu == "🏆 Leaderboard Global":
        st.title("🏆 Papan Peringkat & Milestone Global")
        
        # Ambil ranking seluruh user di db
        leaderboard_data = []
        for u_email, u_data in db["users"].items():
            leaderboard_data.append({
                "email": u_email,
                "name": u_data["name"],
                "level": u_data["level"],
                "exp": u_data["exp"],
                "score": u_data["level"] * 1000 + u_data["exp"] # total skor kumulatif
            })
            
        df_leader = pd.DataFrame(leaderboard_data)
        df_leader = df_leader.sort_values(by="score", ascending=False).reset_index(drop=True)
        
        # Render visual Podium (Top 3)
        st.subheader("3 Besar Peringkat Global")
        
        # Pastikan ada 3 user untuk podium
        r1_name, r2_name, r3_name = "Rian M.", "Firzal", "Amel"
        r1_lv, r2_lv, r3_lv = 25, 18, 15
        
        if len(df_leader) >= 3:
            r1_name = df_leader.iloc[0]["name"]
            r1_lv = df_leader.iloc[0]["level"]
            
            r2_name = df_leader.iloc[1]["name"]
            r2_lv = df_leader.iloc[1]["level"]
            
            r3_name = df_leader.iloc[2]["name"]
            r3_lv = df_leader.iloc[2]["level"]
            
        col_pod1, col_pod2, col_pod3 = st.columns([1, 1.2, 1])
        
        # Rank 2 (Left Side)
        with col_pod1:
            st.markdown(f"""
            <div style='height: 25px;'></div>
            <div class="podium-card podium-rank2" style="margin: 0 auto;">
                <div class="avatar-circle">{r2_name[:2].upper()}</div>
                <h4 style="margin: 0; color: #64748b;">🥈 #2</h4>
                <p style="margin: 5px 0; font-weight: bold; font-size: 0.95rem;">{r2_name}</p>
                <span class="badge" style="background-color: rgba(100,116,139,0.15); border-color: #64748b; color: #94a3b8;">Lv. {r2_lv}</span>
            </div>
            """, unsafe_allow_html=True)
            
        # Rank 1 (Center - Taller)
        with col_pod2:
            st.markdown(f"""
            <div class="podium-card podium-rank1" style="margin: 0 auto;">
                <div class="avatar-circle avatar-rank1" style="border-color: #f59e0b;">{r1_name[:2].upper()}</div>
                <h3 style="margin: 0; color: #f59e0b;">👑 #1</h3>
                <p style="margin: 8px 0; font-weight: 800; font-size: 1.1rem; font-family: Outfit;">{r1_name}</p>
                <span class="badge" style="background-color: rgba(245,158,11,0.15); border-color: #f59e0b; color: #fbbf24;">Lv. {r1_lv}</span>
            </div>
            """, unsafe_allow_html=True)
            
        # Rank 3 (Right Side)
        with col_pod3:
            st.markdown(f"""
            <div style='height: 45px;'></div>
            <div class="podium-card podium-rank3" style="margin: 0 auto;">
                <div class="avatar-circle">{r3_name[:2].upper()}</div>
                <h4 style="margin: 0; color: #b45309;">🥉 #3</h4>
                <p style="margin: 5px 0; font-weight: bold; font-size: 0.95rem;">{r3_name}</p>
                <span class="badge" style="background-color: rgba(180,83,9,0.15); border-color: #b45309; color: #d97706;">Lv. {r3_lv}</span>
            </div>
            """, unsafe_allow_html=True)
            
        # Peringkat Global Lainnya
        st.subheader("Peringkat Global Selengkapnya")
        
        # Tampilkan tabel rankings lengkap
        table_rows = []
        for idx, row in df_leader.iterrows():
            badge_icon = "👑" if idx == 0 else "🥈" if idx == 1 else "🥉" if idx == 2 else f"  {idx+1}"
            table_rows.append({
                "Rank": badge_icon,
                "Nama Pengguna": row["name"],
                "Level": f"Lv. {row['level']}",
                "EXP": f"{row['exp']} EXP"
            })
            
        st.table(pd.DataFrame(table_rows))

    # --- 6. PENGATURAN TAB ---
    elif menu == "⚙️ Pengaturan Akun":
        st.title("⚙️ Pengaturan Aplikasi & Akun")
        
        col_set1, col_set2 = st.columns([2, 1])
        
        with col_set1:
            st.subheader("Edit Profil Pengguna")
            new_name = st.text_input("Nama Lengkap", user["name"])
            new_limit = st.number_input("Limit Anggaran Bulanan (Rp)", min_value=10000.0, value=float(user["budget_limit"]), step=50000.0)
            
            st.subheader("Konfigurasi Notifikasi Reminder")
            is_reminder_enabled = st.toggle("Aktifkan Pengingat Harian (Reminder)", user["reminders_enabled"])
            new_reminder_time = st.text_input("Waktu Pengingat (WIB)", user["reminder_time"])
            
            if st.button("Simpan Perubahan Pengaturan", use_container_width=True):
                user["name"] = new_name
                user["budget_limit"] = float(new_limit)
                user["reminders_enabled"] = is_reminder_enabled
                user["reminder_time"] = new_reminder_time
                db["users"][email] = user
                save_db(db)
                st.success("Pengaturan akun berhasil disimpan!")
                st.rerun()
                
        with col_set2:
            st.subheader("Informasi Mahasiswa")
            st.markdown("""
            <div class="card">
                <h4>👨‍💻 Tim Pengembang</h4>
                <p style="margin: 5px 0;"><strong>Nama:</strong> Firzal Akbar Ramadhan</p>
                <p style="margin: 5px 0;"><strong>NIM:</strong> 2400018093</p>
                <p style="margin: 5px 0;"><strong>Mata Kuliah:</strong> APPL Kelas C</p>
                <p style="margin: 5px 0;"><strong>Dosen Pengampu:</strong> Drs. Tedy Setiadi, M.T.</p>
            </div>
            """, unsafe_allow_html=True)
            
            st.subheader("Manajemen Database")
            if st.button("⚠️ Reset Database Ke Bawaan", use_container_width=True):
                if os.path.exists(DB_PATH):
                    os.remove(DB_PATH)
                st.session_state.logged_in = False
                st.session_state.user_email = ""
                st.warning("Database telah di-reset! Silakan login ulang.")
                st.rerun()
