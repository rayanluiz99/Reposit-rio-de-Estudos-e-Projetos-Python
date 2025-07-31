from sqlmodel import SQLModel, Field, Relationship
from typing import Optional
from datetime import datetime

class SessaoAnestesia(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    id_animal: Optional[int] = Field(default=None, foreign_key="animal.id")
    id_farmaco: int = Field(foreign_key="farmaco.id")
    dose_utilizada_ml: float = Field(gt=0)  # Dose > 0
    observacoes: Optional[str] = None
    # Adicionar data também para sessões normais
    data: datetime = Field(default_factory=datetime.now)
    config_infusao_id: Optional[int] = Field(
        default=None,
        foreign_key="configinfusao.id",
        nullable=True
    )
    config_infusao: Optional["ConfigInfusao"] = Relationship(
        back_populates="sessoes",
        sa_relationship_kwargs={
            'foreign_keys': '[SessaoAnestesia.config_infusao_id]'
        }
    )

class SessaoAvulsaAnestesia(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    especie: str
    nome_animal: str
    peso_kg: float
    id_farmaco: int
    dose_utilizada_ml: float
    observacoes: Optional[str] = None
    data: datetime = Field(default_factory=datetime.now)
    
