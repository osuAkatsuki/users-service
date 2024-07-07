from pydantic import BaseModel

class TournamentBadge(BaseModel):
    id: int
    name: str
    icon: str
