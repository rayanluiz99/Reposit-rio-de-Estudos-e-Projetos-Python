from sqlmodel import SQLModel, Field, Relationship
from typing import Optional
from datetime import datetime

class SessaoAnestesia(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    id_animal: int = Field(foreign_key="animal.id")
    id_farmaco: int = Field(foreign_key="farmaco.id")
    dose_utilizada_ml: float
    observacoes: Optional[str] = None