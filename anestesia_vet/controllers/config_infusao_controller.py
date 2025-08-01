from sqlmodel import Session
from sqlmodel import select
from models.config_infusao import TipoEquipo
from models.config_infusao import ConfigInfusao
from models.sessao import SessaoAnestesia
from typing import Optional, List

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

def menu_config_infusao(session: Session, peso_padrao: float = None) -> ConfigInfusao:
    """Menu interativo para configuração de infusão contínua"""
    print("\n⚙️ Configuração de Infusão Contínua")
    
    # Peso do paciente
    while True:
        try:
            peso = float(input(f"Peso do paciente (kg) [{peso_padrao}]: ") or peso_padrao)
            if peso <= 0:
                raise ValueError
            break
        except (ValueError, TypeError):
            print("Digite um valor numérico positivo")

    # Volume da bolsa
    volumes = [20, 50, 100, 250, 500, 1000]
    print("\nVolumes disponíveis:")
    for i, vol in enumerate(volumes, 1):
        print(f"{i}. {vol} ml")
    
    while True:
        try:
            opcao = int(input("Selecione o volume: ")) - 1
            volume = volumes[opcao]
            break
        except (ValueError, IndexError):
            print(f"Digite um número entre 1 e {len(volumes)}")

    # Tipo de equipo
    while True:
        equipo = input("Tipo de equipo (micro/macro) [macro]: ").lower() or "macro"
        if equipo.startswith(('micro', 'macro')):
            break
        print("Digite 'micro' ou 'macro'")

    # Cria e retorna a configuração
    return criar_config_infusao(
        session=session,
        peso_kg=peso,
        volume_bolsa=volume,
        equipo_tipo="microgotas" if equipo.startswith('micro') else "macrogotas"
    )