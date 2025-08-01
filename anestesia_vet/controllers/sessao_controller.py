import os
from models.sessao import SessaoAnestesia, SessaoAvulsaAnestesia
from models.animal import Animal
from models.farmaco import Farmaco
from database.engine import engine
from sqlmodel import Session, select
from datetime import datetime, timezone
from typing import Optional
from controllers.config_infusao_controller import criar_config_infusao, calcular_taxas

def registrar_sessao():
    """Registra uma nova sessão anestésica, com cálculo automático de dose"""
    with Session(engine) as session:
        try:
            # Tratamento do ID do animal
            id_animal_input = input("ID do animal (Pressione Enter para sessão avulsa): ").strip()
            id_animal = int(id_animal_input) if id_animal_input else None
            
            # Obter fármaco
            id_farmaco = int(input("ID do fármaco: "))
            farmaco = session.get(Farmaco, id_farmaco)
            if not farmaco:
                print("Fármaco não encontrado.")
                return
            
            # Validar modo de uso
            if farmaco.modo_uso not in ["bolus", "infusão contínua"]:
                print(f"Modo de uso inválido para {farmaco.nome}")
                return

            # Obter peso
            if id_animal:
                animal = session.get(Animal, id_animal)
                if not animal:
                    print("Animal não encontrado.")
                    return
                peso = animal.peso_kg
                config = criar_config_infusao(
                session=session,
                peso_kg=peso,  # Peso do animal obtido anteriormente
                volume_bolsa=250.0,  # Pode ser um input
                equipo_tipo="microgotas"  # Pode ser um input
            )
            
            # Adicionar à sessão
                sessao.config_infusao_id = config.id
                
                # Mostrar cálculos
                calculos = calcular_taxas(config)
                print(f"\nCálculos de Infusão:")
                print(f"Taxa: {calculos['taxa_ml_h']} ml/h")
                print(f"Gotas/min: {calculos['gotas_min']}")
                print(f"Duração estimada: {calculos['duracao_h']} horas")
            else:
                while True:
                    try:
                        peso = float(input("Peso do animal (kg): "))
                        break
                    except ValueError:
                        print("Digite um valor numérico válido.")

            # Cálculo da dose
            try:
                if farmaco.modo_uso == "bolus":
                    dose_sugerida = (peso * farmaco.dose) / farmaco.concentracao
                else:  # infusão contínua
                    multiplicador = 60 if "min" in farmaco.unidade_dose else 1
                    dose_sugerida = (peso * farmaco.dose * multiplicador) / farmaco.concentracao
                
                print(f"\nDose sugerida: {dose_sugerida:.2f}ml ({farmaco.unidade_dose})")

                # Obter dose utilizada
                while True:
                    dose_input = input(f"Dose utilizada (Enter para {dose_sugerida:.2f}ml): ").strip()
                    try:
                        dose = float(dose_input) if dose_input else dose_sugerida
                        break
                    except ValueError:
                        print("Digite um valor numérico válido.")

                # Registrar sessão
                sessao = SessaoAnestesia(
                    id_animal=id_animal,
                    id_farmaco=id_farmaco,
                    dose_utilizada_ml=dose,
                    observacoes=input("Observações (opcional): ") or None,
                    data=datetime.now(timezone.utc)
                )
                
                session.add(sessao)
                session.commit()
                print("\nSessão registrada com sucesso!")
                
            except Exception as e:
                print(f"\nErro no cálculo: {e}")
                session.rollback()

        except Exception as e:
            print(f"\nErro inesperado: {e}")

