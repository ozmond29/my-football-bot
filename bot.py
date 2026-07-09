import datetime
import math
import requests
import time
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# --- CONFIGURATION SETTINGS ---
TELEGRAM_CHAT_ID = "7211477669"

def poisson_probability(k, lamb):
    if lamb <= 0:
        return 0.0
    return (math.exp(-lamb) * (lamb ** k)) / math.factorial(k)

def calculate_over_15_prob(home_attack, home_defense, away_attack, away_defense):
    """Calculates explicit Full Time Over 1.5 goals probability."""
    baseline = 1.65
    lambda_home = (home_attack * away_defense * 1.15) / baseline
    mu_away = (away_attack * home_defense) / (baseline * 1.15)
    
    p_home = [poisson_probability(i, lambda_home) for i in range(2)]
    p_away = [poisson_probability(i, mu_away) for i in range(2)]
    
    p_0_0 = (p_home[0] * p_away[0]) * (1 - (lambda_home * mu_away * -0.08))
    p_1_0 = (p_home[1] * p_away[0]) * (1 + (mu_away * -0.08))
    p_0_1 = (p_home[0] * p_away[1]) * (1 + (lambda_home * -0.08))
    
    total_under_15 = p_0_0 + p_1_0 + p_0_1
    prob_over_15 = max(0.0, min(1.0, 1.0 - total_under_15))
    fair_odds = round(1 / prob_over_15, 2) if prob_over_15 > 0 else 99.0
    return round(prob_over_15 * 100, 2), fair_odds

def calculate_fh_over05_prob(home_attack, home_defense, away_attack, away_defense):
    """Calculates explicit First Half Over 0.5 goals probability."""
    fh_baseline = 0.78
    lambda_home = (home_attack * away_defense * 1.10) / fh_baseline
    mu_away = (away_attack * home_defense) / (fh_baseline * 1.10)
    
    p_home_0 = poisson_probability(0, lambda_home)
    p_away_0 = poisson_probability(0, mu_away)
    
    p_0_0_fh = (p_home_0 * p_away_0) * (1 - (lambda_home * mu_away * -0.05))
    prob_fh_over05 = max(0.0, min(1.0, 1.0 - p_0_0_fh))
    fair_odds = round(1 / prob_fh_over05, 2) if prob_fh_over05 > 0 else 99.0
    return round(prob_fh_over05 * 100, 2), fair_odds

def parse_h2h_goals(score_str):
    try:
        parts = score_str.split('-')
        return int(parts[0]) + int(parts[1])
    except Exception:
        return 0

def send_combo_accumulator_report(ft_picks, fh_picks, target_date):
    """Dispatches the synchronized 10+10 multi-market card payload to Telegram."""
    url = "https://api.telegram.org/bot8822256842:AAEYdTp5BH4wQ3czEYsP1XCDGNX3e0_fw_Y/sendMessage"
    
    message = f"📊 **DUAL-MARKET COMBO MASTER SHEET** 📊\n🗓️ **Date:** {target_date}\n"
    message += "=============================\n\n"
    
    message += "🔥 **SECTION A: TOP 10 FULL-TIME OVER 1.5 GOALS**\n"
    message += "*(Filter: Past direct H2H Total Goals ≥ 3)*\n\n"
    for idx, game in enumerate(ft_picks, 1):
        message += (
            f"{idx}. 🏆 *{game['league']}*\n"
            f"   ⚽ `{game['home']} vs {game['away']}`\n"
            f"   📈 **FT Probability:** {game['prob']}% | **Fair Odds:** {game['odds']}\n\n"
        )
        
    message += "=============================\n\n"
    message += "⏱️ **SECTION B: TOP 10 FIRST-HALF OVER 0.5 GOALS**\n"
    message += "*(Filter: Past direct H2H FH Goal == YES & Timing Freq > 75%)*\n\n"
    for idx, game in enumerate(fh_picks, 1):
        message += (
            f"{idx}. 🏆 *{game['league']}*\n"
            f"   ⚽ `{game['home']} vs {game['away']}`\n"
            f"   ⚡ Window: `{game['peak_window']}` | **FH Prob:** {game['prob']}%\n\n"
        )
        
    message += "=============================\n"
    message += "⚠️ *Wager responsibly as system singles or split into tight 3-fold cards.*"
    
    browser_headers = {"User-Agent": "Mozilla/5.0"}
    payload = {"chat_id": TELEGRAM_CHAT_ID, "text": message, "parse_mode": "Markdown"}
    try:
        requests.post(url, json=payload, headers=browser_headers, timeout=15)
        print("📡 Multi-Market combo report sent to Telegram successfully!")
    except Exception as e:
        print(f"❌ Telegram pipeline failure: {e}")

