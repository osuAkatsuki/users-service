from pydantic import BaseModel


class Badge(BaseModel):
    id: int
    name: str
    icon: str
    colour: str
