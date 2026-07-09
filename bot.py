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

def calculate_over_15_prob(home_attack, home_defense, away_attack, away_defense):
    """Calculates explicit Over 1.5 goals probability using Dixon-Coles variables."""
    baseline = 1.65
    lambda_home = (home_attack * away_defense * 1.15) / baseline
    mu_away = (away_attack * home_defense) / (baseline * 1.15)
    
    p_home = [poisson_probability(i, lambda_home) for i in range(2)]
    p_away = [poisson_probability(i, mu_away) for i in range(2)]
    
    # Dixon-Coles low-scoring dependence correction (Rho = -0.08)
    p_0_0 = (p_home[0] * p_away[0]) * (1 - (lambda_home * mu_away * -0.08))
    p_1_0 = (p_home[1] * p_away[0]) * (1 + (mu_away * -0.08))
    p_0_1 = (p_home[0] * p_away[1]) * (1 + (lambda_home * -0.08))
    
    total_under_15 = p_0_0 + p_1_0 + p_0_1
    prob_over_15 = max(0.0, min(1.0, 1.0 - total_under_15))
    
    fair_odds = round(1 / prob_over_15, 2) if prob_over_15 > 0 else 99.0
    return round(prob_over_15 * 100, 2), fair_odds

def parse_h2h_goals(score_str):
    """Parses a score string like '2-1' or '3-0' and returns total goals scored."""
    try:
        parts = score_str.split('-')
        return int(parts[0]) + int(parts[1])
    except Exception:
        return 0

def send_accumulator_report(fixtures_list, target_date):
    """Dispatches the finalized high-volume accumulator list to Telegram."""
    url = "https://api.telegram.org/bot8822256842:AAEYdTp5BH4wQ3czEYsP1XCDGNX3e0_fw_Y/sendMessage"
    
    message = f"📊 **STRATEGY ACCUMULATOR SHEET (OVER 1.5)** 📊\n🗓️ **Date:** {target_date}\n"
    message += f"🎯 **Qualified Picks:** {len(fixtures_list)} Matches\n"
    message += "🔥 *Filter Rule: Last H2H Total Goals ≥ 3*\n"
    message += "=============================\n\n"
    
    for idx, game in enumerate(fixtures_list, 1):
        message += (
            f"{idx}. 🏆 *{game['league']}*\n"
            f"   ⚽ `{game['home']} vs {game['away']}`\n"
            f"   ⏱️ Last H2H Score: `{game['last_score']}`\n"
            f"   📈 **Probability:** {game['prob']}% | **Fair Odds:** {game['odds']}\n\n"
        )
        
    message += "⚠️ *Wager as high-probability singles or split into 5-fold tickets.*"
    
    browser_headers = {"User-Agent": "Mozilla/5.0"}
    payload = {"chat_id": TELEGRAM_CHAT_ID, "text": message, "parse_mode": "Markdown"}
    try:
        requests.post(url, json=payload, headers=browser_headers, timeout=12)
        print("📡 High-volume strategy report sent to Telegram!")
    except Exception as e:
        print(f"❌ Telegram pipeline failure: {e}")

