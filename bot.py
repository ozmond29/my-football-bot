import datetime
import math
import requests
import time
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# --- CONFIGURATION SETTINGS ---
TELEGRAM_CHAT_ID = "7211477669"

def poisson_probability(k, lamb):
    if lamb <= 0: return 0.0
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
    except: return 0

def send_combo_accumulator_report(ft_picks, fh_picks, target_date):
    url = "https://api.telegram.org/bot8822256842:AAEYdTp5BH4wQ3czEYsP1XCDGNX3e0_fw_Y/sendMessage"
    
    message = f"📊 **DUAL-MARKET COMBO MASTER SHEET** 📊\n🗓️ **Date:** {target_date}\n"
    message += "=============================\n\n"
    
    message += "🔥 **SECTION A: FULL-TIME OVER 1.5 GOALS**\n\n"
    for idx, game in enumerate(ft_picks, 1):
        message += f"{idx}. 🏆 *{game['league']}*\n   ⚽ `{game['home']} vs {game['away']}`\n   📈 **FT Prob:** {game['prob']}% | **Fair:** {game['odds']}\n\n"
        
    message += "=============================\n\n"
    message += "⏱️ **SECTION B: FIRST-HALF OVER 0.5 GOALS**\n\n"
    for idx, game in enumerate(fh_picks, 1):
        message += f"{idx}. 🏆 *{game['league']}*\n   ⚽ `{game['home']} vs {game['away']}`\n   ⚡ Window: `{game['peak_window']}` | **FH Prob:** {game['prob']}%\n\n"
        
    message += "=============================\n⚠️ *Wager responsibly as system singles or split cards.*"
    
    browser_headers = {"User-Agent": "Mozilla/5.0"}
    payload = {"chat_id": TELEGRAM_CHAT_ID, "text": message, "parse_mode": "Markdown"}
    try:
        requests.post(url, json=payload, headers=browser_headers, timeout=15)
        print("📡 Combo report sent successfully!")
    except Exception as e:
        print(f"❌ Error: {e}")

def get_global_database():
    return [
        {"league": "Iceland Urvalsdeild", "home": "Vikingur", "away": "Valur", "last_h2h": "2-1", "last_h2h_fh_goal": True, "peak_window": "1'-15'", "fh_freq_pct": 85, "h_att": 2.9, "h_def": 1.4, "a_att": 2.4, "a_def": 1.8},
        {"league": "Norway Eliteserien", "home": "Bodo/Glimt", "away": "Molde", "last_h2h": "3-2", "last_h2h_fh_goal": True, "peak_window": "31'-45'", "fh_freq_pct": 90, "h_att": 2.8, "h_def": 1.2, "a_att": 2.2, "a_def": 1.7},
        {"league": "Sweden Allsvenskan", "home": "Malmo FF", "away": "Sirius", "last_h2h": "3-0", "last_h2h_fh_goal": True, "peak_window": "1'-15'", "fh_freq_pct": 80, "h_att": 2.7, "h_def": 1.0, "a_att": 1.9, "a_def": 2.1},
        {"league": "USA MLS", "home": "Inter Miami", "away": "Orlando City", "last_h2h": "1-3", "last_h2h_fh_goal": True, "peak_window": "16'-30'", "fh_freq_pct": 88, "h_att": 2.65, "h_def": 1.5, "a_att": 1.85, "a_def": 1.95},
        {"league": "Singapore Premier", "home": "Albirex Niigata", "away": "Lion City", "last_h2h": "4-2", "last_h2h_fh_goal": True, "peak_window": "31'-45'", "fh_freq_pct": 95, "h_att": 3.4, "h_def": 1.9, "a_att": 3.1, "a_def": 1.6},
        {"league": "Estonia Meistriliiga", "home": "Levadia", "away": "Narva", "last_h2h": "3-1", "last_h2h_fh_goal": True, "peak_window": "1'-15'", "fh_freq_pct": 78, "h_att": 2.85, "h_def": 0.6, "a_att": 1.2, "a_def": 2.7},
        {"league": "Norway 1. Divisjon", "home": "Lyn Oslo", "away": "Stabaek", "last_h2h": "2-2", "last_h2h_fh_goal": True, "peak_window": "31'-45'", "fh_freq_pct": 82, "h_att": 2.2, "h_def": 1.4, "a_att": 2.05, "a_def": 1.85},
        {"league": "Peru Liga 1", "home": "Sporting Cristal", "away": "Melgar", "last_h2h": "1-2", "last_h2h_fh_goal": True, "peak_window": "16'-30'", "fh_freq_pct": 80, "h_att": 2.7, "h_def": 1.2, "a_att": 1.8, "a_def": 1.3},
        {"league": "Australia NPL", "home": "Gold Coast", "away": "Peninsula", "last_h2h": "4-1", "last_h2h_fh_goal": True, "peak_window": "1'-15'", "fh_freq_pct": 92, "h_att": 2.95, "h_def": 1.25, "a_att": 2.4, "a_def": 1.9},
        {"league": "Brazil Serie A", "home": "Flamengo", "away": "Botafogo", "last_h2h": "2-1", "last_h2h_fh_goal": True, "peak_window": "31'-45'", "fh_freq_pct": 76, "h_att": 2.3, "h_def": 1.1, "a_att": 1.8, "a_def": 1.4},
        {"league": "Japan J1 League", "home": "Yokohama", "away": "Urawa Reds", "last_h2h": "3-1", "last_h2h_fh_goal": True, "peak_window": "1'-15'", "fh_freq_pct": 84, "h_att": 2.5, "h_def": 1.6, "a_att": 1.7, "a_def": 1.5},
        {"league": "USA USL", "home": "Tampa Bay", "away": "Louisville", "last_h2h": "2-3", "last_h2h_fh_goal": True, "peak_window": "31'-45'", "fh_freq_pct": 91, "h_att": 2.4, "h_def": 1.4, "a_att": 2.5, "a_def": 1.3}
    ]

def run_dual_market_engine():
    target_date = "2026-07-10"
    fixtures = get_global_database()
    ft_candidates, fh_candidates = [], []

    print(f"🤖 Processing distributions across {len(fixtures)} profiles...")

    for item in fixtures:
        total_h2h_goals = parse_h2h_goals(item['last_h2h'])
        if total_h2h_goals >= 3:
            ft_prob, ft_odds = calculate_over_15_prob(item['h_att'], item['h_def'], item['a_att'], item['a_def'])
            ft_candidates.append({"league": item['league'], "home": item['home'], "away": item['away'], "prob": ft_prob, "odds": ft_odds})
            
        if item['last_h2h_fh_goal'] and item['fh_freq_pct'] >= 75:
            fh_prob, fh_odds = calculate_fh_over05_prob(item['h_att'], item['h_def'], item['a_att'], item['a_def'])
            fh_candidates.append({"league": item['league'], "home": item['home'], "away": item['away'], "peak_window": item['peak_window'], "prob": fh_prob, "odds": fh_odds})

    ft_candidates.sort(key=lambda x: x['prob'], reverse=True)
    fh_candidates.sort(key=lambda x: x['prob'], reverse=True)

    send_combo_accumulator_report(ft_candidates[:10], fh_candidates[:10], target_date)
    print("🏁 Complete! Dispatched combo packs cleanly.")

if __name__ == "__main__":
    run_dual_market_engine()
            
