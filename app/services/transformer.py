from typing import Dict, List
from collections import defaultdict, Counter
import requests


def process_strong_pokemon_info(pokemon_info: Dict[str, str]):

    summary = []

    grouped = defaultdict(list)
    for poke in pokemon_info:
        grouped[poke["name"]].append(poke)

    for name, entries in grouped.items():
        total = len(entries)

        items = Counter([entry["item"] for entry in entries])
        abilities = Counter([entry["ability"] for entry in entries])
        teras = Counter([entry["tera"] for entry in entries])
        moves = Counter()
        for entry in entries:
            moves.update(entry["moves"])

        result = {
            "name": name,
            "items": [
                {"name": item, "usage": round((count / total) * 100.0, 2)}
                for item, count in items.items()
            ],
            "abilities": [
                {"name": ability, "usage": round((count / total) * 100.0, 2)}
                for ability, count in abilities.items()
            ],
            "teratype": [
                {"name": tera, "usage": round((count / total) * 100.0, 2)}
                for tera, count in teras.items()
            ],
            "moves": [
                {"name": move, "usage": round((count / total) * 100.0, 2)}
                for move, count in moves.items()
            ],
        }

        summary.append(result)

    return {"weakness_pokemon": summary}


def filter_strong_pokemons(
    teams_info: List[Dict[str, str]], strong_against_player_team: List[str]
) -> List[Dict[str, str]]:
    filtered_teams = []
    for team in teams_info:
        team_members = [name.strip() for name in team["sorted_team"].split(",")]
        if any(pokemon in team_members for pokemon in strong_against_player_team):
            top_cut_team_player = (
                team["best_placing_team"]
                .split("Player:")[1]
                .split(" Tournament:")[0]
                .strip()
                .capitalize()
            )
            top_cut_team_tournament = (
                team["best_placing_team"]
                .split("Tournament:")[1]
                .split(" Placing:")[0]
                .strip()
            )
            top_cut_team_placing = (
                team["best_placing_team"].split("Placing:")[1].strip()
            )
            filtered_teams.append(
                {
                    "top_cut_tournament": top_cut_team_tournament,
                    "top_cut_player": top_cut_team_player,
                    "top_cut_placing": top_cut_team_placing,
                    "team": team["sorted_team"].split(","),
                    "occurences": team["occurrences"],
                    "best_placing": team["best_placing"],
                    "worst_placing": team["worst_placing"],
                }
            )

    return {"strong_teams": filtered_teams}


def get_all_pokemons_from_type(pokemons_types: List[str]):
    pokemons = []
    for pkm_type in pokemons_types:
        response = requests.get(rf"https://pokeapi.co/api/v2/type/{pkm_type}")
        jr = response.json()

        for pokemon in jr["pokemon"]:
            pokemons.append(pokemon["pokemon"]["name"])

    return pokemons
