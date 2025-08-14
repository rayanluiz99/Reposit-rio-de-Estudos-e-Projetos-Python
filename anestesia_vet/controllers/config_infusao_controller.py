from sqlmodel import Session
from sqlmodel import select
from models.config_infusao import ConfigInfusao, TipoEquipo
from typing import Dict, Optional
import math

def criar_config_infusao(session: Session, peso_kg: float, 
                        volume_bolsa_ml: float = 20.0,
                        equipo_tipo: str = "macrogotas",
                        modo_calculo: str = "peso") -> ConfigInfusao:
    config = ConfigInfusao(
        peso_kg=peso_kg,
        volume_bolsa_ml=volume_bolsa_ml,
        equipo_tipo=TipoEquipo(equipo_tipo.lower()),
        modo_calculo=modo_calculo
    )
    session.add(config)
    session.commit()
    session.refresh(config)
    return config

def calcular_infusao_continua(
    peso_kg: float,
    dose: float,
    unidade_dose: str,
    concentracao: float,
    volume_bolsa_ml: float = None,
    equipo_tipo: str = "macrogotas",
    modo: str = "taxa"
) -> dict:
    # Converter unidades para padrão (mcg/kg/h)
    if "mg" in unidade_dose:
        dose_conv = dose * 1000  # mg para mcg
    else:
        dose_conv = dose
    
    # Se unidade for por minuto, converter para por hora
    if "/min" in unidade_dose:
        dose_conv *= 60
    
    # Converter concentração para mcg/ml
    concentracao_conv = concentracao * 1000  # mg/ml para mcg/ml
    
    if modo == "taxa":
        # Cálculo direto da taxa (ml/h) = (Dose * Peso) / Concentração
        taxa_ml_h = (dose_conv * peso_kg) / concentracao_conv
        
        # Calcular gotas/min
        fator = 20 if equipo_tipo == "macrogotas" else 60
        gotas_min = (taxa_ml_h * fator) / 60
        
        return {
            'taxa_ml_h': round(taxa_ml_h, 2),
            'gotas_min': round(gotas_min, 2),
            'instrucao': f"Configurar a bomba em {round(taxa_ml_h, 2)} ml/h"
        }
        
    else:  # modo == "solucao"
        if volume_bolsa_ml is None:
            raise ValueError("Volume da bolsa é obrigatório para o modo solução")
        
        # Cálculo correto: Volume do fármaco = (Dose * Volume da Bolsa) / Concentração
        volume_farmaco_ml = (dose_conv * volume_bolsa_ml) / concentracao_conv
        
        # Calcular a taxa separadamente
        taxa_ml_h = (dose_conv * peso_kg) / concentracao_conv
        
        # Garantir que não excede o volume da bolsa
        if volume_farmaco_ml > volume_bolsa_ml:
            volume_farmaco_ml = volume_bolsa_ml
            
        volume_dilente_ml = volume_bolsa_ml - volume_farmaco_ml
        
        # Calcular gotas/min
        fator = 20 if equipo_tipo == "macrogotas" else 60
        gotas_min = (taxa_ml_h * fator) / 60
        
        # Calcular duração
        duracao_h = volume_bolsa_ml / taxa_ml_h if taxa_ml_h > 0 else 0
        horas = int(duracao_h)
        minutos = int((duracao_h - horas) * 60)
        duracao_str = f"{horas}h {minutos}min" if minutos > 0 else f"{horas}h"
        
        return {
            'taxa_ml_h': round(taxa_ml_h, 2),
            'gotas_min': round(gotas_min, 2),
            'volume_farmaco_ml': round(volume_farmaco_ml, 2),
            'volume_dilente_ml': round(volume_dilente_ml, 2),
            'duracao_h': duracao_str
        }
