import os
from models.sessao import SessaoAnestesia, SessaoAvulsaAnestesia
from models.animal import Animal
from models.farmaco import Farmaco
from database.engine import engine
from sqlmodel import Session, select
from datetime import datetime

def registrar_sessao():
    with Session(engine) as session:
        id_animal_input = int(input("ID do animal (Pressione Enter para sessão avulsa): "))
        id_animal = int(id_animal_input) if id_animal_input.strip() != "" else None
        id_farmaco = int(input("ID do fármaco:  "))
        farmaco = session.exec(select(Farmaco).where(Farmaco.id == id_farmaco)).first()

        if not farmaco:
            print("Fármaco não encontrado.")
            return
        if id_animal:
            animal = session.exec(select(Animal).where(Animal.id == id_animal)).first()
            if not animal:
                print("animal não encontrado.")
            peso = animal.peso_kg
        else:
            peso = float(input("Peso do animal (kg): "))  

        dose_sugerida = (peso* farmaco.dose_mg_por_kg) / farmaco.concentracao_mg_ml
        print (f" Dose sugerida: {dose_sugerida:.2f} ml com base no peso informado.")

        dose_str = input("Dose utilizada (pressione Enter para aceitar a sugerida): ") 
        if dose_str.strip() == "":
            dose = dose_sugerida
        else:
            dose = float(dose_str)             
       
        obs = input("Observações(opcional): ")
    
    
        sessao = SessaoAnestesia(id_animal=id_animal,
                             id_farmaco=id_farmaco,
                             dose_utilizada_ml=dose,
                             observacoes=obs if obs else None
                    
        )
        
        session.add(sessao)
        session.commit()
        print("Sessão registrada com sucesso!")

def gerar_prescricao_txt():
    id_sessao = int(input("ID da sessão para prescrição: "))    

    with Session(engine) as session:
        sessao = session.get(SessaoAnestesia, id_sessao)
        if not sessao:
            print("Sessão não encontrada.")
            return    
        farmaco = session.get(Farmaco, sessao.id_farmaco)
        animal = session.get(Animal, sessao.id_animal) if sessao.id_animal else None

        nome_animal = animal.nome if animal else "Avulso"
        especie = animal.especie if animal else"Não informada"
        peso = f"{animal.peso_kg} kg" if animal else "Informado manualmente"
        dose_sugerida = (animal.peso_kg * farmaco.dose_mg_por_kg) / farmaco.concentracao_mg_ml if animal else "Desconhecida"

        conteudo = f"""---- PRESCRIÇÃO ANESTÉSICA -----
Animal: {nome_animal}
Espécie: {especie}
Peso: {peso}

Fármaco: {farmaco.nome}
Concentração: {farmaco.concentracao_mg_ml} mg/ml
Dose terapêutica:{farmaco.dose_mg_por_kg} mg/kg

Dose sugerida (Automática): {dose_sugerida if isinstance(dose_sugerida, str) else f"{dose_sugerida:.2f} mL"}
Dose utilizada: {sessao.dose_utilizada_ml:.2f} mL

Observações: {sessao.observacoes or "Nenhuma"}

-------------------------------
"""
        
        os.makedirs("prescricoes", exist_ok=True)
        nome_arquivo = f"prescricoes/prescricao_sessao_{id_sessao}.txt"

        with open(nome_arquivo, "w", encoding="utf-8") as file:
            file.write(conteudo)

        print(f"Prescrição gerada em: {nome_arquivo}")    

def registrar_sessao_avulsa():
    print("--- Registrar sessão avulsa ---")

    # Tratamento da espécie
    especie = None
    while True:
        opcao = input("Espécie (1 - Cão | 2 - Gato): ")
        if opcao == "1":
            especie = "Cão"
            break
        elif opcao == "2":
            especie = "Gato"
            break
        else:
            print("Opção inválida. Tente novamente.")

    nome = input("Nome do animal: ")
    peso = float(input("Peso do animal (kg): "))
    
    # Verificar fármacos disponíveis antes de pedir o ID
    with Session(engine) as session:
        farmacos = session.query(Farmaco).all()
        if not farmacos:
            print("Nenhum fármaco cadastrado! Cadastre fármacos primeiro.")
            return
            
        print("\nFármacos disponíveis:")
        for farmaco in farmacos:
            print(f"ID: {farmaco.id} - {farmaco.nome}")
        
        while True:
            try:
                id_farmaco = int(input("ID do fármaco: "))
                # Verificar se o ID existe
                if not any(f.id == id_farmaco for f in farmacos):
                    print("ID inválido. Digite um ID da lista acima.")
                    continue
                break
            except ValueError:
                print("Digite um número válido.")
    
    dose = float(input("Dose utilizada (ml): "))
    obs = input("Observações (opcional): ")

    # Criar a sessão com todos os campos
    with Session(engine) as session:
        sessao = SessaoAvulsaAnestesia(
            especie=especie,
            nome_animal=nome,
            peso_kg=peso,
            id_farmaco=id_farmaco,  # Incluindo o ID do fármaco
            dose_utilizada_ml=dose,  # Incluindo a dose
            observacoes=obs if obs else None,
            data=datetime.now()  # Adicionando data/hora atual
        )
        
        session.add(sessao)
        session.commit()
        print("Sessão avulsa registrada com sucesso!")
    