from sqlmodel import SQLModel, Field
from typing import Optional

class Animal(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    nome: str
    especie: str
    raca: Optional[str] = None
    idade: Optional[int] = None
    peso_kg: float