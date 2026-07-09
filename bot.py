import datetime, math, requests, time, urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

TELEGRAM_CHAT_ID = "7211477669"

def poisson_probability(k, lamb):
    if lamb <= 0: return 0.0
    return (math.exp(-lamb) * (lamb ** k)) / math.factorial(k)

def calculate_over_15_prob(h_att, h_def, a_att, a_def):
    base = 1.65
    l_h = (h_att * a_def * 1.15) / base
    m_a = (a_att * h_def) / (base * 1.15)
    p_h = [poisson_probability(i, l_h) for i in range(2)]
    p_a = [poisson_probability(i, m_a) for i in range(2)]
    p_0_0 = (p_h[0] * p_a[0]) * (1 - (l_h * m_a * -0.08))
    p_1_0 = (p_h[1] * p_a[0]) * (1 + (m_a * -0.08))
    p_0_1 = (p_h[0] * p_a[1]) * (1 + (l_h * -0.08))
    p_over = max(0.0, min(1.0, 1.0 - (p_0_0 + p_1_0 + p_0_1)))
    return round(p_over * 100, 2), round(1 / p_over, 2) if p_over > 0 else 99.0

def calculate_fh_over05_prob(h_att, h_def, a_att, a_def):
    fh_base = 0.78
    l_h = (h_att * a_def * 1.10) / fh_base
    m_a = (a_att * h_def) / (fh_base * 1.10)
    p_0_0 = (poisson_probability(0, l_h) * poisson_probability(0, m_a)) * (1 - (l_h * m_a * -0.05))
    p_over = max(0.0, min(1.0, 1.0 - p_0_0))
    return round(p_over * 100, 2), round(1 / p_over, 2) if p_over > 0 else 99.0

def parse_h2h_goals(score_str):
    try:
        parts = score_str.split('-')
        return int(parts[0]) + int(parts[1])
    except: return 0

def send_combo_accumulator_report(ft_picks, fh_picks, target_date):
    url = "https://api.telegram.org/bot8822256842:AAEYdTp5BH4wQ3czEYsP1XCDGNX3e0_fw_Y/sendMessage"
    msg = f"📊 **DUAL-MARKET COMBO MASTER SHEET** 📊\n🗓️ **Date:** {target_date}\n"
    msg += f"🎯 **Total Selections:** {len(ft_picks) + len(fh_picks)} Unique Matches\n=============================\n\n"
    msg += "🔥 **SECTION A: 10 FULL-TIME OVER 1.5 GOALS**\n\n"
    for i, g in enumerate(ft_picks, 1):
        msg += f"{i}. 🏆 *{g['league']}*\n   ⚽ `{g['home']} vs {g['away']}`\n   📈 **FT Prob:** {g['prob']}% | **Fair:** {g['odds']}\n\n"
    msg += "=============================\n\n"
    msg += "⏱️ **SECTION B: 10 FIRST-HALF OVER 0.5 GOALS**\n\n"
    for i, g in enumerate(fh_picks, 1):
        msg += f"{i}. 🏆 *{g['league']}*\n   ⚽ `{g['home']} vs {g['away']}`\n   ⚡ Window: `{g['peak_window']}` | **FH Prob:** {g['prob']}%\n\n"
    msg += "=============================\n⚠️ *Wager responsibly. Every fixture across both markets is 100% unique.*"
    payload = {"chat_id": TELEGRAM_CHAT_ID, "text": msg, "parse_mode": "Markdown"}
    try: requests.post(url, json=payload, headers={"User-Agent": "Mozilla/5.0"}, timeout=15)
    except Exception as e: print(f"❌ Error: {e}")

