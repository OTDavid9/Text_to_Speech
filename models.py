from pydantic import BaseModel

class AudioRequest(BaseModel):
    text: str
    voice: str
