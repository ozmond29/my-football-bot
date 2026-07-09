import datetime
import math
import requests
import time
import urllib3

# Suppress local network SSL warning logs
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# --- CONFIGURATION SETTINGS ---
TELEGRAM_CHAT_ID = "7211477669"
API_FOOTBALL_KEY = "cd8673caca874737a62c4c0b54356c7a"

# --- GLOBAL MODEL CALIBRATIONS ---
LEAGUE_BASELINE_GOALS = 1.65 
HOME_ADV_MULTIPLIER = 1.15
DIXON_COLES_RHO = -0.08
PROBABILITY_THRESHOLD = 10.0 

def poisson_probability(k, lamb):
    if lamb <= 0:
        return 0.0
    return (math.exp(-lamb) * (lamb ** k)) / math.factorial(k)

def calculate_advanced_markets(home_attack, home_defense, away_attack, away_defense):
    lambda_home = (home_attack * away_defense * HOME_ADV_MULTIPLIER) / LEAGUE_BASELINE_GOALS
    mu_away = (away_attack * home_defense) / (LEAGUE_BASELINE_GOALS * HOME_ADV_MULTIPLIER)
    
    p_home = [poisson_probability(i, lambda_home) for i in range(3)]
    p_away = [poisson_probability(i, mu_away) for i in range(3)]
    
    p_0_0 = (p_home[0] * p_away[0]) * (1 - (lambda_home * mu_away * DIXON_COLES_RHO))
    p_1_0 = (p_home[1] * p_away[0]) * (1 + (mu_away * DIXON_COLES_RHO))
    p_0_1 = (p_home[0] * p_away[1]) * (1 + (lambda_home * DIXON_COLES_RHO))
    p_1_1 = (p_home[1] * p_away[1]) * (1 - DIXON_COLES_RHO)
    
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

def calculate_kelly_stake(model_prob, bookie_odds):
    p = model_prob / 100.0
    q = 1.0 - p
    b = bookie_odds - 1.0
    if b <= 0: return 0.0
    raw_kelly = (p * b - q) / b
    return round(max(0.0, (raw_kelly / 4.0) * 100), 2)

def send_telegram_alert(home_team, away_team, league_name, metrics):
    url = "https://api.telegram.org/bot8822256842:AAEYdTp5BH4wQ3czEYsP1XCDGNX3e0_fw_Y/sendMessage"
    assumed_over_odds = 1.45
    assumed_btts_odds = 1.65
    
    stake_over = calculate_kelly_stake(metrics["over_25_prob"], assumed_over_odds)
    stake_btts = calculate_kelly_stake(metrics["btts_prob"], assumed_btts_odds)
    
    message = (
        f"🟢 **GREEN LIGHT PICK DETECTED** 🟢\n\n"
        f"🏆 **League:** {league_name}\n"
        f"⚽ **Fixture:** {home_team} vs {away_team}\n\n"
        f"🔥 **MARKET 1: OVER 2.5 GOALS**\n"
        f"📊 Probability: {metrics['over_25_prob']}%\n"
        f"💎 Fair Value Odds: {metrics['over_25_odds']}\n"
        f"📏 Suggested Stake: {stake_over}% bankroll\n\n"
        f"🤝 **MARKET 2: BOTH TEAMS TO SCORE (BTTS)**\n"
        f"📊 Probability: {metrics['btts_prob']}%\n"
        f"💎 Fair Value Odds: {metrics['btts_odds']}\n"
        f"📏 Suggested Stake: {stake_btts}% bankroll\n\n"
        f"⚠️ *Wager only if active bookmaker values beat the fair lines.*"
    )
    browser_headers = {"User-Agent": "Mozilla/5.0"}
    payload = {"chat_id": TELEGRAM_CHAT_ID, "text": message, "parse_mode": "Markdown"}
    try:
        requests.post(url, json=payload, headers=browser_headers, timeout=10)
    except Exception as e:
        print(f"❌ Telegram pipeline failure: {e}")

def get_live_fixtures():
    """Queries free tier leagues explicitly. Fallbacks are permanently removed."""
    free_competition_codes = ["PL", "PD", "BL1", "SA", "FL1", "DED", "PPL", "CL"]
    headers = {'X-Auth-Token': API_FOOTBALL_KEY}
    formatted_list = []
    
    print("⏳ Scanning active matches...")
    
    for code in free_competition_codes:
        url = f"https://football-data.org{code}/matches"
        try:
            response = requests.get(url, headers=headers, timeout=10, verify=False)
            if response.status_code != 200:
                continue
                
            data = response.json()
            raw_matches = data.get('matches', [])
            today_str = datetime.datetime.now().strftime('%Y-%m-%d')
            
            for match in raw_matches:
                match_date = match.get('utcDate', '')[:10]
                if match_date == today_str:
                    formatted_list.append({
                        "league": data.get('competition', {}).get('name', 'Top division'),
                        "home": match['homeTeam']['name'],
                        "away": match['awayTeam']['name'],
                        "h_att": 2.20, "h_def": 1.70, "a_att": 1.95, "a_def": 2.05  
                    })
        except Exception:
            continue
            
    print(f"📡 Found {len(formatted_list)} actual matches playing today.")
    return formatted_list

def run_predictions():
    fixtures = get_live_fixtures()
    if not fixtures:
        print("🏁 Scan finished. No active top-tier games scheduled today.")
        return

    print("🤖 Processing parameters...")
    alerts_triggered = 0

    for item in fixtures:
        league_name = item['league']
        home_team = item['home']
        away_team = item['away']
        
        metrics = calculate_advanced_markets(item['h_att'], item['h_def'], item['a_att'], item['a_def'])
        
        if metrics["over_25_prob"] >= PROBABILITY_THRESHOLD or metrics["btts_prob"] >= PROBABILITY_THRESHOLD:
            send_telegram_alert(home_team, away_team, league_name, metrics)
            print(f"✅ ALERT SENT: {home_team} vs {away_team}")
            alerts_triggered += 1
            time.sleep(1)
            
    print(f"🏁 Execution finished. Dispatched {alerts_triggered} value lines.")

if __name__ == "__main__":
    run_predictions()
  
