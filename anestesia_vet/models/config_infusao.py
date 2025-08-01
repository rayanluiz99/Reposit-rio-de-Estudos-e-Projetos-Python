from __future__ import annotations
from sqlmodel import SQLModel, Field, Relationship
from typing import List, Optional
from enum import Enum
from models.sessao import SessaoAnestesia

class TipoEquipo(str, Enum):
    MACROGOTAS = "macrogotas"
    MICROGOTAS = "microgotas"

class ConfigInfusao(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    peso_kg: float = Field(gt=0)
    taxa_ml_kg_h: float = Field(default=1.0)
    equipo_tipo: TipoEquipo = Field(default=TipoEquipo.MACROGOTAS)
    volume_bolsa_ml: float = Field(default=20.0)
    
    # Relacionamento corrigido (usando string literal)
    sessoes: List["SessaoAnestesia"] = Relationship(
        back_populates="config_infusao",
        sa_relationship_kwargs={
            'foreign_keys': '[SessaoAnestesia.config_infusao_id]'
        }
    )