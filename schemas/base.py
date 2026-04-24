from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class BaseSchema(BaseModel): 
    id: int
    created_at: datetime

    class Config:
        from_attributes = True