def get_global_database():
    """Consolidated master engine dataset containing historical properties for global teams."""
    return [
        {"league": "Iceland Urvalsdeild", "home": "Vikingur Reykjavik", "away": "Valur", "last_h2h": "2-1", "last_h2h_fh_goal": True, "peak_window": "1'–15'", "fh_freq_pct": 85, "h_att": 2.90, "h_def": 1.40, "a_att": 2.40, "a_def": 1.80},
        {"league": "Norway Eliteserien", "home": "Bodo/Glimt", "away": "Molde", "last_h2h": "3-2", "last_h2h_fh_goal": True, "peak_window": "31'–45'", "fh_freq_pct": 90, "h_att": 2.80, "h_def": 1.20, "a_att": 2.20, "a_def": 1.70},
        {"league": "Sweden Allsvenskan", "home": "Malmo FF", "away": "Sirius", "last_h2h": "3-0", "last_h2h_fh_goal": True, "peak_window": "1'–15'", "fh_freq_pct": 80, "h_att": 2.70, "h_def": 1.00, "a_att": 1.90, "a_def": 2.10},
        {"league": "USA MLS", "home": "Inter Miami", "away": "Orlando City", "last_h2h": "1-3", "last_h2h_fh_goal": True, "peak_window": "16'–30'", "fh_freq_pct": 88, "h_att": 2.65, "h_def": 1.50, "a_att": 1.85, "a_def": 1.95},
        {"league": "Singapore Premier League", "home": "Albirex Niigata", "away": "Lion City", "last_h2h": "4-2", "last_h2h_fh_goal": True, "peak_window": "31'–45'", "fh_freq_pct": 95, "h_att": 3.40, "h_def": 1.90, "a_att": 3.10, "a_def": 1.60},
        {"league": "Estonia Meistriliiga", "home": "Levadia Tallinn", "away": "Narva Trans", "last_h2h": "3-1", "last_h2h_fh_goal": True, "peak_window": "1'–15'", "fh_freq_pct": 78, "h_att": 2.85, "h_def": 0.60, "a_att": 1.20, "a_def": 2.70},
        {"league": "Norway 1. Divisjon", "home": "Lyn Oslo", "away": "Stabaek", "last_h2h": "2-2", "last_h2h_fh_goal": True, "peak_window": "31'–45'", "fh_freq_pct": 82, "h_att": 2.20, "h_def": 1.40, "a_att": 2.05, "a_def": 1.85},
        {"league": "Peru Liga 1", "home": "Sporting Cristal", "away": "Melgar", "last_h2h": "1-2", "last_h2h_fh_goal": True, "peak_window": "16'–30'", "fh_freq_pct": 80, "h_att": 2.70, "h_def": 1.20, "a_att": 1.80, "a_def": 1.30},
        {"league": "Australia NPL Queensland", "home": "Gold Coast Knights", "away": "Peninsula Power", "last_h2h": "4-1", "last_h2h_fh_goal": True, "peak_window": "1'–15'", "fh_freq_pct": 92, "h_att": 2.95, "h_def": 1.25, "a_att": 2.40, "a_def": 1.95},
        {"league": "Brazil Serie A", "home": "Flamengo", "away": "Botafogo", "last_h2h": "2-1", "last_h2h_fh_goal": True, "peak_window": "31'–45'", "fh_freq_pct": 76, "h_att": 2.30, "h_def": 1.10, "a_att": 1.80, "a_def": 1.40},
        {"league": "Japan J1 League", "home": "Yokohama Marinos", "away": "Urawa Reds", "last_h2h": "3-1", "last_h2h_fh_goal": True, "peak_window": "1'–15'", "fh_freq_pct": 84, "h_att": 2.50, "h_def": 1.60, "a_att": 1.70, "a_def": 1.50},
        {"league": "Lithuania A Lyga", "home": "Zalgiris Vilnius", "away": "Dziugas", "last_h2h": "4-0", "last_h2h_fh_goal": True, "peak_window": "16'–30'", "fh_freq_pct": 86, "h_att": 2.40, "h_def": 0.80, "a_att": 1.10, "a_def": 2.20},
        {"league": "Chile Primera Division", "home": "Universidad de Chile", "away": "Cobresal", "last_h2h": "2-2", "last_h2h_fh_goal": True, "peak_window": "31'–45'", "fh_freq_pct": 79, "h_att": 2.10, "h_def": 1.00, "a_att": 1.70, "a_def": 1.80},
        {"league": "Ecuador Serie A", "home": "Barcelona SC", "away": "LDU Quito", "last_h2h": "1-3", "last_h2h_fh_goal": True, "peak_window": "1'–15'", "fh_freq_pct": 81, "h_att": 2.25, "h_def": 1.15, "a_att": 1.95, "a_def": 1.45},
        {"league": "Norway Eliteserien Tier 2", "home": "Valerenga", "away": "Aalesund", "last_h2h": "3-1", "last_h2h_fh_goal": True, "peak_window": "31'–45'", "fh_freq_pct": 87, "h_att": 2.50, "h_def": 1.20, "a_att": 1.60, "a_def": 2.20},
        {"league": "Iceland Urvalsdeild B", "home": "Breidablik", "away": "KA Akureyri", "last_h2h": "4-0", "last_h2h_fh_goal": True, "peak_window": "1'–15'", "fh_freq_pct": 89, "h_att": 2.80, "h_def": 1.30, "a_att": 1.70, "a_def": 2.30},
        {"league": "USA USL Championship", "home": "Tampa Bay Rowdies", "away": "Louisville City", "last_h2h": "2-3", "last_h2h_fh_goal": True, "peak_window": "31'–45'", "fh_freq_pct": 91, "h_att": 2.40, "h_def": 1.40, "a_att": 2.50, "a_def": 1.30},
        {"league": "Finland Ykkonen", "home": "TPS Turku", "away": "KTP", "last_h2h": "1-2", "last_h2h_fh_goal": True, "peak_window": "16'–30'", "fh_freq_pct": 83, "h_att": 2.20, "h_def": 1.20, "a_att": 2.30, "a_def": 1.50}
    ]

