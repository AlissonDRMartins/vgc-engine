from typing import List, Dict, Optional
from pydantic import BaseModel


class HighestUsagePokemons(BaseModel):
    top_cut: int
    team_occurrences: int
    pokemons: List[str]


class PokemonTypes(BaseModel):
    types: List[str]


class MovesList(BaseModel):
    moves: List[str]


class AbilitiesList(BaseModel):
    abilities: List[str]


class PokepasteLink(BaseModel):
    pokepaste: str


class PokemonInfo(BaseModel):
    name: str
    item: Optional[str] = ""
    ability: str
    level: Optional[int] = 50
    tera: Optional[str] = "stellar"
    evs: Optional[Dict[str, int]] = {
        "hp": 0,
        "attack": 0,
        "defense": 0,
        "special_attack": 0,
        "special_defense": 0,
        "speed": 0,
    }
    nature: Optional[str] = "hardy"
    ivs: Optional[Dict[str, int]] = {
        "hp": 31,
        "attack": 31,
        "defense": 31,
        "special_attack": 31,
        "special_defense": 31,
        "speed": 31,
    }
    moves: Optional[List[str]] = []
