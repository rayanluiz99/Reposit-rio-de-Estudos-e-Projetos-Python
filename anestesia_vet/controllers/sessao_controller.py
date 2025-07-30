from models.sessao import SessaoAnestesia
from database.engine import engine
from sqlmodel import Session

def registrar_sessao():
    id_animal = int(input("ID do animal: "))
    id_farmaco = int(input("ID do fármaco:  "))
    dose = float(input("Dose utilizada (ml): "))
    obs = input("Observações(opcional): ")
    
    
    sessao = SessaoAnestesia(id_animal=id_animal,
                             id_farmaco=id_farmaco,
                             dose_utilizada_ml=dose,
                             observacoes=obs if obs else None
                    
    )
    with Session(engine) as session:
        session.add(sessao)
        session.commit()
        print("Sessão registrada com sucesso!")