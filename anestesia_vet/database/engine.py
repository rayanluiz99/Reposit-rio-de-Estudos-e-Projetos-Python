from sqlmodel import SQLModel, create_engine
from models.animal import Animal
from models.farmaco import Farmaco
from models.sessao import SessaoAnestesia, SessaoAvulsaAnestesia
from models.config_infusao import ConfigInfusao
from models.protocolo import Protocolo, ProtocoloFarmaco

sqlite_url = "sqlite:///database.db"
engine = create_engine(sqlite_url, echo=True)

# ... código existente ...

def criar_db_e_tabelas():
    SQLModel.metadata.create_all(engine)