import os
from fastapi import APIRouter
from app.db.supabase_ops import SupabaseService
from app.services.transformer import (
    process_strong_pokemon_info,
    filter_strong_pokemons,
    process_team,
    process_pokemon,
)
from app.models.schemas import (
    HighestUsagePokemons,
    PokemonTypes,
    MovesList,
    AbilitiesList,
    PokepasteLink,
    PokemonInfo,
)

router = APIRouter()


@router.post("/weakpoints")
def get_team_weapoints(pokemon_team: PokemonTypes):
    client = SupabaseService(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_API_KEY"))
    response = client.get_team_weakpoints(pokemon_team.types)
    strong_pokemon_summary = process_strong_pokemon_info(response)
    return strong_pokemon_summary


@router.post("/top_teams")
def get_top_pokemons(highest_usage_pokemons: HighestUsagePokemons):
    client = SupabaseService(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_API_KEY"))
    response = client.get_topx_teams(
        top_cut=highest_usage_pokemons.top_cut,
        team_occurrences=highest_usage_pokemons.team_occurrences,
    )
    filtered_teams = filter_strong_pokemons(
        teams_info=response, strong_against_player_team=highest_usage_pokemons.pokemons
    )
    return filtered_teams


@router.post("/moves_details")
def get_move_details(moves_list: MovesList):
    client = SupabaseService(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_API_KEY"))
    response = client.get_moves_details(moves_list.moves)
    return {"moves": response}


@router.get("/items")
def get_item_details():
    client = SupabaseService(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_API_KEY"))
    response = client.get_items_details()

    return {"items": response}


@router.post("/abilities")
def get_abitily_details(abilities_list: AbilitiesList):
    client = SupabaseService(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_API_KEY"))
    response = client.get_abilities_details(abilities_list.abilities)

    return {"abilities": response}


@router.post("/analyze_pokepaste")
def pokepaste_analysis(pokepaste_link: PokepasteLink):
    info = process_team(pokepaste_link.pokepaste)
    return {"team_info": info}


@router.post("/analyze_pokemon")
def pokemon_analysis(pokemon_info: PokemonInfo):
    poke_info = {
        "name": pokemon_info.name,
        "item": pokemon_info.item,
        "ability": pokemon_info.ability,
        "level": pokemon_info.level,
        "tera": pokemon_info.tera,
        "evs": pokemon_info.evs,
        "nature": pokemon_info.nature,
        "ivs": pokemon_info.ivs,
        "moves": pokemon_info.moves,
    }
    info = process_pokemon(poke_info)
    return {"pokemon_info": info}
