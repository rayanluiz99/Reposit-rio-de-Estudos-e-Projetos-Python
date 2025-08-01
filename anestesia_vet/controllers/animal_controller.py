from models.animal import Animal
from sqlmodel import Session
from database.engine import engine

def cadastrar_animal():
    nome = input("Nome do animal: ")
    especie = input("Espécie: ")
    raca = input("Raça: ")
    idade = input("Idade(em anos): ")
    peso = float(input("Peso (kg): "))
    
    animal = Animal(nome=nome,
                    especie=especie,
                    raca=raca,
                    idade=idade if idade else None,
                    peso_kg=peso
                    
    )
    with Session(engine) as session:
        session.add(animal)
        session.commit()
        print("Animal cadastradocom sucesso!")
        
        