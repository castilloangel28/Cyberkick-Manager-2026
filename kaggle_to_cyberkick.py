import csv
import json

# Archivo descargado de Kaggle
CSV_FILE = "male_players.csv"  # O el nombre de tu archivo .csv
OUTPUT_JSON = "database.json"

# Equipos que quieres incluir en la liga de tu PWA
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
    """ Convierte valores de mercado como '€150M' o números puros a millones enteros """
    try:
        val = float(val_str)
        return int(val / 1000000) if val > 1000 else int(val)
    except:
        return 20

def process_kaggle_csv():
    teams_data = {name: {"players": [], "att_sum": 0, "def_sum": 0} for name in TARGET_TEAMS}
    market_players = []

    print("Procesando datos de Kaggle...")

    with open(CSV_FILE, mode="r", encoding="utf-8") as file:
        reader = csv.DictReader(file)
        
        for row in reader:
            # Adaptación según encabezados comunes de Kaggle (short_name, overall, club_name, etc.)
            name = row.get("short_name") or row.get("Name") or row.get("long_name")
            club = row.get("club_name") or row.get("Club")
            ovr = int(row.get("overall") or row.get("Overall") or 75)
            pos = row.get("player_positions") or row.get("Position") or "MC"
            pos = pos.split(",")[0].strip() # Tomar primera posición
            val = clean_value(row.get("value_eur") or row.get("Value") or "10000000")

            player_obj = {
                "name": name,
                "pos": pos,
                "ovr": ovr,
                "val": max(5, val)
            }

            # Asignar a equipo blanco o al mercado
            if club in TARGET_TEAMS:
                teams_data[club]["players"].append(player_obj)
            elif ovr >= 85 and len(market_players) < 20:
                market_players.append(player_obj)

    # Construir estructura final para CyberKick
    formatted_teams = []
    user_squad = []

    for club_name, info in teams_data.items():
        meta = TARGET_TEAMS[club_name]
        players = info["players"]
        
        # Calcular medias de ataque y defensa según rating del plantel
        if players:
            avg_ovr = sum(p["ovr"] for p in players) // len(players)
            att = min(99, avg_ovr + 2)
            defense = min(99, avg_ovr - 2)
        else:
            att, defense = 80, 80

        formatted_teams.append({
            "id": meta["id"],
            "name": club_name,
            "att": att,
            "def": defense,
            "pts": 0,
            "pj": 0,
            "dg": 0,
            "country": meta["country"]
        })

        if meta["id"] == "RM": # Equipo inicial del jugador
            user_squad = players[:11] if players else []

    final_db = {
        "userTeamId": "RM",
        "budget": 120,
        "week": 1,
        "teams": formatted_teams,
        "squad": user_squad,
        "market": market_players
    }

    with open(OUTPUT_JSON, "w", encoding="utf-8") as out:
        json.dump(final_db, out, ensure_ascii=False, indent=2)

    print(f"¡Éxito! Base de datos real creada en '{OUTPUT_JSON}'.")

if __name__ == "__main__":
    process_kaggle_csv()
