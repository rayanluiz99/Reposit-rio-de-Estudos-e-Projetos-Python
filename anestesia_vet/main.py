from database.engine import engine, criar_db_e_tabelas
from sqlmodel import Session
from controllers.config_infusao_controller import (
    criar_config_infusao,
    calcular_taxas,
    menu_config_infusao
)

def testar_config_infusao():
    """Testa todas as combinações de configuração de infusão"""
    criar_db_e_tabelas()
    
    casos_teste = [
        # (peso, volume, equipo_tipo, taxa_esperada_ml_h, gotas_esperadas_min)
        (5.0, 20, "microgotas", 5.0, 5.0),       # 5 * 60 / 60 = 5
        (15.5, 250, "macrogotas", 15.5, 5.166),  # 15.5 * 20 / 60 ≈ 5.166
        (30.0, 500, "microgotas", 30.0, 30.0),   # 30 * 60 / 60 = 30
        (2.5, 50, "macrogotas", 2.5, 0.833)      # 2.5 * 20 / 60 ≈ 0.833
    ]

    with Session(engine) as session:
        for peso, volume, equipo, taxa_esp, gotas_esp in casos_teste:
            print(f"\n=== TESTE: {peso}kg, {volume}ml, {equipo} ===")
            
            config = criar_config_infusao(
                session=session,
                peso_kg=peso,
                volume_bolsa=volume,
                equipo_tipo=equipo
            )
            print(f"Config criada - ID: {config.id}")

            taxas = calcular_taxas(config)
            print("\nResultado dos cálculos:")
            print(f"Taxa (ml/h): {taxas['taxa_ml_h']:.2f} (esperado: {taxa_esp})")
            print(f"Gotas/min: {taxas['gotas_min']:.3f} (esperado: {gotas_esp})")
            print(f"Duração: {taxas['duracao_h']:.2f} horas")

            # Validações com margem de erro
            assert abs(taxas['taxa_ml_h'] - taxa_esp) < 0.01
            assert abs(taxas['gotas_min'] - gotas_esp) < 0.01
            assert abs(taxas['duracao_h'] - (volume / taxa_esp)) < 0.01
            
            print("✅ Validações passaram!")

        # Teste interativo
        print("\n=== TESTE MENU INTERATIVO ===")
        config_menu = menu_config_infusao(session, peso_padrao=10.0)
        print("\nConfiguração criada via menu:")
        print(f"Peso: {config_menu.peso_kg}kg")
        print(f"Volume: {config_menu.volume_bolsa_ml}ml")
        print(f"Equipo: {config_menu.equipo_tipo}")

if __name__ == "__main__":
    testar_config_infusao()

# def main():
#     with Session(engine) as session:
#         print("=== TESTE CONFIG INFUSÃO ===")
#         config = menu_config_infusao(session, peso_padrao=15.0)
#         print("\nConfiguração criada:")
#         print(f"- Peso: {config.peso_kg} kg")
#         print(f"- Volume: {config.volume_bolsa_ml} ml")
#         print(f"- Equipo: {config.equipo_tipo}")

# if __name__ == "__main__":
#     main()









# from database.engine import engine
# from database.engine import criar_db_e_tabelas
# from sqlmodel import Session
# from controllers.config_infusao_controller import *
# from controllers.farmaco_controller import importar_farmacos_csv


# from controllers.sessao_controller import registrar_sessao_avulsa
# from controllers.sessao_controller import registrar_sessao

# from controllers.config_infusao_controller import menu_config_infusao

# menu_config_infusao()

