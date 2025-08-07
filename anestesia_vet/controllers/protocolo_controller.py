from sqlmodel import Session, select
from models.protocolo import Protocolo, ProtocoloFarmaco
from models.farmaco import Farmaco
from typing import List, Tuple

def criar_protocolo(session: Session, nome: str, descricao: str = None, farmaco_ids: List[int] = None) -> Protocolo:
    protocolo = Protocolo(nome=nome, descricao=descricao)
    session.add(protocolo)
    session.commit()
    session.refresh(protocolo)
    
    if farmaco_ids:
        for ordem, farmaco_id in enumerate(farmaco_ids, start=1):
            # Verificar se o fármaco existe
            farmaco = session.get(Farmaco, farmaco_id)
            if farmaco:
                pf = ProtocoloFarmaco(protocolo_id=protocolo.id, farmaco_id=farmaco_id, ordem=ordem)
                session.add(pf)
        session.commit()
    
    return protocolo

def listar_protocolos(session: Session) -> List[Protocolo]:
    protocolos = session.exec(select(Protocolo)).all()
    return protocolos

def obter_protocolo(session: Session, protocolo_id: int) -> Protocolo:
    return session.get(Protocolo, protocolo_id)

def obter_farmacos_do_protocolo(session: Session, protocolo_id: int) -> List[Tuple[Farmaco, int]]:
    stmt = select(ProtocoloFarmaco).where(ProtocoloFarmaco.protocolo_id == protocolo_id).order_by(ProtocoloFarmaco.ordem)
    resultados = session.exec(stmt).all()
    
    farmacos = []
    for pf in resultados:
        farmaco = session.get(Farmaco, pf.farmaco_id)
        if farmaco:
            farmacos.append((farmaco, pf.ordem))
    
    return farmacos

def adicionar_farmaco_a_protocolo(session: Session, protocolo_id: int, farmaco_id: int, ordem: int = None) -> ProtocoloFarmaco:
    # Se não for passada a ordem, coloca no final
    if ordem is None:
        # Conta quantos fármacos já tem no protocolo
        stmt = select(ProtocoloFarmaco).where(ProtocoloFarmaco.protocolo_id == protocolo_id)
        itens = session.exec(stmt).all()
        ordem = len(itens) + 1
    
    pf = ProtocoloFarmaco(protocolo_id=protocolo_id, farmaco_id=farmaco_id, ordem=ordem)
    session.add(pf)
    session.commit()
    session.refresh(pf)
    return pf

def remover_farmaco_de_protocolo(session: Session, protocolo_id: int, farmaco_id: int) -> None:
    pf = session.get(ProtocoloFarmaco, (protocolo_id, farmaco_id))
    if pf:
        session.delete(pf)
        session.commit()

def deletar_protocolo(session: Session, protocolo_id: int) -> None:
    protocolo = session.get(Protocolo, protocolo_id)
    if protocolo:
        # Primeiro remove os ProtocoloFarmaco associados
        stmt = select(ProtocoloFarmaco).where(ProtocoloFarmaco.protocolo_id == protocolo_id)
        for pf in session.exec(stmt):
            session.delete(pf)
        session.delete(protocolo)
        session.commit()