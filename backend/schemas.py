from pydantic import BaseModel
from typing import Optional, List

class KBBase(BaseModel):
    title: str
    content: str
    category: Optional[str] = "general"

class KBResponse(KBBase):
    id: int
    class Config:
        from_attributes = True

class ChatRequest(BaseModel):
    user_id: str
    question: str
    stream: bool = False

class ConfigBase(BaseModel):
    avatar_style: str
    voice_type: str
    greeting_text: str

class ConfigResponse(ConfigBase):
    id: int
    class Config:
        from_attributes = True