from pydantic import BaseModel

class CustomBadge(BaseModel):
    name: str
    icon: str
    enabled: bool