from pydantic import BaseModel

class AudioRequest(BaseModel):
    text: str
    voice: str
    # speed: float = 1.0  # 