import datetime
import math
import requests
import time

# --- CONFIGURATION SETTINGS ---
TELEGRAM_CHAT_ID = "7211477669"

def poisson_probability(k, lamb):
    if lamb <= 0:
        return 0.0
    return (math.exp(-lamb) * (lamb ** k)) / math.factorial(k)

def calculate_advanced_markets(home_attack, home_defense, away_attack, away_defense):
    lambda_home = (home_attack * away_defense * 1.15) / 1.65
    mu_away = (away_attack * home_defense) / (1.65 * 1.15)
    
    p_home = [poisson_probability(i, lambda_home) for i in range(3)]
    p_away = [poisson_probability(i, mu_away) for i in range(3)]
    
    p_0_0 = (p_home[0] * p_away[0]) * (1 - (lambda_home * mu_away * -0.08))
    p_1_0 = (p_home[1] * p_away[0]) * (1 + (mu_away * -0.08))
    p_0_1 = (p_home[0] * p_away[1]) * (1 + (lambda_home * -0.08))
    p_1_1 = (p_home[1] * p_away[1]) * (1 - -0.08)
    
    p_2_0 = p_home[2] * p_away[0]
    p_0_2 = p_home[0] * p_away[2]
    
    total_under_25 = p_0_0 + p_1_0 + p_0_1 + p_1_1 + p_2_0 + p_0_2
    prob_over_25 = max(0.0, min(1.0, 1 - total_under_25))
    fair_odds_over = round(1 / prob_over_25, 2) if prob_over_25 > 0 else 99.0

    prob_btts_no = p_home[0] + p_away[0] - p_0_0
    prob_btts_yes = max(0.0, min(1.0, 1.0 - prob_btts_no))
    fair_odds_btts = round(1 / prob_btts_yes, 2) if prob_btts_yes > 0 else 99.0
    
    return {
        "over_25_prob": round(prob_over_25 * 100, 2),
        "over_25_odds": fair_odds_over,
        "btts_prob": round(prob_btts_yes * 100, 2),
        "btts_odds": fair_odds_btts
    }

def send_telegram_alert(home_team, away_team, league_name, metrics):
    url = "https://api.telegram.org/bot8822256842:AAEYdTp5BH4wQ3czEYsP1XCDGNX3e0_fw_Y/sendMessage"
    
    message = (
        f"🟢 **GREEN LIGHT PICK DETECTED** 🟢\n\n"
        f"🏆 **League:** {league_name}\n"
        f"⚽ **Fixture:** {home_team} vs {away_team}\n\n"
        f"🔥 **MARKET 1: OVER 2.5 GOALS**\n"
        f"📊 Probability: {metrics['over_25_prob']}%\n"
        f"💎 Fair Value Odds: {metrics['over_25_odds']}\n\n"
        f"🤝 **MARKET 2: BOTH TEAMS TO SCORE (BTTS)**\n"
        f"📊 Probability: {metrics['btts_prob']}%\n"
        f"💎 Fair Value Odds: {metrics['btts_odds']}\n\n"
        f"⚠️ *Wager only if active bookmaker values beat the fair lines.*"
    )
    browser_headers = {"User-Agent": "Mozilla/5.0"}
    payload = {"chat_id": TELEGRAM_CHAT_ID, "text": message, "parse_mode": "Markdown"}
    requests.post(url, json=payload, headers=browser_headers, timeout=10)

def run_predictions():
    print("🤖 Processing forced simulation line...")
    
    # Direct high-scoring mock values to bypass off-season network traps completely
    fixtures = [
        {"league": "UEFA Champions League (Live Test)", "home": "Real Madrid", "away": "Manchester City", "h_att": 3.50, "h_def": 1.10, "a_att": 3.20, "a_def": 1.20},
        {"league": "English Premier League (Live Test)", "home": "Arsenal", "away": "Chelsea", "h_att": 3.10, "h_def": 1.00, "a_att": 2.90, "a_def": 1.30}
    ]

    for item in fixtures:
        metrics = calculate_advanced_markets(item['h_att'], item['h_def'], item['a_att'], item['a_def'])
        send_telegram_alert(item['home'], item['away'], item['league'], metrics)
        print(f"✅ ALERT FORCED TO TELEGRAM: {item['home']} vs {item['away']}")
        time.sleep(1)

if __name__ == "__main__":
    run_predictions()
    
