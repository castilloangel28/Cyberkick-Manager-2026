import csv
import json
import os

CSV_FILE = "male_players.csv"
OUTPUT_JSON = "database.json"

# Ligas y equipos principales a incluir en la base de datos
TARGET_TEAMS = {
    "Real Madrid": {"id": "RM", "country": "🇪🇸"},
    "FC Barcelona": {"id": "FCB", "country": "🇪🇸"},
    "Atlético de Madrid": {"id": "ATM", "country": "🇪🇸"},
    "Manchester City": {"id": "MCI", "country": "🇬🇧"},
    "Arsenal": {"id": "ARS", "country": "🇬🇧"},
    "Bayern München": {"id": "BAY", "country": "🇩🇪"},
    "Paris Saint-Germain": {"id": "PSG", "country": "🇫🇷"},
    "Inter": {"id": "INT", "country": "🇮🇹"}
}

def clean_value(val_str):
    try:
        val = float(val_str)
        return int(val / 1000000) if val > 1000 else int(val)
    except:
        return 15

def process_kaggle_csv():
    if not os.path.exists(CSV_FILE):
        print(f"❌ Error: No se encontró '{CSV_FILE}'. Asegúrate de renombrar tu CSV de Kaggle.")
        return

    teams_data = {name: {"players": [], "logo": ""} for name in TARGET_TEAMS}
    market_players = []

    print("⚡ Procesando datos, caras y escudos desde Kaggle...")

    with open(CSV_FILE, mode="r", encoding="utf-8") as file:
        reader = csv.DictReader(file)
        
        for row in reader:
            name = row.get("short_name") or row.get("Name") or row.get("long_name") or "Jugador"
            club = row.get("club_name") or row.get("Club") or ""
            ovr = int(row.get("overall") or row.get("Overall") or 75)
            pos_raw = row.get("player_positions") or row.get("Position") or "MC"
            pos = pos_raw.split(",")[0].strip()
            val = clean_value(row.get("value_eur") or row.get("Value") or 10000000)
            
            face_url = row.get("player_face_url") or row.get("photo_url") or ""
            logo_url = row.get("club_logo_url") or row.get("logo_url") or ""

            player_obj = {
                "name": name,
                "pos": pos,
                "ovr": ovr,
                "val": max(5, val),
                "faceUrl": face_url
            }

            if club in TARGET_TEAMS:
                teams_data[club]["players"].append(player_obj)
                if not teams_data[club]["logo"] and logo_url:
                    teams_data[club]["logo"] = logo_url
            elif ovr >= 84 and len(market_players) < 25:
                market_players.append(player_obj)

    formatted_teams = []
    user_squad = []

    for club_name, info in teams_data.items():
        meta = TARGET_TEAMS[club_name]
        players = info["players"]
        avg_ovr = sum(p["ovr"] for p in players) // len(players) if players else 80

        formatted_teams.append({
            "id": meta["id"],
            "name": club_name,
            "logoUrl": info["logo"],
            "att": min(99, avg_ovr + 3),
            "def": min(99, avg_ovr - 2),
            "pts": 0, "pj": 0, "dg": 0,
            "country": meta["country"]
        })

        if meta["id"] == "RM":
            user_squad = players[:16] if players else []

    final_db = {
        "userTeamId": "RM",
        "budget": 150,
        "week": 1,
        "teams": formatted_teams,
        "squad": user_squad,
        "market": market_players
    }

    with open(OUTPUT_JSON, "w", encoding="utf-8") as out:
        json.dump(final_db, out, ensure_ascii=False, indent=2)

    print(f"✅ ¡Base de datos creada exitosamente en '{OUTPUT_JSON}'!")

if __name__ == "__main__":
    process_kaggle_csv()