def get_global_database():
    return [
        {"league": "Iceland Urvals", "home": "Vikingur", "away": "Valur", "last_h2h": "2-1", "last_h2h_fh_goal": True, "peak_window": "1'-15'", "fh_freq_pct": 85, "h_att": 2.9, "h_def": 1.4, "a_att": 2.4, "a_def": 1.8},
        {"league": "Norway Elite", "home": "Bodo/Glimt", "away": "Molde", "last_h2h": "3-2", "last_h2h_fh_goal": True, "peak_window": "31'-45'", "fh_freq_pct": 90, "h_att": 2.8, "h_def": 1.2, "a_att": 2.2, "a_def": 1.7},
        {"league": "Sweden Allsv", "home": "Malmo FF", "away": "Sirius", "last_h2h": "3-0", "last_h2h_fh_goal": True, "peak_window": "1'-15'", "fh_freq_pct": 80, "h_att": 2.7, "h_def": 1.0, "a_att": 1.9, "a_def": 2.1},
        {"league": "USA MLS", "home": "Inter Miami", "away": "Orlando City", "last_h2h": "1-3", "last_h2h_fh_goal": True, "peak_window": "16'-30'", "fh_freq_pct": 88, "h_att": 2.65, "h_def": 1.5, "a_att": 1.85, "a_def": 1.95},
        {"league": "Singapore Premier", "home": "Albirex", "away": "Lion City", "last_h2h": "4-2", "last_h2h_fh_goal": True, "peak_window": "31'-45'", "fh_freq_pct": 95, "h_att": 3.4, "h_def": 1.9, "a_att": 3.1, "a_def": 1.6},
        {"league": "Estonia Meistr", "home": "Levadia", "away": "Narva", "last_h2h": "3-1", "last_h2h_fh_goal": True, "peak_window": "1'-15'", "fh_freq_pct": 78, "h_att": 2.85, "h_def": 0.6, "a_att": 1.2, "a_def": 2.7},
        {"league": "Norway 1. Div", "home": "Lyn Oslo", "away": "Stabaek", "last_h2h": "2-2", "last_h2h_fh_goal": True, "peak_window": "31'-45'", "fh_freq_pct": 82, "h_att": 2.2, "h_def": 1.4, "a_att": 2.05, "a_def": 1.85},
        {"league": "Peru Liga 1", "home": "Sporting C.", "away": "Melgar", "last_h2h": "1-2", "last_h2h_fh_goal": True, "peak_window": "16'-30'", "fh_freq_pct": 80, "h_att": 2.7, "h_def": 1.2, "a_att": 1.8, "a_def": 1.3},
        {"league": "Australia NPL", "home": "Gold Coast", "away": "Peninsula", "last_h2h": "4-1", "last_h2h_fh_goal": True, "peak_window": "1'-15'", "fh_freq_pct": 92, "h_att": 2.95, "h_def": 1.25, "a_att": 2.4, "a_def": 1.9},
        {"league": "Brazil Serie A", "home": "Flamengo", "away": "Botafogo", "last_h2h": "2-1", "last_h2h_fh_goal": True, "peak_window": "31'-45'", "fh_freq_pct": 76, "h_att": 2.3, "h_def": 1.1, "a_att": 1.8, "a_def": 1.4},
        {"league": "Japan J1", "home": "Yokohama", "away": "Urawa Reds", "last_h2h": "3-1", "last_h2h_fh_goal": True, "peak_window": "1'-15'", "fh_freq_pct": 84, "h_att": 2.5, "h_def": 1.6, "a_att": 1.7, "a_def": 1.5},
        {"league": "USA USL", "home": "Tampa Bay", "away": "Louisville", "last_h2h": "2-3", "last_h2h_fh_goal": True, "peak_window": "31'-45'", "fh_freq_pct": 91, "h_att": 2.4, "h_def": 1.4, "a_att": 2.5, "a_def": 1.3},
        {"league": "Finland Ykk", "home": "TPS Turku", "away": "KTP", "last_h2h": "3-1", "last_h2h_fh_goal": True, "peak_window": "16'-30'", "fh_freq_pct": 83, "h_att": 2.2, "h_def": 1.2, "a_att": 2.3, "a_def": 1.5},
        {"league": "Iceland Div 2", "home": "Fylkir", "away": "Fram", "last_h2h": "3-2", "last_h2h_fh_goal": True, "peak_window": "31'-45'", "fh_freq_pct": 87, "h_att": 2.6, "h_def": 1.5, "a_att": 2.1, "a_def": 1.9},
        {"league": "Ireland 1st Div", "home": "Cork City", "away": "Wexford", "last_h2h": "4-1", "last_h2h_fh_goal": True, "peak_window": "1'-15'", "fh_freq_pct": 81, "h_att": 2.5, "h_def": 0.8, "a_att": 1.7, "a_def": 2.2},
        {"league": "Austria 2. Liga", "home": "Liefering", "away": "Amstetten", "last_h2h": "3-1", "last_h2h_fh_goal": True, "peak_window": "16'-30'", "fh_freq_pct": 89, "h_att": 2.7, "h_def": 1.4, "a_att": 1.9, "a_def": 2.1},
        {"league": "Swiss Challeng", "home": "Thun", "away": "Aarau", "last_h2h": "4-2", "last_h2h_fh_goal": True, "peak_window": "31'-45'", "fh_freq_pct": 92, "h_att": 2.8, "h_def": 1.3, "a_att": 2.0, "a_def": 2.1},
        {"league": "Denmark 1st D", "home": "Hobro", "away": "Koge", "last_h2h": "3-0", "last_h2h_fh_goal": True, "peak_window": "1'-15'", "fh_freq_pct": 79, "h_att": 2.4, "h_def": 1.1, "a_att": 1.6, "a_def": 2.3},
        {"league": "Holland Eerst", "home": "Cambuur", "away": "Eindhoven", "last_h2h": "3-2", "last_h2h_fh_goal": True, "peak_window": "16'-30'", "fh_freq_pct": 86, "h_att": 2.5, "h_def": 1.3, "a_att": 2.1, "a_def": 1.8},
        {"league": "Scotland Champ", "home": "Partick T.", "away": "Raith Rov", "last_h2h": "2-2", "last_h2h_fh_goal": True, "peak_window": "31'-45'", "fh_freq_pct": 82, "h_att": 2.1, "h_def": 1.2, "a_att": 1.9, "a_def": 1.6},
        {"league": "Wales Premier", "home": "New Saints", "away": "Bala Town", "last_h2h": "4-1", "last_h2h_fh_goal": True, "peak_window": "1'-15'", "fh_freq_pct": 94, "h_att": 3.3, "h_def": 0.8, "a_att": 1.8, "a_def": 2.4},
        {"league": "N. Ireland", "home": "Linfield", "away": "Larne", "last_h2h": "3-1", "last_h2h_fh_goal": True, "peak_window": "16'-30'", "fh_freq_pct": 80, "h_att": 2.4, "h_def": 1.0, "a_att": 1.8, "a_def": 1.5}
    ]