def get_global_strategy_fixtures():
    """Massive internal fixture data feed matrix containing global games and their last H2H scorelines."""
    return [
        {"league": "Iceland Urvalsdeild", "home": "Vikingur Reykjavik", "away": "Valur", "last_h2h": "2-1", "h_att": 2.90, "h_def": 1.40, "a_att": 2.40, "a_def": 1.80},
        {"league": "Norway Eliteserien", "home": "Bodo/Glimt", "away": "Molde", "last_h2h": "3-2", "h_att": 2.80, "h_def": 1.20, "a_att": 2.20, "a_def": 1.70},
        {"league": "Sweden Allsvenskan", "home": "Malmo FF", "away": "Sirius", "last_h2h": "3-0", "h_att": 2.70, "h_def": 1.00, "a_att": 1.90, "a_def": 2.10},
        {"league": "USA MLS", "home": "Inter Miami", "away": "Orlando City", "last_h2h": "1-3", "h_att": 2.65, "h_def": 1.50, "a_att": 1.85, "a_def": 1.95},
        {"league": "Singapore Premier League", "home": "Albirex Niigata", "away": "Lion City", "last_h2h": "4-2", "h_att": 3.40, "h_def": 1.90, "a_att": 3.10, "a_def": 1.60},
        {"league": "Estonia Meistriliiga", "home": "Levadia Tallinn", "away": "Narva Trans", "last_h2h": "3-1", "h_att": 2.85, "h_def": 0.60, "a_att": 1.20, "a_def": 2.70},
        {"league": "Iceland 1. Deild", "home": "Fjolnir", "away": "Leiknir Reykjavik", "last_h2h": "0-3", "h_att": 2.60, "h_def": 1.50, "a_att": 2.10, "a_def": 2.10},
        {"league": "Norway 1. Divisjon", "home": "Lyn Oslo", "away": "Stabaek", "last_h2h": "2-2", "h_att": 2.20, "h_def": 1.40, "a_att": 2.05, "a_def": 1.85},
        {"league": "Peru Liga 1", "home": "Sporting Cristal", "away": "Melgar", "last_h2h": "1-2", "h_att": 2.70, "h_def": 1.20, "a_att": 1.80, "a_def": 1.30},
        {"league": "Australia NPL Queensland", "home": "Gold Coast Knights", "away": "Peninsula Power", "last_h2h": "4-1", "h_att": 2.95, "h_def": 1.25, "a_att": 2.40, "a_def": 1.95},
        {"league": "Finland Veikkausliiga", "home": "HJK Helsinki", "away": "Ilves", "last_h2h": "1-1", "h_att": 2.10, "h_def": 1.10, "a_att": 1.90, "a_def": 1.80}, # Should filter out (2 goals)
        {"league": "Ireland Premier Division", "home": "Derry City", "away": "Dundalk", "last_h2h": "1-0", "h_att": 2.20, "h_def": 0.90, "a_att": 1.30, "a_def": 2.10}, # Should filter out (1 goal)
        {"league": "Brazil Serie A", "home": "Flamengo", "away": "Botafogo", "last_h2h": "2-1", "h_att": 2.30, "h_def": 1.10, "a_att": 1.80, "a_def": 1.40},
        {"league": "Japan J1 League", "home": "Yokohama Marinos", "away": "Urawa Reds", "last_h2h": "3-1", "h_att": 2.50, "h_def": 1.60, "a_att": 1.70, "a_def": 1.50},
        {"league": "Lithuania A Lyga", "home": "Zalgiris Vilnius", "away": "Dziugas", "last_h2h": "4-0", "h_att": 2.40, "h_def": 0.80, "a_att": 1.10, "a_def": 2.20},
        {"league": "Sweden Superettan", "home": "Osters IF", "away": "Utsiktens", "last_h2h": "0-2", "h_att": 2.15, "h_def": 1.10, "a_att": 1.60, "a_def": 1.90}, # Filter out
        {"league": "Chile Primera Division", "home": "Universidad de Chile", "away": "Cobresal", "last_h2h": "2-2", "h_att": 2.10, "h_def": 1.00, "a_att": 1.70, "a_def": 1.80},
        {"league": "Ecuador Serie A", "home": "Barcelona SC", "away": "LDU Quito", "last_h2h": "1-3", "h_att": 2.25, "h_def": 1.15, "a_att": 1.95, "a_def": 1.45},
        {"league": "Venezuela Primera", "home": "Deportivo Tachira", "away": "Caracas", "last_h2h": "0-0", "h_att": 1.90, "h_def": 0.95, "a_att": 1.50, "a_def": 1.60}, # Filter out
        {"league": "South Korea K League 1", "home": "Ulsan HD", "away": "Pohang Steelers", "last_h2h": "2-1", "h_att": 2.20, "h_def": 1.15, "a_att": 1.85, "a_def": 1.30},
        {"league": "Norway Eliteserien Tier 2", "home": "Valerenga", "away": "Aalesund", "last_h2h": "3-1", "h_att": 2.50, "h_def": 1.20, "a_att": 1.60, "a_def": 2.20},
        {"league": "Iceland Urvalsdeild B", "home": "Breidablik", "away": "KA Akureyri", "last_h2h": "4-0", "h_att": 2.80, "h_def": 1.30, "a_att": 1.70, "a_def": 2.30},
        {"league": "USA USL Championship", "home": "Tampa Bay Rowdies", "away": "Louisville City", "last_h2h": "2-3", "h_att": 2.40, "h_def": 1.40, "a_att": 2.50, "a_def": 1.30},
        {"league": "Finland Ykkonen", "home": "TPS Turku", "away": "KTP", "last_h2h": "1-2", "h_att": 2.20, "h_def": 1.20, "a_att": 2.30, "a_def": 1.50},
        {"league": "Brazil Serie B", "home": "Santos", "away": "Sport Recife", "last_h2h": "1-1", "h_att": 1.80, "h_def": 0.80, "a_att": 1.60, "a_def": 1.10} # Filter out
    ]

def run_strategy_predictions():
    target_date = "2026-07-10"
    fixtures = get_global_strategy_fixtures()
    
    print(f"🤖 Screening {len(fixtures)} global fixtures against H2H goal filters...")
    qualified_list = []

    for item in fixtures:
        last_score = item['last_h2h']
        total_h2h_goals = parse_h2h_goals(last_score)
        
        # 🛡️ THE STRATEGIC H2H FILTER STEP: Must have produced 3 or more goals last time out
        if total_h2h_goals >= 3:
            prob, fair_odds = calculate_over_15_prob(item['h_att'], item['h_def'], item['a_att'], item['a_def'])
            
            qualified_list.append({
                "league": item['league'],
                "home": item['home'],
                "away": item['away'],
                "last_score": last_score,
                "prob": prob,
                "odds": fair_odds
            })
            
    # Sort the matches from highest calculated mathematical probability to lowest
    qualified_list.sort(key=lambda x: x['prob'], reverse=True)
    
    # Bound payload display strictly within your target 10-20 bracket range
    final_picks = qualified_list[:20]
    
    if final_picks:
        send_accumulator_report(final_picks, target_date)
        print(f"🏁 Complete! Screened out low-scoring H2Hs. Dispatched {len(final_picks)} high-volume picks to Telegram.")
    else:
        print("❌ Evaluation finished. 0 fixtures satisfied the strategy conditions.")

if __name__ == "__main__":
    run_strategy_predictions()
    
