from sqlmodel import SQLModel, create_engine
from models.animal import Animal
from models.farmaco import Farmaco
from models.sessao import SessaoAnestesia, SessaoAvulsaAnestesia
from models.config_infusao import ConfigInfusao
from models.protocolo import Protocolo, ProtocoloFarmaco  # Importar explicitamente

# Configuração do banco de dados
DATABASE_URL = "sqlite:///database.db"
engine = create_engine(DATABASE_URL, echo=True)

def create_db_and_tables():
    print("Criando tabelas no banco de dados...")
    
    # Criar tabelas na ordem correta
    SQLModel.metadata.create_all(engine, tables=[
        Animal.__table__,
        Farmaco.__table__,
        Protocolo.__table__,
        ProtocoloFarmaco.__table__,
        ConfigInfusao.__table__,
        SessaoAnestesia.__table__,
        SessaoAvulsaAnestesia.__table__,
    ])
    
    print("Tabelas criadas com sucesso!")

if __name__ == "__main__":
    create_db_and_tables()