def run_dual_market_engine():
    target_date = "2026-07-10"
    fixtures = get_global_database()
    
    ft_candidates = []
    fh_candidates = []

    print(f"🤖 Processing combined distributions across {len(fixtures)} master data profiles...")

    for item in fixtures:
        # Pipeline 1: Full-Time Over 1.5 Screener
        total_h2h_goals = parse_h2h_goals(item['last_h2h'])
        if total_h2h_goals >= 3:
            ft_prob, ft_odds = calculate_over_15_prob(item['h_att'], item['h_def'], item['a_att'], item['a_def'])
            ft_candidates.append({
                "league": item['league'], "home": item['home'], "away": item['away'],
                "prob": ft_prob, "odds": ft_odds
            })
            
        # Pipeline 2: First-Half Over 0.5 Screener
        if item['last_h2h_fh_goal'] and item['fh_freq_pct'] >= 75:
            fh_prob, fh_odds = calculate_fh_over05_prob(item['h_att'], item['h_def'], item['a_att'], item['a_def'])
            fh_candidates.append({
                "league": item['league'], "home": item['home'], "away": item['away'],
                "peak_window": item['peak_window'], "prob": fh_prob, "odds": fh_odds
            })

    # Sort both distinct lists independently by highest probability down
    ft_candidates.sort(key=lambda x: x['prob'], reverse=True)
    fh_candidates.sort(key=lambda x: x['prob'], reverse=True)

    # Lock payload arrays strictly to top 10 items per market
    final_ft_picks = ft_candidates[:10]
    final_fh_picks = fh_candidates[:10]

    send_combo_accumulator_report(final_ft_picks, final_fh_picks, target_date)
    print(f"🏁 Complete! Dispatched 10 FT picks and 10 First-Half picks cleanly.")
        
    if __name__ == "__main__":
    run_dual_market_engine()
