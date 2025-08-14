from sqlmodel import SQLModel, Field
from typing import Optional

class Farmaco(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    nome: str
    dose: float
    concentracao: float
    unidade_dose: str
    modo_uso: str = "bolus"
    volume_seringa: Optional[float] = None
    comentario: Optional[str] = None
    tipo_infusao: str = "padrao"  # padrao, especifica, vasoativo
    doses_variaveis: Optional[str] = Field(default="", nullable=True) 

