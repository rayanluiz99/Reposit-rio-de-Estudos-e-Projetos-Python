from sqlmodel import Session
from models.config_infusao import TipoEquipo
from models.config_infusao import ConfigInfusao
from models.sessao import SessaoAnestesia

def criar_config_infusao(session: Session, peso_kg: float, 
                        volume_bolsa: float = 20.0,
                        equipo_tipo: str = "macrogotas") -> ConfigInfusao:
    """
    Cria uma nova configuração de infusão no banco de dados
    """
    config = ConfigInfusao(
        peso_kg=peso_kg,
        volume_bolsa_ml=volume_bolsa,
        equipo_tipo=TipoEquipo(equipo_tipo.lower())
    )
    
    session.add(config)
    session.commit()
    session.refresh(config)
    return config

def calcular_taxas(config: ConfigInfusao) -> dict:
    """
    Calcula todas as taxas baseadas na configuração de infusão
    Retorna um dicionário com:
    - taxa_ml_h
    - gotas_min
    - duracao_h
    - fator_equipo
    """
    taxa_ml_h = config.peso_kg * config.taxa_ml_kg_h
    fator = 20 if config.equipo_tipo == TipoEquipo.MACROGOTAS else 60
    gotas_min = (taxa_ml_h * fator) / 60
    duracao_h = config.volume_bolsa_ml / taxa_ml_h
    
    return {
        'taxa_ml_h': round(taxa_ml_h, 2),
        'gotas_min': round(gotas_min, 2),
        'duracao_h': round(duracao_h, 2),
        'fator_equipo': fator
    }