from database.engine import create_db
from controllers.animal_controller import cadastrar_animal
from controllers.farmaco_controller import cadastrar_farmaco
from controllers.farmaco_controller import importar_farmacos_csv
from controllers.sessao_controller import registrar_sessao


def menu():
    while True:
        print("\n--- Sistema de Anestesia Vet ---")
        print("1. Cadastrar Animal")
        print("2. Cadastrar Fármaco")
        print("3. Registrar Sessão Anestésica")
        print("4. Sair")

        opcao = input("Escolha uma opção: ")

        if opcao == "1":
            cadastrar_animal()
        elif opcao == "2":
            cadastrar_farmaco()
        elif opcao == "3":
            registrar_sessao()
        elif opcao == "4":
            print("Encerrando...")
            break
        else:
            print("Opção inválida.")

if __name__ == "__main__":
    create_db() 
    menu()