# Importações de modelos
from models.animal import Animal
from models.farmaco import Farmaco
from models.config_infusao import ConfigInfusao, TipoEquipo
from models.sessao import SessaoAnestesia, SessaoAvulsaAnestesia

# Importações de controllers
from controllers.animal_controller import cadastrar_animal
from controllers.farmaco_controller import (
    cadastrar_farmaco,
    importar_farmacos_csv,
    exportar_farmacos_csv,
    listar_farmacos
)
from controllers.config_infusao_controller import (
    criar_config_infusao,
    calcular_taxas,
    menu_config_infusao
)
from controllers.sessao_controller import (
    registrar_sessao,
    registrar_sessao_avulsa,
    gerar_prescricao_txt
)

# Importações do banco de dados
from database.engine import engine

# Importações padrão
import os
import csv
from datetime import datetime
from typing import Optional

# Importações do tkinter
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from tkinter.scrolledtext import ScrolledText

# Importações do SQLModel
from sqlmodel import Session, select

class VetAnesthesiaApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Anestesia Veterinária - Cálculos de Infusão")
        self.root.geometry("1200x800")
        self.style = ttk.Style()
        self.configure_styles()
        
        # Layout principal
        self.main_frame = ttk.Frame(root)
        self.main_frame.pack(expand=True, fill='both', padx=10, pady=10)
        
        # Notebook (abas)
        self.notebook = ttk.Notebook(self.main_frame)
        self.notebook.pack(expand=True, fill='both')
        
        # Criar abas
        self.create_animal_tab()
        self.create_farmaco_tab()
        self.create_session_tab()
        self.create_infusion_tab()
        
        # Painel de fórmulas
        self.create_formulas_panel()
        
        # Carregar dados iniciais
        self.load_initial_data()

    def delete_farmaco(self):
        """Exclui um fármaco selecionado"""
        selected_item = self.farmaco_tree.selection()
        if not selected_item:
            messagebox.showerror("Erro", "Selecione um fármaco para excluir!")
            return
        
        farmaco_id = self.farmaco_tree.item(selected_item[0])['values'][0]
        farmaco_nome = self.farmaco_tree.item(selected_item[0])['values'][1]
        
        if not messagebox.askyesno("Confirmar", f"Tem certeza que deseja excluir o fármaco {farmaco_nome} (ID: {farmaco_id})?"):
            return
        
        try:
            with Session(engine) as session:
                farmaco = session.get(Farmaco, farmaco_id)
                if not farmaco:
                    messagebox.showerror("Erro", "Fármaco não encontrado!")
                    return
                
                session.delete(farmaco)
                session.commit()
                messagebox.showinfo("Sucesso", "Fármaco excluído com sucesso!")
                self.load_farmacos_tree()  # Atualiza a lista
                
        except Exception as e:
            messagebox.showerror("Erro", f"Falha ao excluir fármaco: {str(e)}")

    def configure_styles(self):
        """Configura os estilos visuais da aplicação"""
        self.style.configure('TFrame', background='#f0f0f0')
        self.style.configure('TLabel', background='#f0f0f0', font=('Arial', 10))
        self.style.configure('Header.TLabel', font=('Arial', 12, 'bold'))
        self.style.configure('TButton', font=('Arial', 10))
        self.style.configure('TNotebook.Tab', font=('Arial', 10, 'bold'))
        self.style.configure('Success.TLabel', foreground='green')
        self.style.configure('Error.TLabel', foreground='red')

    def load_initial_data(self):
        """Carrega dados iniciais do banco de dados"""
        with Session(engine) as session:
            # Carregar animais para combobox
            animais = session.exec(select(Animal)).all()
            self.animal_combobox['values'] = [f"{a.id} - {a.nome} ({a.especie})" for a in animais]
            
            # Carregar fármacos para combobox
            farmacos = session.exec(select(Farmaco)).all()
            self.farmaco_combobox['values'] = [f"{f.id} - {f.nome} ({f.modo_uso})" for f in farmacos]
            
            # Carregar lista completa de fármacos (Treeview)
            self.load_farmacos_tree()  # Agora chamando o método corretamente
    def create_animal_tab(self):
        """Cria a aba de cadastro de animais"""
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="🐾 Animais")
        
        # Formulário de cadastro
        form_frame = ttk.LabelFrame(frame, text="Cadastrar Novo Animal", padding=10)
        form_frame.pack(fill='x', pady=5)
        
        ttk.Label(form_frame, text="Nome:").grid(row=0, column=0, sticky='e', padx=5, pady=2)
        self.animal_nome = ttk.Entry(form_frame, width=30)
        self.animal_nome.grid(row=0, column=1, sticky='w', padx=5, pady=2)
        
        ttk.Label(form_frame, text="Espécie:").grid(row=1, column=0, sticky='e', padx=5, pady=2)
        self.animal_especie = ttk.Combobox(form_frame, values=["Cão", "Gato", "Equino", "Bovino", "Outro"], width=27)
        self.animal_especie.grid(row=1, column=1, sticky='w', padx=5, pady=2)
        
        ttk.Label(form_frame, text="Raça:").grid(row=2, column=0, sticky='e', padx=5, pady=2)
        self.animal_raca = ttk.Entry(form_frame, width=30)
        self.animal_raca.grid(row=2, column=1, sticky='w', padx=5, pady=2)
        
        ttk.Label(form_frame, text="Idade (anos):").grid(row=3, column=0, sticky='e', padx=5, pady=2)
        self.animal_idade = ttk.Entry(form_frame, width=30)
        self.animal_idade.grid(row=3, column=1, sticky='w', padx=5, pady=2)
        
        ttk.Label(form_frame, text="Peso (kg):").grid(row=4, column=0, sticky='e', padx=5, pady=2)
        self.animal_peso = ttk.Entry(form_frame, width=30)
        self.animal_peso.grid(row=4, column=1, sticky='w', padx=5, pady=2)
        
        btn_frame = ttk.Frame(form_frame)
        btn_frame.grid(row=5, column=0, columnspan=2, pady=10)
        ttk.Button(btn_frame, text="Cadastrar", command=self.register_animal).pack(side='left', padx=5)
        
        # Lista de animais cadastrados
        list_frame = ttk.LabelFrame(frame, text="Animais Cadastrados", padding=10)
        list_frame.pack(expand=True, fill='both', pady=5)
        
        columns = ("ID", "Nome", "Espécie", "Raça", "Idade", "Peso")
        self.animal_tree = ttk.Treeview(list_frame, columns=columns, show='headings', height=10)
        
        for col in columns:
            self.animal_tree.heading(col, text=col)
            self.animal_tree.column(col, width=100, anchor='center')
        
        self.animal_tree.pack(expand=True, fill='both')
        self.load_animals_list()

    def create_farmaco_tab(self):
        """Cria a aba de gerenciamento de fármacos com todas as funcionalidades"""
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="💊 Fármacos")
        
        # Frame principal com scrollbar
        main_frame = ttk.Frame(frame)
        main_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Treeview para exibir os fármacos
        columns = ("ID", "Nome", "Dose", "Concentração", "Unidade", "Modo Uso", "Volume Seringa", "Comentário")
        self.farmaco_tree = ttk.Treeview(main_frame, columns=columns, show='headings', height=15)
        
        # Configurar colunas
        self.farmaco_tree.heading("ID", text="ID")
        self.farmaco_tree.heading("Nome", text="Nome")
        self.farmaco_tree.heading("Dose", text="Dose")
        self.farmaco_tree.heading("Concentração", text="Conc. (mg/ml)")
        self.farmaco_tree.heading("Unidade", text="Unidade")
        self.farmaco_tree.heading("Modo Uso", text="Modo de Uso")
        self.farmaco_tree.heading("Volume Seringa", text="Vol. Seringa (ml)")
        self.farmaco_tree.heading("Comentário", text="Comentários")
        
        # Ajustar largura das colunas
        self.farmaco_tree.column("ID", width=50, anchor='center')
        self.farmaco_tree.column("Nome", width=150)
        self.farmaco_tree.column("Dose", width=80, anchor='center')
        self.farmaco_tree.column("Concentração", width=100, anchor='center')
        self.farmaco_tree.column("Unidade", width=100, anchor='center')
        self.farmaco_tree.column("Modo Uso", width=100, anchor='center')
        self.farmaco_tree.column("Volume Seringa", width=100, anchor='center')
        self.farmaco_tree.column("Comentário", width=200)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(main_frame, orient='vertical', command=self.farmaco_tree.yview)
        self.farmaco_tree.configure(yscrollcommand=scrollbar.set)
        
        # Layout
        self.farmaco_tree.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
        
        # Frame de botões com todas as funcionalidades
        btn_frame = ttk.Frame(frame, padding=10)
        btn_frame.pack(fill='x')
        
        ttk.Button(btn_frame, text="Atualizar Lista", command=self.load_farmacos_tree).pack(side='left', padx=5)
        ttk.Button(btn_frame, text="Cadastrar Novo", command=self.register_farmaco).pack(side='left', padx=5)
        ttk.Button(btn_frame, text="Importar CSV", command=self.import_farmacos_csv).pack(side='left', padx=5)
        ttk.Button(btn_frame, text="Exportar CSV", command=self.export_farmacos_csv).pack(side='left', padx=5)
        ttk.Button(btn_frame, text="Excluir Selecionado", command=self.delete_farmaco).pack(side='left', padx=5)
        
        # Carregar dados inicialmente
        self.load_farmacos_tree()

    def register_farmaco(self):
        """Janela para cadastrar novo fármaco"""
        cadastro_window = tk.Toplevel(self.root)
        cadastro_window.title("Cadastrar Novo Fármaco")
        cadastro_window.geometry("400x400")
        
        # Variáveis
        nome = tk.StringVar()
        dose = tk.DoubleVar()
        concentracao = tk.DoubleVar()
        unidade = tk.StringVar()
        modo = tk.StringVar()
        volume = tk.DoubleVar()
        comentario = tk.StringVar()
        
        # Formulário
        ttk.Label(cadastro_window, text="Nome:").pack()
        ttk.Entry(cadastro_window, textvariable=nome).pack()
        
        ttk.Label(cadastro_window, text="Dose:").pack()
        ttk.Entry(cadastro_window, textvariable=dose).pack()
        
        ttk.Label(cadastro_window, text="Concentração (mg/ml):").pack()
        ttk.Entry(cadastro_window, textvariable=concentracao).pack()
        
        ttk.Label(cadastro_window, text="Unidade de dose:").pack()
        ttk.Combobox(cadastro_window, textvariable=unidade, values=["mg/kg", "µg/kg", "mg/kg/min", "µg/kg/min"]).pack()
        
        ttk.Label(cadastro_window, text="Modo de uso:").pack()
        ttk.Combobox(cadastro_window, textvariable=modo, values=["bolus", "infusão contínua"]).pack()
        
        ttk.Label(cadastro_window, text="Volume da seringa (ml - opcional):").pack()
        ttk.Entry(cadastro_window, textvariable=volume).pack()
        
        ttk.Label(cadastro_window, text="Comentários (opcional):").pack()
        ttk.Entry(cadastro_window, textvariable=comentario).pack()
        
        def salvar_farmaco():
            """Salva o novo fármaco no banco de dados"""
            try:
                farmaco = Farmaco(
                    nome=nome.get(),
                    dose=dose.get(),
                    concentracao=concentracao.get(),
                    unidade_dose=unidade.get(),
                    modo_uso=modo.get(),
                    volume_seringa=volume.get() if volume.get() != 0 else None,
                    comentario=comentario.get() or None
                )
                
                with Session(engine) as session:
                    session.add(farmaco)
                    session.commit()
                    messagebox.showinfo("Sucesso", "Fármaco cadastrado com sucesso!")
                    cadastro_window.destroy()
                    self.load_farmacos_tree()  # Atualiza a lista
                
            except Exception as e:
                messagebox.showerror("Erro", f"Falha ao cadastrar: {str(e)}")
        
        ttk.Button(cadastro_window, text="Salvar", command=salvar_farmaco).pack(pady=10)

    def import_farmacos_csv(self):
        """Importa fármacos de arquivo CSV"""
        filepath = filedialog.askopenfilename(
            title="Selecione o arquivo CSV",
            filetypes=(("CSV files", "*.csv"), ("All files", "*.*"))
        )
        
        if not filepath:
            return
            
        try:
            with open(filepath, newline='', encoding='utf-8') as csvfile:
                reader = csv.DictReader(csvfile)
                farmacos = []
                
                for row in reader:
                    try:
                        farmaco = Farmaco(
                            nome=row['nome'].strip(),
                            dose=float(row['dose'].replace(',', '.')),
                            concentracao=float(row['concentracao'].replace(',', '.')),
                            unidade_dose=row['unidade_dose'].strip(),
                            modo_uso=row['modo_uso'].strip().lower(),
                            volume_seringa=float(row['volume_seringa'].replace(',', '.')) if row.get('volume_seringa') else None,
                            comentario=row.get('comentario', '').strip() or None
                        )
                        farmacos.append(farmaco)
                    except Exception as e:
                        print(f"Erro na linha: {row}. Erro: {str(e)}")
                        continue
                
                if not farmacos:
                    messagebox.showwarning("Aviso", "Nenhum fármaco válido encontrado no arquivo.")
                    return
                
                if messagebox.askyesno("Confirmar", f"Importar {len(farmacos)} fármacos?"):
                    with Session(engine) as session:
                        session.add_all(farmacos)
                        session.commit()
                        messagebox.showinfo("Sucesso", f"{len(farmacos)} fármacos importados!")
                        self.load_farmacos_tree()
                        
        except Exception as e:
            messagebox.showerror("Erro", f"Falha ao importar: {str(e)}")

    def export_farmacos_csv(self):
        """Exporta fármacos para arquivo CSV"""
        filepath = filedialog.asksaveasfilename(
            title="Salvar como CSV",
            defaultextension=".csv",
            filetypes=(("CSV files", "*.csv"), ("All files", "*.*")))
        
        if not filepath:
            return
            
        try:
            with Session(engine) as session:
                farmacos = session.exec(select(Farmaco)).all()
                
                if not farmacos:
                    messagebox.showwarning("Aviso", "Nenhum fármaco cadastrado para exportar.")
                    return
                
                with open(filepath, mode='w', newline='', encoding='utf-8') as csvfile:
                    writer = csv.DictWriter(csvfile, fieldnames=[
                        'nome', 'dose', 'concentracao', 'unidade_dose', 
                        'modo_uso', 'volume_seringa', 'comentario'
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
                
                messagebox.showinfo("Sucesso", f"{len(farmacos)} fármacos exportados para:\n{filepath}")
                
        except Exception as e:
            messagebox.showerror("Erro", f"Falha ao exportar: {str(e)}")
    def load_farmacos_tree(self):
        """Carrega os fármacos no Treeview"""
        with Session(engine) as session:
            farmacos = session.exec(select(Farmaco).order_by(Farmaco.nome)).all()
            
            # Limpar treeview
            for item in self.farmaco_tree.get_children():
                self.farmaco_tree.delete(item)
                
            # Adicionar novos itens
            for f in farmacos:
                self.farmaco_tree.insert('', 'end', values=(
                    f.id,
                    f.nome,
                    f.dose,
                    f.concentracao,
                    f.unidade_dose,
                    f.modo_uso,
                    f.volume_seringa if f.volume_seringa else "N/A",
                    f.comentario if f.comentario else "Nenhum"
                ))

    def load_farmacos_list(self):
        """Carrega a lista completa de fármacos no TreeView"""
        with Session(engine) as session:
            farmacos = session.exec(select(Farmaco).order_by(Farmaco.nome)).all()
            
            # Limpar treeview
            for item in self.farmaco_tree.get_children():
                self.farmaco_tree.delete(item)
                
            # Adicionar novos itens
            for farmaco in farmacos:
                self.farmaco_tree.insert('', 'end', values=(
                    farmaco.id,
                    farmaco.nome,
                    farmaco.dose,
                    farmaco.concentracao,
                    farmaco.unidade_dose,
                    farmaco.modo_uso,
                    farmaco.volume_seringa if farmaco.volume_seringa else "N/A",
                    farmaco.comentario if farmaco.comentario else "Nenhum"
            ))

    def create_session_tab(self):
        """Cria a aba de registro de sessões anestésicas"""
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="📋 Sessões")
        
        # Formulário de nova sessão
        form_frame = ttk.LabelFrame(frame, text="Nova Sessão Anestésica", padding=10)
        form_frame.pack(fill='x', pady=5)
        
        # Seleção de animal
        ttk.Label(form_frame, text="Animal:").grid(row=0, column=0, sticky='e', padx=5, pady=2)
        self.animal_combobox = ttk.Combobox(form_frame, state='readonly', width=40)
        self.animal_combobox.grid(row=0, column=1, sticky='w', padx=5, pady=2)
        ttk.Button(form_frame, text="Sessão Avulsa", command=self.open_avulsa_session).grid(row=0, column=2, padx=5)
        
        # Peso (atualizado quando seleciona animal)
        ttk.Label(form_frame, text="Peso (kg):").grid(row=1, column=0, sticky='e', padx=5, pady=2)
        self.session_peso = ttk.Label(form_frame, text="", width=10)
        self.session_peso.grid(row=1, column=1, sticky='w', padx=5, pady=2)
        
        # Seleção de fármaco
        ttk.Label(form_frame, text="Fármaco:").grid(row=2, column=0, sticky='e', padx=5, pady=2)
        self.farmaco_combobox = ttk.Combobox(form_frame, state='readonly', width=40)
        self.farmaco_combobox.grid(row=2, column=1, sticky='w', padx=5, pady=2)
        self.farmaco_combobox.bind('<<ComboboxSelected>>', self.update_farmaco_info)
        
        # Info do fármaco
        ttk.Label(form_frame, text="Dose:").grid(row=3, column=0, sticky='e', padx=5, pady=2)
        self.farmaco_dose = ttk.Label(form_frame, text="")
        self.farmaco_dose.grid(row=3, column=1, sticky='w', padx=5, pady=2)
        
        ttk.Label(form_frame, text="Modo de uso:").grid(row=4, column=0, sticky='e', padx=5, pady=2)
        self.farmaco_modo = ttk.Label(form_frame, text="")
        self.farmaco_modo.grid(row=4, column=1, sticky='w', padx=5, pady=2)
        
        # Dose calculada
        ttk.Label(form_frame, text="Dose calculada:").grid(row=5, column=0, sticky='e', padx=5, pady=2)
        self.dose_calculada = ttk.Label(form_frame, text="", style='Header.TLabel')
        self.dose_calculada.grid(row=5, column=1, sticky='w', padx=5, pady=2)
        
        # Observações
        ttk.Label(form_frame, text="Observações:").grid(row=6, column=0, sticky='ne', padx=5, pady=2)
        self.session_obs = tk.Text(form_frame, height=3, width=30)
        self.session_obs.grid(row=6, column=1, sticky='w', padx=5, pady=2)
        
        # Botões
        btn_frame = ttk.Frame(form_frame)
        btn_frame.grid(row=7, column=0, columnspan=3, pady=10)
        
        ttk.Button(btn_frame, text="Calcular Dose", command=self.calculate_dose).pack(side='left', padx=5)
        ttk.Button(btn_frame, text="Registrar Sessão", command=self.register_session).pack(side='left', padx=5)
        ttk.Button(btn_frame, text="Gerar Prescrição", command=self.generate_prescription).pack(side='left', padx=5)
        
        # Lista de sessões
        list_frame = ttk.LabelFrame(frame, text="Sessões Registradas", padding=10)
        list_frame.pack(expand=True, fill='both', pady=5)
        
        columns = ("ID", "Animal", "Fármaco", "Dose (ml)", "Data")
        self.session_tree = ttk.Treeview(list_frame, columns=columns, show='headings', height=10)
        
        for col in columns:
            self.session_tree.heading(col, text=col)
            self.session_tree.column(col, width=120, anchor='center')
        
        self.session_tree.pack(expand=True, fill='both')
        self.load_sessions_list()

    def create_infusion_tab(self):
        """Cria a aba de configuração de infusão contínua"""
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="💉 Infusão")
        
        # Formulário de configuração
        form_frame = ttk.LabelFrame(frame, text="Configuração de Infusão Contínua", padding=10)
        form_frame.pack(fill='x', pady=5)
        
        # Peso do paciente
        ttk.Label(form_frame, text="Peso do paciente (kg):").grid(row=0, column=0, sticky='e', padx=5, pady=2)
        self.infusion_peso = ttk.Entry(form_frame, width=10)
        self.infusion_peso.grid(row=0, column=1, sticky='w', padx=5, pady=2)
        
        # Volume da bolsa (menu suspenso)
        ttk.Label(form_frame, text="Volume da bolsa (ml):").grid(row=1, column=0, sticky='e', padx=5, pady=2)
        self.infusion_volume = ttk.Combobox(form_frame, values=[20, 50, 100, 250, 500, 1000], width=8)
        self.infusion_volume.grid(row=1, column=1, sticky='w', padx=5, pady=2)
        self.infusion_volume.current(0)  # Seleciona o primeiro valor por padrão
        
        # Tipo de equipo (menu suspenso)
        ttk.Label(form_frame, text="Tipo de equipo:").grid(row=2, column=0, sticky='e', padx=5, pady=2)
        self.infusion_equipo = ttk.Combobox(form_frame, values=["Macrogotas (20 gts/ml)", "Microgotas (60 gts/ml)"], width=20)
        self.infusion_equipo.grid(row=2, column=1, sticky='w', padx=5, pady=2)
        self.infusion_equipo.current(0)
        
        # Taxa de infusão
        ttk.Label(form_frame, text="Taxa (ml/kg/h):").grid(row=3, column=0, sticky='e', padx=5, pady=2)
        self.infusion_taxa = ttk.Entry(form_frame, width=10)
        self.infusion_taxa.grid(row=3, column=1, sticky='w', padx=5, pady=2)
        
        # Botão de cálculo
        btn_frame = ttk.Frame(form_frame)
        btn_frame.grid(row=4, column=0, columnspan=2, pady=10)
        ttk.Button(btn_frame, text="Calcular Infusão", command=self.calculate_infusion).pack(side='left', padx=5)
        
        # Resultados
        results_frame = ttk.LabelFrame(form_frame, text="Resultados", padding=10)
        results_frame.grid(row=5, column=0, columnspan=2, sticky='ew', pady=5)
        
        ttk.Label(results_frame, text="Taxa de infusão:").grid(row=0, column=0, sticky='e', padx=5, pady=2)
        self.result_taxa = ttk.Label(results_frame, text="", style='Header.TLabel')
        self.result_taxa.grid(row=0, column=1, sticky='w', padx=5, pady=2)
        
        ttk.Label(results_frame, text="Gotas/min:").grid(row=1, column=0, sticky='e', padx=5, pady=2)
        self.result_gotas = ttk.Label(results_frame, text="")
        self.result_gotas.grid(row=1, column=1, sticky='w', padx=5, pady=2)
        
        ttk.Label(results_frame, text="Duração estimada:").grid(row=2, column=0, sticky='e', padx=5, pady=2)
        self.result_duracao = ttk.Label(results_frame, text="")
        self.result_duracao.grid(row=2, column=1, sticky='w', padx=5, pady=2)

    def create_formulas_panel(self):
        """Cria o painel de fórmulas no canto inferior direito"""
        formula_frame = ttk.LabelFrame(self.main_frame, text="Fórmulas Utilizadas", padding=10)
        formula_frame.place(relx=0.75, rely=0.7, relwidth=0.25, relheight=0.3, anchor='nw')
        
        self.formula_text = tk.Text(formula_frame, wrap=tk.WORD, height=10, width=40)
        self.formula_text.pack(fill='both', expand=True)
        
        formulas = """
        [Cálculo de Dose]
        Dose (mg) = Peso (kg) × Dose recomendada (mg/kg)
        
        [Taxa de Infusão]
        Taxa (ml/h) = (Dose (μg/kg/min) × Peso (kg) × 60) / Concentração (μg/ml)
        
        [Gotas/min]
        Gotas/min = (Taxa (ml/h) × Fator equipo) / 60
        (Macrogotas: 20 gts/ml, Microgotas: 60 gts/ml)
        
        [Duração da Infusão]
        Duração (h) = Volume da bolsa (ml) / Taxa (ml/h)
        """
        self.formula_text.insert(tk.END, formulas)
        self.formula_text.config(state=tk.DISABLED)

    # Métodos de controle (a serem implementados)
    def register_animal(self):
        """Cadastra um novo animal no sistema"""
        try:
            animal = Animal(
                nome=self.animal_nome.get(),
                especie=self.animal_especie.get(),
                raca=self.animal_raca.get(),
                idade=float(self.animal_idade.get()) if self.animal_idade.get() else None,
                peso_kg=float(self.animal_peso.get())
            )
            
            with Session(engine) as session:
                session.add(animal)
                session.commit()
                messagebox.showinfo("Sucesso", f"Animal {animal.nome} cadastrado com sucesso!")
                self.load_animals_list()
                self.load_initial_data()  # Atualiza comboboxes
                
                # Limpar campos
                self.animal_nome.delete(0, tk.END)
                self.animal_especie.set('')
                self.animal_raca.delete(0, tk.END)
                self.animal_idade.delete(0, tk.END)
                self.animal_peso.delete(0, tk.END)
                
        except Exception as e:
            messagebox.showerror("Erro", f"Falha ao cadastrar animal: {str(e)}")

    def load_animals_list(self):
        """Carrega a lista de animais no TreeView"""
        with Session(engine) as session:
            animais = session.exec(select(Animal)).all()
            
            # Limpar treeview
            for item in self.animal_tree.get_children():
                self.animal_tree.delete(item)
                
            # Adicionar novos itens
            for animal in animais:
                self.animal_tree.insert('', 'end', values=(
                    animal.id,
                    animal.nome,
                    animal.especie,
                    animal.raca,
                    animal.idade if animal.idade else 'N/A',
                    f"{animal.peso_kg} kg"
                ))

    def register_farmaco(self):
        """Janela para cadastrar novo fármaco"""
        cadastro_window = tk.Toplevel(self.root)
        cadastro_window.title("Cadastrar Novo Fármaco")
        cadastro_window.geometry("400x500")
        
        # Frame principal
        main_frame = ttk.Frame(cadastro_window, padding=10)
        main_frame.pack(fill='both', expand=True)
        
        # Variáveis
        nome_var = tk.StringVar()
        dose_var = tk.StringVar()
        conc_var = tk.StringVar()
        unidade_var = tk.StringVar()
        modo_var = tk.StringVar()
        volume_var = tk.StringVar()
        comentario_var = tk.StringVar()
        
        # Formulário
        ttk.Label(main_frame, text="Nome do fármaco:").grid(row=0, column=0, sticky='w', pady=2)
        nome_entry = ttk.Entry(main_frame, textvariable=nome_var)
        nome_entry.grid(row=0, column=1, sticky='we', pady=2)
        
        ttk.Label(main_frame, text="Dose terapêutica:").grid(row=1, column=0, sticky='w', pady=2)
        dose_entry = ttk.Entry(main_frame, textvariable=dose_var)
        dose_entry.grid(row=1, column=1, sticky='we', pady=2)
        
        ttk.Label(main_frame, text="Concentração (mg/ml):").grid(row=2, column=0, sticky='w', pady=2)
        conc_entry = ttk.Entry(main_frame, textvariable=conc_var)
        conc_entry.grid(row=2, column=1, sticky='we', pady=2)
        
        ttk.Label(main_frame, text="Unidade de dose:").grid(row=3, column=0, sticky='w', pady=2)
        unidade_cb = ttk.Combobox(main_frame, textvariable=unidade_var, 
                                values=["mg/kg", "µg/kg", "mg/kg/min", "µg/kg/min"])
        unidade_cb.grid(row=3, column=1, sticky='we', pady=2)
        
        ttk.Label(main_frame, text="Modo de uso:").grid(row=4, column=0, sticky='w', pady=2)
        modo_cb = ttk.Combobox(main_frame, textvariable=modo_var, 
                            values=["bolus", "infusão contínua"])
        modo_cb.grid(row=4, column=1, sticky='we', pady=2)
        
        ttk.Label(main_frame, text="Volume seringa (ml - opcional):").grid(row=5, column=0, sticky='w', pady=2)
        volume_entry = ttk.Entry(main_frame, textvariable=volume_var)
        volume_entry.grid(row=5, column=1, sticky='we', pady=2)
        
        ttk.Label(main_frame, text="Comentários (opcional):").grid(row=6, column=0, sticky='nw', pady=2)
        comentario_entry = tk.Text(main_frame, height=4, width=30)
        comentario_entry.grid(row=6, column=1, sticky='we', pady=2)
        
        def salvar_farmaco():
            try:
                farmaco = Farmaco(
                    nome=nome_var.get(),
                    dose=float(dose_var.get()),
                    concentracao=float(conc_var.get()),
                    unidade_dose=unidade_var.get(),
                    modo_uso=modo_var.get(),
                    volume_seringa=float(volume_var.get()) if volume_var.get() else None,
                    comentario=comentario_entry.get("1.0", tk.END).strip() or None
                )
                
                with Session(engine) as session:
                    session.add(farmaco)
                    session.commit()
                    messagebox.showinfo("Sucesso", "Fármaco cadastrado com sucesso!")
                    cadastro_window.destroy()
                    self.load_farmacos_tree()  # Atualiza a lista de fármacos
                
            except ValueError:
                messagebox.showerror("Erro", "Digite valores numéricos válidos para dose e concentração!")
            except Exception as e:
                messagebox.showerror("Erro", f"Falha ao cadastrar fármaco: {str(e)}")
        
        # Frame de botões
        btn_frame = ttk.Frame(main_frame)
        btn_frame.grid(row=7, column=0, columnspan=2, pady=10)
        
        ttk.Button(btn_frame, text="Salvar", command=salvar_farmaco).pack(side='left', padx=5)
        ttk.Button(btn_frame, text="Cancelar", command=cadastro_window.destroy).pack(side='left', padx=5)
        
        # Configurar grid
        main_frame.columnconfigure(1, weight=1)
        nome_entry.focus()

    def load_farmacos_list(self):
        """Carrega a lista de fármacos no ListBox"""
        with Session(engine) as session:
            farmacos = session.exec(select(Farmaco)).all()
            
            self.load_farmacos_tree.delete(0, tk.END)
            for farmaco in farmacos:
                self.load_farmacos_tree.insert(tk.END, f"{farmaco.id} - {farmaco.nome} ({farmaco.modo_uso})")

    def import_farmacos_csv(self):
        """Importa fármacos de um arquivo CSV"""
        filepath = filedialog.askopenfilename(
            title="Selecione o arquivo CSV",
            filetypes=(("CSV files", "*.csv"), ("All files", "*.*"))
        )
        
        if not filepath:
            return
            
        try:
            with open(filepath, newline='', encoding='utf-8') as csvfile:
                reader = csv.DictReader(csvfile)
                farmacos = []
                
                for row in reader:
                    try:
                        # Converter modo de uso para padrão
                        modo = row['modo_uso'].strip().lower()
                        if 'infus' in modo or 'contin' in modo:
                            modo = 'infusão contínua'
                        else:
                            modo = 'bolus'
                            
                        farmaco = Farmaco(
                            nome=row['nome'].strip(),
                            concentracao=float(row['concentracao'].replace(',', '.')),
                            dose=float(row['dose'].replace(',', '.')),
                            unidade_dose=row['unidade_dose'].strip(),
                            modo_uso=modo,
                            volume_seringa=float(row['volume_seringa'].replace(',', '.')) if row.get('volume_seringa') else None,
                            comentario=row.get('comentario', '').strip() or None
                        )
                        farmacos.append(farmaco)
                    except Exception as e:
                        print(f"Erro na linha: {row}. Erro: {str(e)}")
                        continue
                
                if not farmacos:
                    messagebox.showwarning("Aviso", "Nenhum fármaco válido encontrado no arquivo.")
                    return
                
                # Confirmar importação
                if messagebox.askyesno("Confirmar", f"Importar {len(farmacos)} fármacos?"):
                    with Session(engine) as session:
                        session.add_all(farmacos)
                        session.commit()
                        messagebox.showinfo("Sucesso", f"{len(farmacos)} fármacos importados com sucesso!")
                        self.load_farmacos_list()
                        self.load_initial_data()
                        
        except Exception as e:
            messagebox.showerror("Erro", f"Falha ao importar arquivo: {str(e)}")

    def export_farmacos_csv(self):
        """Exporta fármacos para um arquivo CSV"""
        filepath = filedialog.asksaveasfilename(
            title="Salvar como CSV",
            defaultextension=".csv",
            filetypes=(("CSV files", "*.csv"), ("All files", "*.*"))
        )
        
        if not filepath:
            return
            
        try:
            with Session(engine) as session:
                farmacos = session.exec(select(Farmaco)).all()
                
                if not farmacos:
                    messagebox.showwarning("Aviso", "Nenhum fármaco cadastrado para exportar.")
                    return
                
                with open(filepath, mode='w', newline='', encoding='utf-8') as csvfile:
                    writer = csv.DictWriter(csvfile, fieldnames=[
                        'nome', 'dose', 'concentracao', 'unidade_dose', 
                        'modo_uso', 'volume_seringa', 'comentario'
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
                
                messagebox.showinfo("Sucesso", f"{len(farmacos)} fármacos exportados para:\n{filepath}")
                
        except Exception as e:
            messagebox.showerror("Erro", f"Falha ao exportar: {str(e)}")

    def open_avulsa_session(self):
        """Abre a janela de sessão avulsa com cálculo de dose"""
        avulsa_window = tk.Toplevel(self.root)
        avulsa_window.title("Sessão Avulsa")
        avulsa_window.geometry("500x450")
        
        # Frame principal
        main_frame = ttk.Frame(avulsa_window, padding=10)
        main_frame.pack(fill='both', expand=True)
        
        # Variáveis
        dose_calculada = tk.StringVar(value="")
        farmaco_selecionado = None
        
        # Widgets de entrada (AGORA COMO ATRIBUTOS DA JANELA)
        especie_var = tk.StringVar(value="Cão")
        nome_entry = ttk.Entry(main_frame)
        peso_entry = ttk.Entry(main_frame)
        farmaco_combobox = ttk.Combobox(main_frame, state='readonly')
        dose_entry = ttk.Entry(main_frame)
        obs_text = tk.Text(main_frame, height=4, width=30)
        
        # Função para calcular dose (AGORA DENTRO DO ESCOPO CORRETO)
        def calcular_dose():
            try:
                peso = float(peso_entry.get())  # Agora pode acessar peso_entry
                if not farmaco_selecionado:
                    messagebox.showerror("Erro", "Selecione um fármaco!")
                    return
                    
                dose_valor = (peso * farmaco_selecionado.dose) / farmaco_selecionado.concentracao
                dose_calculada.set(f"{dose_valor:.2f} ml")
                dose_entry.delete(0, tk.END)
                dose_entry.insert(0, f"{dose_valor:.2f}")
                
            except ValueError:
                messagebox.showerror("Erro", "Digite um peso válido!")
            except Exception as e:
                messagebox.showerror("Erro", f"Falha ao calcular dose: {str(e)}")

        # Função ao selecionar fármaco
        def on_farmaco_select(event):
            nonlocal farmaco_selecionado
            farmaco_str = farmaco_combobox.get()
            if farmaco_str:
                farmaco_id = int(farmaco_str.split(' - ')[0])
                with Session(engine) as session:
                    farmaco_selecionado = session.get(Farmaco, farmaco_id)

        # Layout do formulário
        ttk.Label(main_frame, text="Espécie:").grid(row=0, column=0, padx=5, pady=5, sticky='e')
        ttk.Radiobutton(main_frame, text="Cão", variable=especie_var, value="Cão").grid(row=0, column=1, sticky='w')
        ttk.Radiobutton(main_frame, text="Gato", variable=especie_var, value="Gato").grid(row=0, column=2, sticky='w')
        
        ttk.Label(main_frame, text="Nome:").grid(row=1, column=0, padx=5, pady=5, sticky='e')
        nome_entry.grid(row=1, column=1, columnspan=2, sticky='we', padx=5)
        
        ttk.Label(main_frame, text="Peso (kg):").grid(row=2, column=0, padx=5, pady=5, sticky='e')
        peso_entry.grid(row=2, column=1, columnspan=2, sticky='we', padx=5)
        
        ttk.Label(main_frame, text="Fármaco:").grid(row=3, column=0, padx=5, pady=5, sticky='e')
        farmaco_combobox.grid(row=3, column=1, columnspan=2, sticky='we', padx=5)
        farmaco_combobox.bind('<<ComboboxSelected>>', on_farmaco_select)
        
        # Carregar fármacos
        with Session(engine) as session:
            farmacos = session.exec(select(Farmaco)).all()
            farmaco_combobox['values'] = [f"{f.id} - {f.nome} ({f.modo_uso})" for f in farmacos]
        
        ttk.Label(main_frame, text="Dose sugerida:").grid(row=4, column=0, padx=5, pady=5, sticky='e')
        ttk.Label(main_frame, textvariable=dose_calculada).grid(row=4, column=1, sticky='w')
        
        ttk.Label(main_frame, text="Dose utilizada (ml):").grid(row=5, column=0, padx=5, pady=5, sticky='e')
        dose_entry.grid(row=5, column=1, columnspan=2, sticky='we', padx=5)
        
        ttk.Label(main_frame, text="Observações:").grid(row=6, column=0, padx=5, pady=5, sticky='ne')
        obs_text.grid(row=6, column=1, columnspan=2, sticky='we', padx=5)
        
        # Frame de botões
        btn_frame = ttk.Frame(main_frame)
        btn_frame.grid(row=7, column=0, columnspan=3, pady=10)
        def save_avulsa_session():
            """Salva a sessão avulsa"""
            try:
                # Validar campos obrigatórios
                if not all([peso_entry.get(), farmaco_combobox.get(), dose_entry.get()]):
                    messagebox.showerror("Erro", "Preencha todos os campos obrigatórios!")
                    return
                    
                # Extrair ID do fármaco
                farmaco_str = farmaco_combobox.get()
                farmaco_id = int(farmaco_str.split(' - ')[0])
                
                sessao = SessaoAvulsaAnestesia(
                    especie=especie_var.get(),
                    nome_animal=nome_entry.get(),
                    peso_kg=float(peso_entry.get()),
                    id_farmaco=farmaco_id,
                    dose_utilizada_ml=float(dose_entry.get()),
                    observacoes=obs_text.get("1.0", tk.END).strip() or None,
                    data=datetime.now()
                )
                
                with Session(engine) as session:
                    session.add(sessao)
                    session.commit()
                    messagebox.showinfo("Sucesso", "Sessão avulsa registrada com sucesso!")
                    avulsa_window.destroy()
                    self.load_sessions_list()
                    
            except ValueError:
                messagebox.showerror("Erro", "Digite valores numéricos válidos!")
            except Exception as e:
                messagebox.showerror("Erro", f"Falha ao registrar sessão avulsa: {str(e)}")

        # Botões
        ttk.Button(btn_frame, text="Calcular Dose", command=calcular_dose).pack(side='left', padx=5)
        ttk.Button(btn_frame, text="Salvar", command=save_avulsa_session).pack(side='left', padx=5)
        ttk.Button(btn_frame, text="Cancelar", command=avulsa_window.destroy).pack(side='left', padx=5)
    
        main_frame.columnconfigure(1, weight=1)

    def update_farmaco_info(self, event=None):
        """Atualiza as informações do fármaco selecionado"""
        farmaco_str = self.farmaco_combobox.get()
        if not farmaco_str:
            return
            
        farmaco_id = int(farmaco_str.split(' - ')[0])
        
        with Session(engine) as session:
            farmaco = session.get(Farmaco, farmaco_id)
            if farmaco:
                self.farmaco_dose.config(text=f"{farmaco.dose} {farmaco.unidade_dose}")
                self.farmaco_modo.config(text=farmaco.modo_uso)
                
                # Se for infusão contínua, mostra a aba de infusão
                if farmaco.modo_uso == "infusão contínua":
                    self.notebook.select(3)  # Seleciona a aba de infusão

    def calculate_dose(self):
        """Calcula a dose do fármaco baseada no peso do animal"""
        try:
            # Obter animal selecionado
            animal_str = self.animal_combobox.get()
            if not animal_str:
                messagebox.showerror("Erro", "Selecione um animal ou crie uma sessão avulsa!")
                return
                
            animal_id = int(animal_str.split(' - ')[0])
            
            # Obter fármaco selecionado
            farmaco_str = self.farmaco_combobox.get()
            if not farmaco_str:
                messagebox.showerror("Erro", "Selecione um fármaco!")
                return
                
            farmaco_id = int(farmaco_str.split(' - ')[0])
            
            with Session(engine) as session:
                animal = session.get(Animal, animal_id)
                farmaco = session.get(Farmaco, farmaco_id)
                
                if not animal or not farmaco:
                    messagebox.showerror("Erro", "Animal ou fármaco não encontrado!")
                    return
                
                # Calcular dose
                if farmaco.modo_uso == "bolus":
                    dose_ml = (animal.peso_kg * farmaco.dose) / farmaco.concentracao
                    self.dose_calculada.config(text=f"{dose_ml:.2f} ml")
                else:
                    # Para infusão contínua, mostramos na aba específica
                    self.infusion_peso.delete(0, tk.END)
                    self.infusion_peso.insert(0, str(animal.peso_kg))
                    messagebox.showinfo("Info", "Configure a infusão na aba 'Infusão'")
                
        except Exception as e:
            messagebox.showerror("Erro", f"Falha ao calcular dose: {str(e)}")

    def calculate_infusion(self):
        """Calcula os parâmetros de infusão contínua"""
        try:
            peso = float(self.infusion_peso.get())
            volume = int(self.infusion_volume.get())
            equipo = self.infusion_equipo.get()
            taxa = float(self.infusion_taxa.get())
            
            # Criar configuração temporária
            config = ConfigInfusao(
                peso_kg=peso,
                volume_bolsa_ml=volume,
                equipo_tipo="microgotas" if "Micro" in equipo else "macrogotas",
                taxa_ml_kg_h=taxa
            )
            
            # Calcular taxas
            resultados = calcular_taxas(config)
            
            # Mostrar resultados
            self.result_taxa.config(text=f"{resultados['taxa_ml_h']:.2f} ml/h")
            self.result_gotas.config(text=f"{resultados['gotas_min']:.2f} gts/min")
            self.result_duracao.config(text=f"{resultados['duracao_h']:.2f} horas")
            
        except Exception as e:
            messagebox.showerror("Erro", f"Falha ao calcular infusão: {str(e)}")

    def register_session(self):
        """Registra uma nova sessão anestésica"""
        try:
            # Obter animal selecionado
            animal_str = self.animal_combobox.get()
            if not animal_str:
                messagebox.showerror("Erro", "Selecione um animal ou crie uma sessão avulsa!")
                return
                
            animal_id = int(animal_str.split(' - ')[0])
            
            # Obter fármaco selecionado
            farmaco_str = self.farmaco_combobox.get()
            if not farmaco_str:
                messagebox.showerror("Erro", "Selecione um fármaco!")
                return
                
            farmaco_id = int(farmaco_str.split(' - ')[0])
            
            # Obter dose calculada
            dose_text = self.dose_calculada.cget("text")
            if not dose_text or "ml" not in dose_text:
                messagebox.showerror("Erro", "Calcule a dose primeiro!")
                return
                
            dose_utilizada = float(dose_text.replace(" ml", ""))
            
            # Obter observações
            observacoes = self.session_obs.get("1.0", tk.END).strip() or None
            
            with Session(engine) as session:
                # Verificar se é infusão contínua
                farmaco = session.get(Farmaco, farmaco_id)
                config = None
                
                if farmaco.modo_uso == "infusão contínua":
                    # Criar configuração de infusão
                    peso = float(self.infusion_peso.get())
                    volume = int(self.infusion_volume.get())
                    equipo = "microgotas" if "Micro" in self.infusion_equipo.get() else "macrogotas"
                    
                    config = ConfigInfusao(
                        peso_kg=peso,
                        volume_bolsa_ml=volume,
                        equipo_tipo=equipo,
                        taxa_ml_kg_h=float(self.infusion_taxa.get())
                    )
                    session.add(config)
                    session.commit()
                    session.refresh(config)
                
                # Criar sessão
                sessao = SessaoAnestesia(
                    id_animal=animal_id,
                    id_farmaco=farmaco_id,
                    dose_utilizada_ml=dose_utilizada,
                    observacoes=observacoes,
                    config_infusao_id=config.id if config else None,
                    data=datetime.now()
                )
                
                session.add(sessao)
                session.commit()
                
                messagebox.showinfo("Sucesso", f"Sessão registrada com sucesso!\nID: {sessao.id}")
                self.load_sessions_list()
                
                # Limpar campos
                self.session_obs.delete("1.0", tk.END)
                self.dose_calculada.config(text="")
                
        except Exception as e:
            messagebox.showerror("Erro", f"Falha ao registrar sessão: {str(e)}")

    def generate_prescription(self):
        """Gera um arquivo TXT com a prescrição da sessão selecionada"""
        try:
            selected_item = self.session_tree.selection()
            if not selected_item:
                messagebox.showerror("Erro", "Selecione uma sessão na lista!")
                return
                
            session_id = self.session_tree.item(selected_item[0])['values'][0]
            
            with Session(engine) as session:
                # Primeiro tenta buscar como sessão normal
                sessao = session.get(SessaoAnestesia, session_id)
                
                if not sessao:
                    # Se não encontrar, busca como sessão avulsa
                    sessao_avulsa = session.get(SessaoAvulsaAnestesia, session_id)
                    if not sessao_avulsa:
                        messagebox.showerror("Erro", "Sessão não encontrada!")
                        return
                    
                    # Cria conteúdo para sessão avulsa
                    farmaco = session.get(Farmaco, sessao_avulsa.id_farmaco)
                    
                    conteudo = f"PRESCRIÇÃO ANESTÉSICA - Sessão Avulsa #{session_id}\n"
                    conteudo += "="*50 + "\n"
                    conteudo += "\n🐾 DADOS DO PACIENTE:\n"
                    conteudo += f"Nome: {sessao_avulsa.nome_animal}\n"
                    conteudo += f"Espécie: {sessao_avulsa.especie}\n"
                    conteudo += f"Peso: {sessao_avulsa.peso_kg} kg\n"
                    
                    conteudo += "\n💊 DADOS FARMACOLÓGICOS:\n"
                    conteudo += f"Medicação: {farmaco.nome}\n"
                    conteudo += f"Dose: {farmaco.dose} {farmaco.unidade_dose}\n"
                    conteudo += f"Concentração: {farmaco.concentracao} mg/ml\n"
                    conteudo += f"Volume administrado: {sessao_avulsa.dose_utilizada_ml:.2f} ml\n"
                    
                else:
                    # Sessão normal com animal cadastrado
                    farmaco = session.get(Farmaco, sessao.id_farmaco)
                    animal = session.get(Animal, sessao.id_animal) if sessao.id_animal else None
                    config = session.get(ConfigInfusao, sessao.config_infusao_id) if sessao.config_infusao_id else None

                    conteudo = f"PRESCRIÇÃO ANESTÉSICA - Sessão #{session_id}\n"
                    conteudo += "="*50 + "\n"
                    
                    # Dados do Animal
                    conteudo += "\n🐾 DADOS DO PACIENTE:\n"
                    if animal:
                        conteudo += f"Nome: {animal.nome}\nEspécie: {animal.especie}\nPeso: {animal.peso_kg} kg\n"
                    else:
                        conteudo += "Dados do animal não disponíveis\n"

                    conteudo += "\n💊 DADOS FARMACOLÓGICOS:\n"
                    if farmaco:
                        conteudo += f"Medicação: {farmaco.nome}\n"
                        conteudo += f"Dose: {farmaco.dose} {farmaco.unidade_dose}\n"
                        conteudo += f"Concentração: {farmaco.concentracao} mg/ml\n"
                        conteudo += f"Volume administrado: {sessao.dose_utilizada_ml:.2f} ml\n"
                    else:
                        conteudo += "Dados do fármaco não disponíveis\n"

                    # Configuração de Infusão (se aplicável)
                    if config:
                        calculos = calcular_taxas(config)
                        conteudo += "\n⚙️ CONFIGURAÇÃO DE INFUSÃO:\n"
                        conteudo += f"Volume da bolsa: {config.volume_bolsa_ml} ml\n"
                        conteudo += f"Taxa: {calculos['taxa_ml_h']} ml/h\n"
                        conteudo += f"Gotas/min: {calculos['gotas_min']}\n"
                        conteudo += f"Duração estimada: {calculos['duracao_h']:.1f} horas\n"

                    # Observações (se existirem)
                    if sessao.observacoes:
                        conteudo += "\n📝 OBSERVAÇÕES:\n"
                        conteudo += f"{sessao.observacoes}\n"
                                    
                
                # Salvar arquivo
                os.makedirs("prescricoes", exist_ok=True)
                nome_arquivo = f"prescricoes/prescricao_{session_id}.txt"
                
                with open(nome_arquivo, "w", encoding="utf-8") as f:
                    f.write(conteudo)

                messagebox.showinfo("Sucesso", f"Prescrição salva em:\n{nome_arquivo}")
                
        except Exception as e:
            messagebox.showerror("Erro", f"Falha ao gerar prescrição: {str(e)}")
    def load_sessions_list(self):
        """Carrega a lista de sessões no TreeView"""
        with Session(engine) as session:
            # Buscar sessões normais
            sessoes = session.exec(select(SessaoAnestesia)).all()
            
            # Buscar sessões avulsas
            sessoes_avulsas = session.exec(select(SessaoAvulsaAnestesia)).all()
            
            # Limpar treeview
            for item in self.session_tree.get_children():
                self.session_tree.delete(item)
                
            # Adicionar sessões normais
            for sessao in sessoes:
                animal = session.get(Animal, sessao.id_animal)
                farmaco = session.get(Farmaco, sessao.id_farmaco)
                
                self.session_tree.insert('', 'end', values=(
                    sessao.id,
                    animal.nome if animal else "N/A",
                    farmaco.nome if farmaco else "N/A",
                    f"{sessao.dose_utilizada_ml:.2f} ml",
                    sessao.data.strftime('%d/%m/%Y %H:%M') if sessao.data else "N/A"
                ))
            
            # Adicionar sessões avulsas
            for sessao in sessoes_avulsas:
                farmaco = session.get(Farmaco, sessao.id_farmaco)
                
                self.session_tree.insert('', 'end', values=(
                    sessao.id,
                    f"{sessao.nome_animal} (Avulso)",
                    farmaco.nome if farmaco else "N/A",
                    f"{sessao.dose_utilizada_ml:.2f} ml",
                    sessao.data.strftime('%d/%m/%Y %H:%M') if sessao.data else "N/A"
                ))
if __name__ == "__main__":
    root = tk.Tk()
    app = VetAnesthesiaApp(root)
    
    # Centralizar a janela
    window_width = 1200
    window_height = 800
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    position_top = int(screen_height/2 - window_height/2)
    position_right = int(screen_width/2 - window_width/2)
    root.geometry(f"{window_width}x{window_height}+{position_right}+{position_top}")
    
    root.mainloop()  # ÚNICA chamada ao mainloop