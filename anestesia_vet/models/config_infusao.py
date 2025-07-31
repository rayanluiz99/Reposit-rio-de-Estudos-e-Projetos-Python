from sqlmodel import SQLModel, Field
from typing import Optional
from enum import Enum

class TipoEquipo(str, Enum):
    MACROGOTAS = "macrogotas"
    MICROGOTAS = "microgotas"

class ConfigInfusao(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    peso_kg: float = Field(gt=0, description="Peso do paciente em kg")
    taxa_ml_kg_h: float = Field(default=1.0, gt=0)
    equipo_tipo: TipoEquipo = Field(default=TipoEquipo.MACROGOTAS)
    volume_bolsa_ml: float = Field(default=20.0, gt=0)
    
    # Relacionamento opcional com sessão
    sessao_id: Optional[int] = Field(default=None, foreign_key="sessaoanestesia.id")