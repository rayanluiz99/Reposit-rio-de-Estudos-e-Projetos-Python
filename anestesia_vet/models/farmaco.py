from sqlmodel import SQLModel, Field
from typing import Optional

class Farmaco(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    nome: str
    concentracao_mg_ml: float
    volume_total_ml: Optional[float] = Field(default=None)
    via_administracao: Optional[str] = Field(default=None)
    dose_mg_por_kg: float