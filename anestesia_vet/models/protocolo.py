from sqlmodel import SQLModel, Field, Relationship
from typing import List, Optional
from datetime import datetime

class ProtocoloBase(SQLModel):
    nome: str
    descricao: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.now)

class Protocolo(ProtocoloBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    farmacos: List["ProtocoloFarmaco"] = Relationship(back_populates="protocolo")

class ProtocoloFarmacoBase(SQLModel):
    protocolo_id: Optional[int] = Field(default=None, foreign_key="protocolo.id", primary_key=True)
    farmaco_id: Optional[int] = Field(default=None, foreign_key="farmaco.id", primary_key=True)
    ordem: int  # Para ordenar os fármacos no protocolo

class ProtocoloFarmaco(ProtocoloFarmacoBase, table=True):
    protocolo: "Protocolo" = Relationship(back_populates="farmacos")
    farmaco: "Farmaco" = Relationship()  # Relacionamento com Farmaco