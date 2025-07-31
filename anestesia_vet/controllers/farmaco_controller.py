import csv
from typing import Optional
from models.farmaco import Farmaco
from database.engine import engine
from sqlmodel import Session, select

def cadastrar_farmaco():
    """Cadastra um novo fármaco no sistema via terminal"""
    print("\n--- Cadastro de Fármaco ---")
    
    try:
        # Coleta de dados
        nome = input("Nome do fármaco: ").strip()
        while True:
            try:
                conc = float(input("Concentração (mg/ml ou µg/ml): "))
                break
            except ValueError:
                print("Digite um valor numérico válido.")
        
        while True:
            try:
                dose = float(input("Dose terapêutica: "))
                break
            except ValueError:
                print("Digite um valor numérico válido.")

        unidade = input("Unidade de dose (ex: mg/kg, µg/kg/min): ").strip()
        modo = input("Modo de uso (bolus/infusão contínua): ").strip().lower()
        
        volume = None
        volume_input = input("Volume da seringa (ml - opcional): ").strip()
        if volume_input:
            try:
                volume = float(volume_input)
            except ValueError:
                print("Volume inválido. Será definido como None.")

        # Validações básicas
        if not all([nome, unidade, modo]):
            print("Erro: Nome, unidade e modo são obrigatórios!")
            return

        if modo not in ["bolus", "infusão contínua"]:
            print("Erro: Modo de uso deve ser 'bolus' ou 'infusão contínua'")
            return

        # Criação do objeto
        farmaco = Farmaco(
            nome=nome,
            concentracao=conc,
            dose=dose,
            unidade_dose=unidade,
            modo_uso=modo,
            volume_seringa=volume,
            comentario=input("Comentários (opcional): ").strip() or None
        )

        # Persistência
        with Session(engine) as session:
            session.add(farmaco)
            session.commit()
            print(f"\nFármaco '{nome}' cadastrado com sucesso (ID: {farmaco.id})!")

    except Exception as e:
        print(f"\nErro ao cadastrar fármaco: {e}")

def importar_farmacos_csv():
    print("\n--- Importação de Fármacos ---")
    caminho_arquivo = input("Informe o caminho do arquivo CSV: ").strip()

    try:
        with open(caminho_arquivo, newline='', encoding='utf-8') as csvfile:
            leitor = csv.DictReader(csvfile)
            print(f"\nCampos detectados no CSV: {', '.join(leitor.fieldnames)}")

            # Verificação de campos obrigatórios
            campos_obrigatorios = {'nome', 'dose', 'concentracao', 'unidade_dose', 'modo_uso'}
            if not campos_obrigatorios.issubset(leitor.fieldnames):
                faltantes = campos_obrigatorios - set(leitor.fieldnames)
                print(f"\n🚨 Erro: Faltam campos obrigatórios: {', '.join(faltantes)}")
                return

            farmacos = []
            contador_linhas = 0
            
            for linha_num, linha in enumerate(leitor, 1):
                try:
                    # Pré-processamento
                    nome = linha["nome"].strip()
                    dose = float(linha["dose"].replace(',', '.'))
                    concentracao = float(linha["concentracao"].replace(',', '.'))
                    unidade = linha["unidade_dose"].strip()
                    
                    # Padronização do modo_uso
                    modo = linha["modo_uso"].strip().lower()
                    if 'infus' in modo or 'contin' in modo:
                        modo = 'infusão contínua'
                    else:
                        modo = 'bolus'

                    # Tratamento de campos opcionais
                    volume = float(linha["volume_seringa"].replace(',', '.')) if linha.get("volume_seringa") else None
                    comentario = linha.get("comentario", "").strip() or None

                    # Criação do objeto
                    farmaco = Farmaco(
                        nome=nome,
                        dose=dose,
                        concentracao=concentracao,
                        unidade_dose=unidade,
                        modo_uso=modo,
                        volume_seringa=volume,
                        comentario=comentario
                    )
                    farmacos.append(farmaco)
                    contador_linhas += 1
                    print(f"✅ Linha {linha_num}: {nome} - {modo}")

                except Exception as e:
                    print(f"⚠️ Erro na linha {linha_num}: {str(e)}")
                    continue

            if not farmacos:
                print("\nNenhum fármaco válido encontrado.")
                return

            # Resumo detalhado
            print(f"\n📊 Resumo da Importação:")
            print(f"Total de linhas processadas: {linha_num}")
            print(f"Fármacos válidos: {contador_linhas}")
            print(f"Erros: {linha_num - contador_linhas}")
            
            print("\n🔍 Amostra dos primeiros registros:")
            for f in farmacos[:3]:
                print(f" - {f.nome}: {f.dose} {f.unidade_dose} ({f.modo_uso})")

            # Confirmação final
            if input("\nConfirmar importação? (s/n): ").lower() != 's':
                print("Operação cancelada pelo usuário.")
                return

            # Persistência com tratamento de erros
            with Session(engine) as session:
                try:
                    session.add_all(farmacos)
                    session.commit()
                    print(f"\n🎉 {contador_linhas} fármacos importados com sucesso!")
                    print(f"⚠️ {linha_num - contador_linhas} linhas com problemas foram ignoradas")
                except Exception as e:
                    session.rollback()
                    print(f"\n❌ Erro ao salvar no banco de dados: {str(e)}")
                    print("Nenhum dado foi importado devido ao erro.")

    except FileNotFoundError:
        print("\nErro: Arquivo não encontrado. Verifique o caminho:")
        print(f"- {caminho_arquivo}")
    except Exception as e:
        print(f"\n❌ Erro inesperado: {str(e)}")
def exportar_farmacos_csv():
    """Exporta todos os fármacos para um arquivo CSV"""
    print("\n--- Exportação de Fármacos ---")
    caminho_arquivo = input("Informe o caminho para salvar o CSV: ").strip()

    try:
        with Session(engine) as session:
            farmacos = session.exec(select(Farmaco)).all()

            if not farmacos:
                print("Nenhum fármaco cadastrado para exportar.")
                return

            with open(caminho_arquivo, mode='w', newline='', encoding='utf-8') as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=[
                    'nome', 'dose', 'concentracao', 
                    'unidade_dose', 'modo_uso',
                    'volume_seringa', 'comentario'
                ])
                writer.writeheader()
                
                for f in farmacos:
                    writer.writerow({
                        'nome': f.nome,
                        'dose': f.dose,
                        'concentracao': f.concentracao,
                        'unidade_dose': f.unidade_dose,
                        'modo_uso': f.modo_uso,
                        'volume_seringa': f.volume_seringa or '',
                        'comentario': f.comentario or ''
                    })

            print(f"\n{len(farmacos)} fármacos exportados para: {caminho_arquivo}")

    except Exception as e:
        print(f"Erro na exportação: {e}")

def listar_farmacos():
    """Lista todos os fármacos cadastrados"""
    print("\n--- Fármacos Cadastrados ---")
    try:
        with Session(engine) as session:
            farmacos = session.exec(select(Farmaco)).all()
            
            if not farmacos:
                print("Nenhum fármaco cadastrado.")
                return
                
            for f in farmacos:
                print(f"ID: {f.id} | {f.nome}")
                print(f" - Dose: {f.dose} {f.unidade_dose} | Modo: {f.modo_uso}")
                print(f" - Conc: {f.concentracao}mg/ml | Seringa: {f.volume_seringa or 'N/A'}ml")
                print(f" - Comentários: {f.comentario or 'Nenhum'}\n")
                
    except Exception as e:
        print(f"Erro ao listar fármacos: {e}")