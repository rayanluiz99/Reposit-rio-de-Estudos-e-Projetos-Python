from sqlmodel import SQLModel, create_engine

sqlite_file = "anestesia.db"
engine = create_engine(f"sqlite:///{sqlite_file}", echo=True)

def create_db():
    from models.animal import Animal
    from models.farmaco import Farmaco
    from models.sessao import SessaoAnestesia
    
    SQLModel.metadata.create_all(engine)

