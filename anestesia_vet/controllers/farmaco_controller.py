from models.farmaco import Farmaco
from database.engine import engine
from sqlmodel import Session

def cadastrar_farmaco():
    nome = input("Nome do fármaco: ")
    conc = input("Concentração (mg/ml): ")
    volume = input("Volume total (ml): ")
    via = input("Via de administração(IV, IM, SC, etc): ")
    dose_mg_kg = float(input("Dose terapêutica (mg/kg): "))
    
    farmaco = Farmaco(nome=nome,
                      concentracao_mg_ml=conc,
                      volume_total_ml=volume,
                      via_administracao=via,
                      dose_mg_por_kg=dose_mg_kg
    )
    
    with Session(engine) as session:
        session.add(farmaco)
        session.commit()
        print("Fármaco cadastrado com sucesso!")