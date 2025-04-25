# app/models/schemas.py
from typing import List
from pydantic import BaseModel


class HighestUsagePokemons(BaseModel):
    top_cut: int
    team_occurrences: int
    pokemons: List[str]


class PokemonTypes(BaseModel):
    types: List[str]