def run_dual_market_engine():
    target_date = "2026-07-10"
    fixtures = get_global_database()
    ft_pool, fh_pool = [], []
    for item in fixtures:
        if parse_h2h_goals(item['last_h2h']) >= 3:
            ft_prob, ft_odds = calculate_over_15_prob(item['h_att'], item['h_def'], item['a_att'], item['a_def'])
            ft_pool.append({"league": item['league'], "home": item['home'], "away": item['away'], "prob": ft_prob, "odds": ft_odds})
        if item['last_h2h_fh_goal'] and item['fh_freq_pct'] >= 75:
            fh_prob, fh_odds = calculate_fh_over05_prob(item['h_att'], item['h_def'], item['a_att'], item['a_def'])
            fh_pool.append({"league": item['league'], "home": item['home'], "away": item['away'], "peak_window": item['peak_window'], "prob": fh_prob, "odds": fh_odds})
    ft_pool.sort(key=lambda x: x['prob'], reverse=True)
    fh_pool.sort(key=lambda x: x['prob'], reverse=True)
    selected_ft = ft_pool[:10]
    assigned_keys = set(f"{g['home']} vs {g['away']}" for g in selected_ft)
    selected_fh = []
    for g in fh_pool:
        if f"{g['home']} vs {g['away']}" in assigned_keys: continue
        selected_fh.append(g)
        if len(selected_fh) == 10: break
    send_combo_accumulator_report(selected_ft, selected_fh, target_date)
    print("🏁 Execution complete! Dispatched 20 completely unique selections.")

if __name__ == "__main__":
    run_dual_market_engine()
    
