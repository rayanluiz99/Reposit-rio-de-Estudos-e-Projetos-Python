import csv
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

def importar_farmacos_csv():
    caminho = input("Informe o caminho do arquivo CSV: ").strip()

    try:
        with open(caminho, newline='', encoding='utf-8') as csvfile:
            leitor = csv.DictReader(csvfile)
            novos_farmacos = []

            for linha in leitor:
                nome = linha["nome"]
                concentracao = float(linha["concentracao_mg_ml"])
                dose = float(linha["dose_mg_kg"])
                
                farmaco = Farmaco(
                    nome=nome,
                    concentracao_mg_ml=concentracao,
                    dose_mg_por_kg=dose
                )
                novos_farmacos.append(farmaco)

            with Session(engine) as session:
                session.add_all(novos_farmacos)
                session.commit()

            print(f"{len(novos_farmacos)} fármacos importados com sucesso!")      
    except Exception as e:
        print(f"Erro ao importar: {e}")          