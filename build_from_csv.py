import csv
import json
import os

CSV_FILE = "FC26_20250921.csv"
OUTPUT_JSON = "database.json"

# Definición de ligas principales a incluir en el juego
TARGET_LEAGUES = {
    "La Liga": {"id": "ESP1", "country": "🇪🇸 España", "display_name": "LaLiga EA Sports"},
    "Premier League": {"id": "ENG1", "country": "🏴󠁧󠁢󠁥󠁮󠁧󠁿 Inglaterra", "display_name": "Premier League"},
    "Serie A": {"id": "ITA1", "country": "🇮🇹 Italia", "display_name": "Serie A TIM"},
    "Bundesliga": {"id": "GER1", "country": "🇩🇪 Alemania", "display_name": "Bundesliga"},
    "Ligue 1": {"id": "FRA1", "country": "🇫🇷 Francia", "display_name": "Ligue 1 McDonald's"}
}

def parse_val_millions(val_raw):
    try:
        val = float(val_raw)
        return max(2, int(val / 1_000_000))
    except:
        return 5

def build_database():
    if not os.path.exists(CSV_FILE):
        print(f"❌ No se encontró el archivo {CSV_FILE} en la carpeta actual.")
        return

    print("🚀 Procesando FC26_20250921.csv...")

    teams_dict = {}
    market_players = []

    with open(CSV_FILE, mode="r", encoding="utf-8", errors="ignore") as f:
        reader = csv.DictReader(f)
        for row in reader:
            league = row.get("league_name", "").strip()
            club = row.get("club_name", "").strip()
            name = row.get("short_name", "").strip() or row.get("long_name", "").strip()
            ovr = int(row.get("overall", 70))
            pos = row.get("player_positions", "MC").split(",")[0].strip()
            val_m = parse_val_millions(row.get("value_eur", 5000000))
            face = row.get("player_face_url", "").strip()

            # Filtrar solo ligas configuradas y clubes válidos
            if league in TARGET_LEAGUES and club:
                league_id = TARGET_LEAGUES[league]["id"]
                team_key = f"{league_id}_{club}"

                if team_key not in teams_dict:
                    teams_dict[team_key] = {
                        "id": club.replace(" ", "_").upper()[:8],
                        "name": club,
                        "leagueId": league_id,
                        "logoUrl": "",
                        "players": [],
                        "pts": 0, "pj": 0, "pg": 0, "pe": 0, "pp": 0, "gf": 0, "gc": 0, "dg": 0
                    }

                player = {
                    "id": f"p_{row.get('player_id', len(market_players))}",
                    "name": name,
                    "pos": pos,
                    "ovr": ovr,
                    "val": val_m,
                    "goals": 0,
                    "assists": 0,
                    "faceUrl": face
                }

                teams_dict[team_key]["players"].append(player)

            # Jugadores de alto media para el mercado general
            elif ovr >= 80 and len(market_players) < 200:
                market_players.append({
                    "id": f"p_{row.get('player_id', len(market_players))}",
                    "name": name,
                    "pos": pos,
                    "ovr": ovr,
                    "val": val_m,
                    "goals": 0,
                    "assists": 0,
                    "faceUrl": face
                })

    # Formatear equipos y calcular medias
    formatted_teams = []
    for team_key, team_info in teams_dict.items():
        players = team_info.pop("players")
        if players:
            avg_ovr = sum(p["ovr"] for p in players) // len(players)
            team_info["att"] = min(99, avg_ovr + 3)
            team_info["def"] = min(99, avg_ovr - 1)
        else:
            team_info["att"] = 75
            team_info["def"] = 75
        
        formatted_teams.append(team_info)

    # Ligas para la interfaz
    leagues_list = [
        {"id": data["id"], "name": data["display_name"], "country": data["country"]}
        for data in TARGET_LEAGUES.values()
    ]

    full_db = {
        "userTeamId": "REAL_MAD",
        "selectedLeague": "ESP1",
        "budget": 150,
        "week": 1,
        "season": 2026,
        "leagues": leagues_list,
        "teams": formatted_teams,
        "market": market_players,
        "awards": {"ballonDor": None, "goldenBoot": None, "history": []}
    }

    with open(OUTPUT_JSON, "w", encoding="utf-8") as out:
        json.dump(full_db, out, ensure_ascii=False, indent=2)

    print(f"✅ ¡Éxito! Base de datos creada con {len(formatted_teams)} equipos y {len(market_players)} jugadores en el mercado.")

if __name__ == "__main__":
    build_database()
