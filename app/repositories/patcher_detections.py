from datetime import datetime

from pydantic import BaseModel


class PatcherDetection(BaseModel):
    id: str
    method_name: str
    method_assembly_hash: str
    method_assembly_instructions: str
    created_at: datetime
    updated_at: datetime
    patcher_token_log_id: str


READ_PARAMS = """\
    id, method_name, method_assembly_hash, method_assembly_instructions, created_at, updated_at, patcher_token_log_id
"""


# TODO: figure out a way to delete records per-user
