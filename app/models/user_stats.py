from pydantic import BaseModel

class UserStats(BaseModel):
    ranked_score: int
    total_score: int
    play_count: int
    replays_watched: int
    total_hits: int
    accuracy: float
    pp: int
    play_time: int
    ssh_count: int
    ss_count: int
    sh_count: int
    s_count: int
    a_count: int
    b_count: int
    c_count: int
    d_count: int
    max_combo: int
