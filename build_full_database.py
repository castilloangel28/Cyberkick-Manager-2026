import csv
import json
import os

CSV_FILE = "male_players.csv"
OUTPUT_JSON = "database.json"

# Mapeo de ligas reales y sus equipos
LEAGUES_CONFIG = {
    "LaLiga": {
        "id": "ESP1",
        "country": "🇪🇸 España",
        "teams": ["Real Madrid", "FC Barcelona", "Atlético de Madrid", "Athletic Club", "Real Sociedad", "Villarreal CF", "Real Betis", "Sevilla FC"]
    },
    "Premier League": {
        "id": "ENG1",
        "country": "🏴󠁧󠁢󠁥󠁮󠁧󠁿 Inglaterra",
        "teams": ["Manchester City", "Arsenal", "Liverpool", "Aston Villa", "Tottenham Hotspur", "Chelsea", "Manchester United", "Newcastle United"]
    },
    "Serie A": {
        "id": "ITA1",
        "country": "🇮🇹 Italia",
        "teams": ["Inter", "AC Milan", "Juventus", "Atalanta", "Napoli", "AS Roma", "Lazio", "Fiorentina"]
    },
    "Bundesliga": {
        "id": "GER1",
        "country": "🇩🇪 Alemania",
        "teams": ["Bayer 04 Leverkusen", "Bayern München", "VfB Stuttgart", "RB Leipzig", "Borussia Dortmund", "Eintracht Frankfurt"]
    }
}

def clean_val(val_str):
    try:
        val = float(val_str)
        return int(val / 1000000) if val > 1000 else int(val)
    except:
        return 10

def generate_massive_db():
    if not os.path.exists(CSV_FILE):
        print(f"❌ No se encontró {CSV_FILE}. Renombra tu archivo de Kaggle.")
        return

    print("🚀 Procesando todas las ligas, jugadores y competiciones del mundo...")

    # Crear mapa de equipos
    teams_dict = {}
    all_teams_flat = {}

    for l_name, l_data in LEAGUES_CONFIG.items():
        for t_name in l_data["teams"]:
            t_id = t_name.replace(" ", "_").upper()[:6]
            teams_dict[t_name] = {
                "id": t_id,
                "name": t_name,
                "leagueId": l_data["id"],
                "logoUrl": "",
                "players": [],
                "pts": 0, "pj": 0, "pg": 0, "pe": 0, "pp": 0, "gf": 0, "gc": 0, "dg": 0
            }
            all_teams_flat[t_name] = t_id

    market_players = []

    with open(CSV_FILE, mode="r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            name = row.get("short_name") or row.get("Name") or "Jugador"
            club = row.get("club_name") or row.get("Club") or ""
            ovr = int(row.get("overall") or row.get("Overall") or 70)
            pos = (row.get("player_positions") or row.get("Position") or "MC").split(",")[0].strip()
            val = clean_val(row.get("value_eur") or row.get("Value") or 5000000)
            face = row.get("player_face_url") or row.get("photo_url") or ""
            logo = row.get("club_logo_url") or row.get("logo_url") or ""

            player = {
                "id": f"p_{len(market_players) + 100}",
                "name": name,
                "pos": pos,
                "ovr": ovr,
                "val": max(3, val),
                "goals": 0,
                "assists": 0,
                "faceUrl": face
            }

            if club in teams_dict:
                teams_dict[club]["players"].append(player)
                if not teams_dict[club]["logoUrl"] and logo:
                    teams_dict[club]["logoUrl"] = logo
            elif ovr >= 78 and len(market_players) < 200:
                market_players.append(player)

    # Calcular ataque y defensa promedio para cada club
    formatted_teams = []
    for t_name, t_info in teams_dict.items():
        players = t_info["players"]
        if players:
            avg_ovr = sum(p["ovr"] for p in players) // len(players)
            t_info["att"] = min(99, avg_ovr + 2)
            t_info["def"] = min(99, avg_ovr - 2)
        else:
            t_info["att"] = 75
            t_info["def"] = 75
        
        # Eliminar la lista interna de jugadores para no duplicar datos pesados
        p_list = t_info.pop("players")
        formatted_teams.append(t_info)
        # Asignar clubId a cada jugador
        for p in p_list:
            p["clubId"] = t_info["id"]

    # Estructura maestra del juego
    full_db = {
        "userTeamId": "REALM",
        "selectedLeague": "ESP1",
        "budget": 150,
        "week": 1,
        "season": 2026,
        "leagues": [
            {"id": "ESP1", "name": "LaLiga EA Sports", "country": "🇪🇸 España"},
            {"id": "ENG1", "name": "Premier League", "country": "🏴󠁧󠁢󠁥󠁮󠁧󠁿 Inglaterra"},
            {"id": "ITA1", "name": "Serie A TIM", "country": "🇮🇹 Italia"},
            {"id": "GER1", "name": "Bundesliga", "country": "🇩🇪 Alemania"}
        ],
        "teams": formatted_teams,
        "market": market_players,
        "awards": {
            "ballonDor": None,
            "goldenBoot": None,
            "history": []
        }
    }

    with open(OUTPUT_JSON, "w", encoding="utf-8") as out:
        json.dump(full_db, out, ensure_ascii=False, indent=2)

    print(f"✅ ¡`database.json` completo generado con {len(formatted_teams)} equipos y mercado global!")

if __name__ == "__main__":
    generate_massive_db()
