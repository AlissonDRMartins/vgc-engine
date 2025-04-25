from typing import List, Optional
from dataclasses import dataclass
from supabase import create_client, Client


@dataclass
class SupabaseService:
    supabase_url: str
    supabase_api_key: str

    def get_client(self) -> Client:
        return create_client(self.supabase_url, self.supabase_api_key)

    def get_current_tournaments(self):
        client = self.get_client()
        response = client.table("metagame").select("tournament").execute()
        all_tournaments = response.data
        unique_tournaments = list(
            set(
                [
                    x["tournament"]
                    .replace("Standings: ", "")
                    .replace(" | Limitless", "")
                    for x in all_tournaments
                ]
            )
        )
        return unique_tournaments

    def get_top8_teams(self):
        client = self.get_client()
        response = client.rpc("get_top8_teams").execute()
        return response.data

    def get_team_weakpoints(self, pokemon_types: List[str]):
        client = self.get_client()
        response = client.rpc(
            "get_metagame_by_types", {"type_filter": pokemon_types}
        ).execute()

        return response.data

    def get_topx_teams(
        self, top_cut: Optional[int] = 8, team_occurrences: Optional[int] = 3
    ):
        client = self.get_client()
        response = client.rpc(
            "get_topx_teams", {"top_cut": top_cut, "team_occurrences": team_occurrences}
        ).execute()

        return response.data
