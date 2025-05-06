import os
from typing import Dict, List, Union
from collections import defaultdict, Counter
from app.services.res_imun_map import TYPE_EFFECTIVENESS, ABILITIES_IMMUNITIES
from app.db.supabase_ops import SupabaseService
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
            "usage_percent": entry["pct_of_teams"],
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


def extract_pokepaste_info(pokepaste_link: str):
    response = requests.get(rf"{pokepaste_link}/raw")
    all_pokemons = []
    for pokemon in response.text.strip().split("\r\n\r\n"):
        poke_info = {}
        lines = pokemon.strip().split("\r\n")

        a = lines[0]
        poke_info["name"] = a.split("@")[0].strip().lower().replace(" ", "-")
        try:
            poke_info["item"] = a.split("@")[1].strip().lower().replace(" ", "-")
        except:
            poke_info["item"] = "Unknown"
        try:
            poke_info["ability"] = (
                lines[1].split("Ability: ")[1].strip().lower().replace(" ", "-")
            )
        except:
            poke_info["ability"] = "Unknown"
        try:
            poke_info["level"] = lines[2].split("Level: ")[1].lower().strip()
        except:
            poke_info["level"] = "50"
        try:
            poke_info["tera"] = lines[3].split("Tera Type: ")[1].lower().strip()
        except:
            poke_info["tera"] = "Unknown"
        evs = {
            "hp": 0,
            "attack": 0,
            "defense": 0,
            "special_attack": 0,
            "special_defense": 0,
            "speed": 0,
        }

        try:
            ev_line = next(line for line in lines if line.startswith("EVs: "))
            all_evs = ev_line.split("EVs: ")[1].split(" / ")
            for ev in all_evs:
                if ev.endswith("HP"):
                    evs["hp"] = int(ev.split(" ")[0])

                if ev.endswith("Atk"):
                    evs["attack"] = int(ev.split(" ")[0])

                if ev.endswith("Def"):
                    evs["defense"] = int(ev.split(" ")[0])

                if ev.endswith("SpA"):
                    evs["special_attack"] = int(ev.split(" ")[0])

                if ev.endswith("SpD"):
                    evs["special_defense"] = int(ev.split(" ")[0])

                if ev.endswith("Spe"):
                    evs["speed"] = int(ev.split(" ")[0])
        except StopIteration:
            pass
        ivs = {
            "hp": 31,
            "attack": 31,
            "defense": 31,
            "special_attack": 31,
            "special_defense": 31,
            "speed": 31,
        }
        try:
            iv_line = next(line for line in lines if line.startswith("IVs: "))
            all_ivs = iv_line.split("IVs: ")[1].split(" / ")
            for iv in all_ivs:
                if iv.endswith("HP"):
                    ivs["hp"] = int(iv.split(" ")[0])

                if iv.endswith("Atk"):
                    ivs["attack"] = int(iv.split(" ")[0])

                if iv.endswith("Def"):
                    ivs["defense"] = int(iv.split(" ")[0])

                if iv.endswith("SpA"):
                    ivs["special_attack"] = int(iv.split(" ")[0])

                if iv.endswith("SpD"):
                    ivs["special_defense"] = int(iv.split(" ")[0])

                if iv.endswith("Spe"):
                    ivs["speed"] = int(iv.split(" ")[0])

        except StopIteration:
            pass

        poke_info["evs"] = evs
        poke_info["ivs"] = ivs
        try:
            poke_info["moves"] = [
                x.replace("- ", "").strip().replace(" ", "-").lower()
                for x in pokemon.split("- ")[1::]
            ]
        except:
            poke_info["moves"] = "Unkown"
        all_pokemons.append(poke_info)

    return all_pokemons


def process_team(pokepaste_link: str):
    client = SupabaseService(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_API_KEY"))

    all_pokemons = extract_pokepaste_info(pokepaste_link)
    processed_team = []
    for pokemon in all_pokemons:
        processed_team.append(extract_pokemon_details(pokemon, client))
    return processed_team


def process_pokemon(
    pokemon_info: Dict[str, Union[str, Dict[str, int], List[str]]],
):
    client = SupabaseService(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_API_KEY"))
    return extract_pokemon_details(pokemon_info, client)


def get_types_and_abilities(pokemon_name: str) -> List[str]:
    response = requests.get(rf"https://pokeapi.co/api/v2/pokemon/{pokemon_name}")
    rj = response.json()
    pkm_typing = []
    for typing in rj["types"]:
        pkm_typing.append(typing["type"]["name"])

    pkm_abilities = []
    for ability in rj["abilities"]:
        pkm_abilities.append(ability["ability"]["name"])

    return {"types": pkm_typing, "abilities": pkm_abilities}


def extract_pokemon_details(
    pokemon_info: Dict[str, Union[str, Dict[str, int], List[str]]], client
):
    name = pokemon_info.get("name")
    ability = pokemon_info.get("ability")
    item = pokemon_info.get("item")

    response = get_types_and_abilities(name)
    types = response["types"]

    immunities = set()
    if item == "air-balloon":
        immunities.add("ground")
    immunity = ABILITIES_IMMUNITIES.get(ability)
    if immunity:
        immunities.add(immunity)

    super_effective = get_super_effective_types(types)

    effective_weaknesses = [t for t in super_effective if t not in immunities]
    team_weakpoints = client.get_team_weakpoints(effective_weaknesses)
    strong_pokemon_summary = process_strong_pokemon_info(team_weakpoints)
    pokemon_info["types"] = types
    pokemon_info["counter_pokemons"] = strong_pokemon_summary["weakness_pokemon"]
    return pokemon_info


def get_super_effective_types(defending_types: List[str]):
    super_effective = set()

    for atk_type, matchups in TYPE_EFFECTIVENESS.items():
        multiplier = 1.0
        for def_type in defending_types:
            multiplier *= matchups.get(def_type, 1.0)
        if multiplier > 1.0:
            super_effective.add(atk_type)

    return super_effective
