from sqlmodel import SQLModel, Field
from typing import Optional

class Farmaco(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    nome: str
    dose: float  # ← ESTE CAMPO DEVE EXISTIR
    concentracao: float
    unidade_dose: str
    modo_uso: str = "bolus"  # Valor padrão
    volume_seringa: Optional[float] = None
    comentario: Optional[str] = None