def calcular_infusao_especifica(
    peso_kg: float, 
    dose_mg_kg_min: float,  # Alterado para mg/kg/min
    concentracao_mg_ml: float,  # Alterado para mg/ml
    volume_bolsa_ml: float = 20.0,
    equipo_tipo: str = "macrogotas",
    modo: str = "peso"
) -> dict:
    # Converter para unidades consistentes
    dose_mcg_kg_min = dose_mg_kg_min * 1000  # mg para mcg
    concentracao_mcg_ml = concentracao_mg_ml * 1000  # mg/ml para mcg/ml
    
    if modo == "peso":
        # Taxa em ml/h = (dose_mcg_kg_min * peso_kg * 60) / concentracao_mcg_ml
        taxa_ml_h = (dose_mcg_kg_min * peso_kg * 60) / concentracao_mcg_ml
        
        # Volume do fármaco = (dose_mg_kg_min * peso_kg * volume_bolsa_ml) / concentracao_mg_ml
        volume_farmaco_ml = (dose_mg_kg_min * peso_kg * volume_bolsa_ml) / concentracao_mg_ml
    else:
        # Taxa em ml/h = (dose_mg_kg_min * peso_kg * 60 * volume_bolsa_ml) / (concentracao_mg_ml * 1000)
        taxa_ml_h = (dose_mg_kg_min * peso_kg * 60 * volume_bolsa_ml) / (concentracao_mg_ml * 1000)
        
        # Volume do fármaco = volume_bolsa_ml (todo o volume)
        volume_farmaco_ml = volume_bolsa_ml
    
    # Garantir que não excede o volume da seringa
    if volume_farmaco_ml > volume_bolsa_ml:
        volume_farmaco_ml = volume_bolsa_ml
    
    volume_dilente_ml = volume_bolsa_ml - volume_farmaco_ml
    
    # Cálculo de gotas/min
    fator = 20 if equipo_tipo == "macrogotas" else 60
    gotas_min = (taxa_ml_h * fator) / 60
    
    # Calcular duração
    duracao_h = volume_bolsa_ml / taxa_ml_h if taxa_ml_h > 0 else 0
    horas = int(duracao_h)
    minutos = int((duracao_h - horas) * 60)
    duracao_str = f"{horas}h {minutos}min" if minutos > 0 else f"{horas}h"

    return {
        'taxa_ml_h': round(taxa_ml_h, 2),
        'volume_farmaco_ml': round(volume_farmaco_ml, 2),
        'volume_dilente_ml': round(volume_dilente_ml, 2),
        'gotas_min': round(gotas_min, 2),
        'duracao_h': duracao_str
    }
    
def calcular_taxas(config: ConfigInfusao) -> dict:
    """
    Calcula as taxas de infusão com base na configuração.
    Retorna um dicionário com os resultados.
    """
    # Implementação básica - ajuste conforme sua necessidade real
    return {
        'taxa_ml_h': 0,
        'gotas_min': 0,
        'duracao_h': "0h"
    }
def calcular_infusao_planilha(
    peso_kg: float,
    taxa_ml_kg_h: float,
    volume_bolsa_ml: float,
    equipo_tipo: str,
    dose_farmaco: float,
    unidade_dose: str,
    concentracao: float
) -> dict:
    # Calcular vazão (ml/h)
    vazao_ml_h = peso_kg * taxa_ml_kg_h
    
    # Calcular gotas/min
    fator = 20 if equipo_tipo == "macrogotas" else 60
    gotas_min = (vazao_ml_h * fator) / 60
    
    # Calcular duração (h)
    duracao_h = volume_bolsa_ml / vazao_ml_h if vazao_ml_h > 0 else 0
    
    # Converter unidade de dose para µg/kg/h
    if "mg" in unidade_dose:
        dose_conv = dose_farmaco * 1000  # mg para µg
    else:
        dose_conv = dose_farmaco
    
    if "/min" in unidade_dose:
        dose_conv *= 60  # converter min para hora
    
    # Calcular dose total (µg)
    dose_total_ug = dose_conv * peso_kg * duracao_h
    
    # Calcular volume do fármaco (ml)
    volume_farmaco_ml = dose_total_ug / (concentracao * 1000)  # concentração em mg/ml
    
    # Formatar duração
    horas = int(duracao_h)
    minutos = int((duracao_h - horas) * 60)
    duracao_str = f"{horas}h {minutos}min" if minutos > 0 else f"{horas}h"

    return {
        'vazao_ml_h': round(vazao_ml_h, 2),
        'gotas_min': round(gotas_min, 2),
        'duracao_h': duracao_str,
        'dose_total_ug': round(dose_total_ug, 2),
        'volume_farmaco_ml': round(volume_farmaco_ml, 4)  # 4 casas decimais para pequenos volumes
    }

def calcular_vazao(peso_kg: float, taxa_ml_kg_h: float) -> float:
    """Calcula a vazão em ml/h"""
    return peso_kg * taxa_ml_kg_h

def calcular_duracao(volume_bolsa_ml: float, vazao_ml_h: float) -> float:
    """Calcula a duração da infusão em horas"""
    return volume_bolsa_ml / vazao_ml_h if vazao_ml_h > 0 else 0

def calcular_gotas_min(vazao_ml_h: float, equipo_tipo: str) -> float:
    """Calcula gotas por minuto"""
    fator = 20 if equipo_tipo == "Macrogotas" else 60
    return (vazao_ml_h * fator) / 60

def calcular_dose_total(dose: float, unidade: str, peso_kg: float, duracao_h: float) -> float:
    """Calcula a dose total em mcg"""
    # Converter para mcg/kg/h se necessário
    if "mg" in unidade:
        dose_mcg = dose * 1000
    else:
        dose_mcg = dose
    
    if "/min" in unidade:
        dose_mcg_h = dose_mcg * 60
    else:
        dose_mcg_h = dose_mcg
    
    return dose_mcg_h * peso_kg * duracao_h

def calcular_volume_farmaco(dose_total_mcg: float, concentracao_mg_ml: float) -> float:
    """Calcula o volume do fármaco em ml"""
    concentracao_mcg_ml = concentracao_mg_ml * 1000
    return dose_total_mcg / concentracao_mcg_ml if concentracao_mcg_ml > 0 else 0