def gerar_prescricao_txt():
    """Gera um arquivo TXT com a prescrição anestésica"""
    try:
        id_sessao = int(input("ID da sessão para prescrição: "))    
        
        with Session(engine) as session:
            sessao = session.get(SessaoAnestesia, id_sessao)
            if not sessao:
                print("Sessão não encontrada.")
                return    
            
            farmaco = session.get(Farmaco, sessao.id_farmaco)
            animal = session.get(Animal, sessao.id_animal) if sessao.id_animal else None

            # Cálculo da dose sugerida para exibição
            dose_sugerida = "N/A"
            if animal:
                try:
                    if farmaco.modo_uso == "bolus":
                        dose_sugerida = (animal.peso_kg * farmaco.dose) / farmaco.concentracao
                    else:
                        multiplicador = 60 if "min" in farmaco.unidade_dose else 1
                        dose_sugerida = (animal.peso_kg * farmaco.dose * multiplicador) / farmaco.concentracao
                except:
                    pass

            # Conteúdo do relatório
            conteudo = f"""---- PRESCRIÇÃO ANESTÉSICA ----
Data: {sessao.data.strftime('%d/%m/%Y %H:%M')}
Animal: {animal.nome if animal else 'Avulso'}
Espécie: {animal.especie if animal else 'Não informada'}
Peso: {f"{animal.peso_kg}kg" if animal else 'Informado manualmente'}

FÁRMACO:
Nome: {farmaco.nome}
Concentração: {farmaco.concentracao}mg/ml
Dose: {farmaco.dose} {farmaco.unidade_dose}
Modo de uso: {farmaco.modo_uso.capitalize()}

DOSES:
Sugerida: {dose_sugerida if isinstance(dose_sugerida, str) else f"{dose_sugerida:.2f}ml"}
Utilizada: {sessao.dose_utilizada_ml:.2f}ml

Observações: {sessao.observacoes or "Nenhuma"}
----------------------------"""
            
            # Salvar arquivo
            os.makedirs("prescricoes", exist_ok=True)
            nome_arquivo = f"prescricoes/prescricao_{id_sessao}_{datetime.now().strftime('%Y%m%d')}.txt"

            with open(nome_arquivo, "w", encoding="utf-8") as file:
                file.write(conteudo)

            print(f"\nPrescrição gerada em: {nome_arquivo}")    

    except Exception as e:
        print(f"\nErro ao gerar prescrição: {e}")

def registrar_sessao_avulsa():
    """Registra uma sessão avulsa sem animal cadastrado"""
    print("\n--- Registrar sessão avulsa ---")
    
    try:
        # Espécie
        especie = None
        while especie not in ["Cão", "Gato"]:
            opcao = input("Espécie (1 - Cão | 2 - Gato): ")
            especie = "Cão" if opcao == "1" else "Gato" if opcao == "2" else None
            if not especie:
                print("Opção inválida. Tente novamente.")

        # Dados básicos
        nome = input("Nome do animal: ").strip() or "Não informado"
        
        while True:
            try:
                peso = float(input("Peso do animal (kg): "))
                break
            except ValueError:
                print("Digite um valor numérico válido.")

        # Seleção de fármaco
        with Session(engine) as session:
            farmacos = session.exec(select(Farmaco)).all()
            if not farmacos:
                print("Nenhum fármaco cadastrado! Cadastre fármacos primeiro.")
                return
                
            print("\nFármacos disponíveis:")
            for f in farmacos:
                print(f"ID: {f.id} - {f.nome} ({f.modo_uso}, {f.unidade_dose})")
            
            while True:
                try:
                    id_farmaco = int(input("\nID do fármaco: "))
                    if not any(f.id == id_farmaco for f in farmacos):
                        print("ID inválido. Digite um ID da lista acima.")
                        continue
                    break
                except ValueError:
                    print("Digite um número válido.")

            # Dose
            while True:
                try:
                    dose = float(input("Dose utilizada (ml): "))
                    break
                except ValueError:
                    print("Digite um valor numérico válido.")

            # Registrar
            sessao = SessaoAvulsaAnestesia(
                especie=especie,
                nome_animal=nome,
                peso_kg=peso,
                id_farmaco=id_farmaco,
                dose_utilizada_ml=dose,
                observacoes=input("Observações (opcional): ") or None,
                data=datetime.now(timezone.utc)
            )
            session.add(sessao)
            session.commit()
            print("\nSessão avulsa registrada com sucesso!")
            
    except Exception as e:
        print(f"\nErro ao registrar sessão: {e}")