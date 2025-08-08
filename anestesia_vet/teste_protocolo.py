from sqlmodel import create_engine, Session
from models.protocolo import Protocolo

def testar_protocolo():
    engine = create_engine("sqlite:///test.db")
    Protocolo.metadata.create_all(engine)
    
    with Session(engine) as session:
        protocolo = Protocolo(nome="Teste Simples")
        session.add(protocolo)
        session.commit()
        print(f"✅ Protocolo criado (ID: {protocolo.id})")

if __name__ == "__main__":
    testar_protocolo()