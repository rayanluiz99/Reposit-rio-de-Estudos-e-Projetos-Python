# Importações de modelos
from models.protocolo import Protocolo, ProtocoloFarmaco
from controllers.protocolo_controller import criar_protocolo, listar_protocolos, obter_farmacos_do_protocolo, obter_protocolo, deletar_protocolo, obter_todos_farmacos, adicionar_farmaco_a_protocolo
import tkinter as tk
from models.animal import Animal
from models.farmaco import Farmaco
from models.config_infusao import ConfigInfusao, TipoEquipo
from models.sessao import SessaoAnestesia, SessaoAvulsaAnestesia
from controllers.config_infusao_controller import calcular_infusao_continua
# No topo do arquivo, adicione estes imports:



# Importações de controllers
from controllers.animal_controller import cadastrar_animal
from controllers.farmaco_controller import (
    cadastrar_farmaco,
    importar_farmacos_csv,
    exportar_farmacos_csv,
    listar_farmacos,
)
from controllers.config_infusao_controller import (
    criar_config_infusao,
    calcular_infusao_especifica,
    calcular_infusao_continua,
    calcular_taxas,
    calcular_infusao_planilha
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


def formatar_duracao(horas: float) -> str:
        """Formata um tempo em horas (decimal) para horas e minutos."""
        horas_inteiras = int(horas)
        minutos = int((horas - horas_inteiras) * 60)
        
        if horas_inteiras > 0 and minutos > 0:
            return f"{horas_inteiras}h {minutos}min"
        elif horas_inteiras > 0:
            return f"{horas_inteiras}h"
        elif minutos > 0:
            return f"{minutos}min"
        else:
            return "0min"

class VetAnesthesiaApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Anestesia Veterinária - Cálculos de Infusão")
        self.root.geometry("1200x800")
        self.style = ttk.Style()
        self.configure_styles()
        
        # Frame para botões globais (ADICIONE ESTE FRAME)
        global_btn_frame = ttk.Frame(root)
        global_btn_frame.pack(fill='x', padx=10, pady=5)
        
        # Botão da calculadora (MODIFICADO)
        ttk.Button(
            global_btn_frame, 
            text="Calculadora (F2)", 
            command=self.show_calculator
        ).pack(side='left', padx=5)
        
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
        self.create_protocolo_tab() 
        
        # Painel de fórmulas
        self.create_formulas_panel()
        
        # Carregar dados iniciais
        self.load_initial_data()
        
        # Atalho de teclado (MODIFICADO)
        self.root.bind("<F2>", lambda e: self.show_calculator())

    
    
    def show_calculator(self, event=None):
        """Calculadora veterinária com conversões práticas"""
        calc_window = tk.Toplevel(self.root)
        calc_window.title("Calculadora Veterinária")
        calc_window.geometry("380x600")
        calc_window.resizable(False, False)

        # Variável para o visor (agora editável)
        display_var = tk.StringVar(value="")
        
        # Frame do visor melhorado
        display_frame = ttk.Frame(calc_window, padding=10)
        display_frame.pack(pady=10)
        
        ttk.Entry(
            display_frame, 
            textvariable=display_var, 
            font=('Arial', 24),
            justify='right',
            width=12
        ).pack()

        # Frame de botões numéricos
        btn_frame = ttk.Frame(calc_window)
        btn_frame.pack(pady=5)

        # Layout dos botões
        buttons = [
            ('7', 0, 0), ('8', 0, 1), ('9', 0, 2), ('/', 0, 3),
            ('4', 1, 0), ('5', 1, 1), ('6', 1, 2), ('*', 1, 3),
            ('1', 2, 0), ('2', 2, 1), ('3', 2, 2), ('-', 2, 3),
            ('0', 3, 0), ('.', 3, 1), ('C', 3, 2), ('+', 3, 3),
            ('=', 4, 0, 1, 4)  # Botão igual ocupando 4 colunas
        ]

        # Funções atualizadas
        def insert_value(value):
            current = display_var.get()
            display_var.set(current + str(value))
        
        def clear_display():
            display_var.set("")
        
        def calculate():
            try:
                result = eval(display_var.get())
                display_var.set(str(result))
            except:
                display_var.set("ERRO")

        # Criando botões
        for button in buttons:
            if button[0] == '=':
                btn = ttk.Button(btn_frame, text=button[0], command=calculate)
                btn.grid(row=button[1], column=button[2], 
                        columnspan=button[3], sticky='nsew', padx=2, pady=2)
            elif button[0] == 'C':
                btn = ttk.Button(btn_frame, text=button[0], command=clear_display)
                btn.grid(row=button[1], column=button[2], padx=2, pady=2)
            else:
                btn = ttk.Button(btn_frame, text=button[0], 
                            command=lambda v=button[0]: insert_value(v))
                btn.grid(row=button[1], column=button[2], padx=2, pady=2)

        # Conversões veterinárias (área expandida)
        conv_frame = ttk.LabelFrame(calc_window, text="Conversões Clínicas", padding=10)
        conv_frame.pack(pady=10, fill='x', padx=10)

        def convert_mg_to_mcg():
            try:
                mg = float(display_var.get())
                display_var.set(str(mg * 1000))
            except:
                display_var.set("ERRO")
        
        def convert_mcg_to_mg():
            try:
                mcg = float(display_var.get())
                display_var.set(str(mcg / 1000))
            except:
                display_var.set("ERRO")
        
        def convert_ml_to_macrodrops():
            try:
                ml = float(display_var.get())
                display_var.set(str(ml * 20))  # 20 gotas/ml
            except:
                display_var.set("ERRO")
        
        def convert_macrodrops_to_ml():
            try:
                gotas = float(display_var.get())
                display_var.set(str(gotas / 20))
            except:
                display_var.set("ERRO")
        
        def convert_kg_to_lbs():
            try:
                kg = float(display_var.get())
                display_var.set(str(kg * 2.20462))
            except:
                display_var.set("ERRO")
        
        def convert_lbs_to_kg():
            try:
                lbs = float(display_var.get())
                display_var.set(str(lbs / 2.20462))
            except:
                display_var.set("ERRO")
        
        # Frame de conversões
        conv_frame = ttk.LabelFrame(calc_window, text="Conversões Clínicas", padding=10)
        conv_frame.pack(pady=10, fill='x', padx=10)
        
        # Botões de conversão (2 colunas)
        conversions = [
            ("mg → mcg", convert_mg_to_mcg),
            ("mcg → mg", convert_mcg_to_mg),
            ("mL → gotas (macro)", convert_ml_to_macrodrops),
            ("gotas (macro) → mL", convert_macrodrops_to_ml),
            ("kg → lbs", convert_kg_to_lbs),
            ("lbs → kg", convert_lbs_to_kg)
        ]
        
        for i, (text, command) in enumerate(conversions):
            row = i // 2
            col = i % 2
            ttk.Button(
                conv_frame, 
                text=text, 
                command=command
            ).grid(row=row, column=col, padx=5, pady=5, sticky='ew')
        
        # Configurar grid
        conv_frame.columnconfigure(0, weight=1)
        conv_frame.columnconfigure(1, weight=1)
    
    
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
            
            protocolos = listar_protocolos(session)
            self.protocolo_combobox['values'] = [f"{p.id} - {p.nome}" for p in protocolos]
            
            # Carregar fármacos para combobox
            farmacos = session.exec(select(Farmaco)).all()
            self.farmaco_combobox['values'] = [f"{f.id} - {f.nome} ({f.modo_uso})" for f in farmacos]
            
            # Carregar lista completa de fármacos (Treeview)
            self.load_farmacos_tree()  # Agora chamando o método corretamente
    def create_protocolo_tab(self):
        """Cria a aba de gerenciamento de protocolos"""
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="📜 Protocolos")
        
        # Frame principal
        main_frame = ttk.Frame(frame)
        main_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Treeview para protocolos
        columns = ("ID", "Nome", "Descrição", "Criado em")
        self.protocolo_tree = ttk.Treeview(main_frame, columns=columns, show='headings')
        
        self.protocolo_tree.heading("ID", text="ID")
        self.protocolo_tree.heading("Nome", text="Nome")
        self.protocolo_tree.heading("Descrição", text="Descrição")
        self.protocolo_tree.heading("Criado em", text="Criado em")
        
        self.protocolo_tree.column("ID", width=50, anchor='center')
        self.protocolo_tree.column("Nome", width=150)
        self.protocolo_tree.column("Descrição", width=200)
        self.protocolo_tree.column("Criado em", width=120)
        
        # Treeview para fármacos do protocolo
        farmaco_columns = ("Ordem", "Nome", "Dose", "Concentração", "Modo Uso")
        self.protocolo_farmaco_tree = ttk.Treeview(main_frame, columns=farmaco_columns, show='headings')
        
        for col in farmaco_columns:
            self.protocolo_farmaco_tree.heading(col, text=col)
            self.protocolo_farmaco_tree.column(col, width=100)
        
        # Layout
        self.protocolo_tree.pack(fill='x', pady=5)
        self.protocolo_farmaco_tree.pack(fill='x', pady=5)
        
        # Frame de botões
        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(fill='x', pady=10)
        
        ttk.Button(btn_frame, text="Novo Protocolo", command=self.criar_novo_protocolo).pack(side='left', padx=5)
        ttk.Button(btn_frame, text="Excluir Protocolo", command=self.deletar_protocolo).pack(side='left', padx=5)
        ttk.Button(btn_frame, text="Adicionar Fármaco", command=self.adicionar_farmaco_protocolo).pack(side='left', padx=5)
        ttk.Button(btn_frame, text="Remover Fármaco", command=self.remover_farmaco_protocolo).pack(side='left', padx=5)
        
        # Carregar protocolos
        self.carregar_protocolos()
        
        # Evento de seleção
        self.protocolo_tree.bind('<<TreeviewSelect>>', self.selecionar_protocolo)
    def adicionar_farmaco_protocolo(self):
        """Janela para adicionar um fármaco ao protocolo selecionado"""
        selected = self.protocolo_tree.selection()
        
        if not selected:
            messagebox.showwarning("Aviso", "Selecione um protocolo para adicionar fármacos.")
            return
        
        protocolo_id = self.protocolo_tree.item(selected[0])["values"][0]

        window = tk.Toplevel(self.root)
        window.title("Adicionar Fármaco ao Protocolo")
        window.geometry("400x200")

        # Seleção de fármaco
        ttk.Label(window, text="Fármaco:").pack(pady=5)
        farmaco_var = tk.StringVar()
        farmaco_combo = ttk.Combobox(window, textvariable=farmaco_var, state="readonly", width=40)
        farmaco_combo.pack(pady=5)

        # Carrega os fármacos do banco
        with Session(engine) as session:
            farmacos = obter_todos_farmacos(session)
            farmaco_combo["values"] = [f"{f.id} - {f.nome} ({f.modo_uso})" for f in farmacos]

        def salvar_farmaco():
            farmaco_str = farmaco_var.get()
            if not farmaco_str:
                messagebox.showerror("Erro", "Selecione um fármaco!")
                return
            
            farmaco_id = int(farmaco_str.split(' - ')[0])
            
            with Session(engine) as session:
                # Determinar ordem (último + 1)
                stmt = select(ProtocoloFarmaco).where(ProtocoloFarmaco.protocolo_id == protocolo_id)
                itens = session.exec(stmt).all()
                ordem = len(itens) + 1
                
                # Adicionar fármaco ao protocolo
                adicionar_farmaco_a_protocolo(session, protocolo_id, farmaco_id, ordem)
                messagebox.showinfo("Sucesso", "Fármaco adicionado ao protocolo!")
                window.destroy()
                self.selecionar_protocolo(None)  # Atualizar lista

        ttk.Button(window, text="Adicionar", command=salvar_farmaco).pack(pady=10)

    def criar_novo_protocolo(self):
        """Janela para criar novo protocolo"""
        window = tk.Toplevel(self.root)
        window.title("Novo Protocolo")
        window.geometry("400x300")
        
        ttk.Label(window, text="Nome do Protocolo:").pack(pady=5)
        nome_entry = ttk.Entry(window, width=30)
        nome_entry.pack(pady=5)
        
        ttk.Label(window, text="Descrição:").pack(pady=5)
        desc_entry = tk.Text(window, height=4, width=30)
        desc_entry.pack(pady=5)
        
        def salvar():
            nome = nome_entry.get().strip()
            desc = desc_entry.get("1.0", tk.END).strip()
            
            if not nome:
                messagebox.showerror("Erro", "O nome do protocolo é obrigatório!")
                return
                
            with Session(engine) as session:
                criar_protocolo(session, nome, desc)
                messagebox.showinfo("Sucesso", "Protocolo criado com sucesso!")
                window.destroy()
                self.carregar_protocolos()
        
        ttk.Button(window, text="Salvar", command=salvar).pack(pady=10)

    def deletar_protocolo(self):
        """Deleta o protocolo selecionado na Treeview"""
        selected = self.protocolo_tree.selection()
        
        if not selected:
            messagebox.showwarning("Atenção", "Selecione um protocolo para excluir.")
            return

        protocolo_id = self.protocolo_tree.item(selected[0])["values"][0]
        
        confirm = messagebox.askyesno(
            "Confirmação",
            f"Tem certeza que deseja excluir o protocolo ID {protocolo_id}?"
        )
        
        if not confirm:
            return
        
        from controllers.protocolo_controller import deletar_protocolo  # Certifique-se que isso existe

        with Session(engine) as session:
            deletar_protocolo(session, protocolo_id)
            messagebox.showinfo("Sucesso", "Protocolo excluído com sucesso!")
            self.carregar_protocolos()
            
    def adicionar_farmaco_protocolo(self):
        """Janela para adicionar um fármaco ao protocolo selecionado"""
        selected = self.protocolo_tree.selection()
        
        if not selected:
            messagebox.showwarning("Aviso", "Selecione um protocolo para adicionar fármacos.")
            return
        
        protocolo_id = self.protocolo_tree.item(selected[0])["values"][0]

        window = tk.Toplevel(self.root)
        window.title("Adicionar Fármaco ao Protocolo")
        window.geometry("400x200")

        # Seleção de fármaco
        ttk.Label(window, text="Fármaco:").pack(pady=5)
        farmaco_var = tk.StringVar()
        farmaco_combo = ttk.Combobox(window, textvariable=farmaco_var, state="readonly", width=40)
        farmaco_combo.pack(pady=5)

        # Carrega os fármacos do banco CORRETAMENTE
        with Session(engine) as session:
            # Busca todos os fármacos usando a declaração SQLModel correta
            stmt = select(Farmaco)
            farmacos = session.exec(stmt).all()
            
            # Preenche o combobox com os fármacos
            farmaco_combo["values"] = [f"{f.id} - {f.nome} ({f.modo_uso})" for f in farmacos]

        def salvar_farmaco():
            farmaco_str = farmaco_var.get()
            if not farmaco_str:
                messagebox.showerror("Erro", "Selecione um fármaco!")
                return
            
            # Extrai o ID do fármaco da string formatada
            farmaco_id = int(farmaco_str.split(' - ')[0])
            
            with Session(engine) as session:
                # Determinar a ordem (última posição + 1)
                stmt = select(ProtocoloFarmaco).where(ProtocoloFarmaco.protocolo_id == protocolo_id)
                itens = session.exec(stmt).all()
                ordem = len(itens) + 1
                
                # Adicionar fármaco ao protocolo
                pf = ProtocoloFarmaco(
                    protocolo_id=protocolo_id,
                    farmaco_id=farmaco_id,
                    ordem=ordem
                )
                
                session.add(pf)
                session.commit()
                messagebox.showinfo("Sucesso", "Fármaco adicionado ao protocolo!")
                window.destroy()
                
                # Atualizar a lista de fármacos do protocolo
                self.selecionar_protocolo(None)

        ttk.Button(window, text="Adicionar", command=salvar_farmaco).pack(pady=10)
            
    def remover_farmaco_protocolo(self):
        """Remove um fármaco do protocolo selecionado"""
        # Verifica se há um protocolo selecionado
        selected_protocolo = self.protocolo_tree.selection()
        if not selected_protocolo:
            messagebox.showwarning("Aviso", "Selecione um protocolo primeiro.")
            return

        protocolo_id = self.protocolo_tree.item(selected_protocolo[0])["values"][0]

        # Criar uma janela para seleção do fármaco a remover
        window = tk.Toplevel(self.root)
        window.title("Remover Fármaco do Protocolo")
        window.geometry("400x300")

        ttk.Label(window, text="Selecione o fármaco a remover:").pack(pady=5)

        farmaco_var = tk.StringVar()
        farmaco_combo = ttk.Combobox(window, textvariable=farmaco_var, state="readonly")
        farmaco_combo.pack(pady=10)

        from controllers.protocolo_controller import obter_farmacos_do_protocolo
        with Session(engine) as session:
            farmacos_atuais = obter_farmacos_do_protocolo(session, protocolo_id)
            self._farmacos_e
            

    def carregar_protocolos(self):
        """Carrega todos os protocolos na treeview"""
        with Session(engine) as session:
            # Usando a declaração correta para buscar protocolos
            protocolos = session.exec(select(Protocolo)).all()
            
            # Limpar treeview
            for item in self.protocolo_tree.get_children():
                self.protocolo_tree.delete(item)
                
            # Adicionar protocolos
            for p in protocolos:
                self.protocolo_tree.insert('', 'end', values=(
                    p.id,
                    p.nome,
                    p.descricao or "",
                    p.created_at.strftime('%d/%m/%Y')
                ))

    def selecionar_protocolo(self, event):
        """Carrega os fármacos do protocolo selecionado"""
        selected = self.protocolo_tree.selection()
        if not selected:
            return
            
        protocolo_id = self.protocolo_tree.item(selected[0])['values'][0]
        
        with Session(engine) as session:
            # Busca os fármacos do protocolo usando a declaração correta
            stmt = (
                select(Farmaco, ProtocoloFarmaco.ordem)
                .join(ProtocoloFarmaco, Farmaco.id == ProtocoloFarmaco.farmaco_id)
                .where(ProtocoloFarmaco.protocolo_id == protocolo_id)
                .order_by(ProtocoloFarmaco.ordem)
            )
            
            resultados = session.exec(stmt).all()
            
            # Limpar treeview de fármacos
            for item in self.protocolo_farmaco_tree.get_children():
                self.protocolo_farmaco_tree.delete(item)
                
            # Adicionar fármacos
            for farmaco, ordem in resultados:
                self.protocolo_farmaco_tree.insert('', 'end', values=(
                    ordem,
                    farmaco.nome,
                    f"{farmaco.dose} {farmaco.unidade_dose}",
                    f"{farmaco.concentracao} mg/ml",
                    farmaco.modo_uso
                ))
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
        
        ttk.Label(form_frame, text="Protocolo:").grid(row=0, column=3, sticky='e', padx=5, pady=2)
        self.protocolo_combobox = ttk.Combobox(form_frame, state='readonly', width=30)
        self.protocolo_combobox.grid(row=0, column=4, sticky='w', padx=5, pady=2)
        ttk.Button(form_frame, text="Carregar", command=self.carregar_protocolo_sessao).grid(row=0, column=5, padx=5)
        
        # Treeview para fármacos do protocolo na sessão
        ttk.Label(form_frame, text="Fármacos do Protocolo:").grid(row=8, column=0, sticky='ne', padx=5, pady=2)
        columns_farmacos = ("Fármaco", "Dose", "Modo", "Dose Calculada")
        self.protocolo_farmacos_tree = ttk.Treeview(form_frame, columns=columns_farmacos, show='headings', height=4)
        
        for col in columns_farmacos:
            self.protocolo_farmacos_tree.heading(col, text=col)
            self.protocolo_farmacos_tree.column(col, width=100)
        
        self.protocolo_farmacos_tree.grid(row=8, column=1, columnspan=4, sticky='we', padx=5, pady=2)
        
        
        # Seleção de animal
        ttk.Label(form_frame, text="Animal:").grid(row=0, column=0, sticky='e', padx=5, pady=2)
        self.animal_combobox = ttk.Combobox(form_frame, state='readonly', width=40)
        self.animal_combobox.grid(row=0, column=1, sticky='w', padx=5, pady=2)
        ttk.Button(form_frame, text="Sessão Avulsa", command=self.open_avulsa_session).grid(row=0, column=2, padx=5)
        
        # Peso (atualizado quando seleciona animal)
        ttk.Label(form_frame, text="Peso (kg):").grid(row=1, column=0, sticky='e', padx=5, pady=2)
        self.session_peso = ttk.Label(form_frame, text="", width=10)
        self.session_peso.grid(row=1, column=1, sticky='w', padx=5, pady=2)
        
        ttk.Label(form_frame, text="Protocolo:").grid(row=0, column=3, sticky='e', padx=5, pady=2)
        self.protocolo_combobox = ttk.Combobox(form_frame, state='readonly', width=30)
        self.protocolo_combobox.grid(row=0, column=4, sticky='w', padx=5, pady=2)
        ttk.Button(form_frame, text="Carregar", command=self.carregar_protocolo_sessao).grid(row=0, column=5, padx=5)

        # Seleção de fármaco
        ttk.Label(form_frame, text="Fármaco:").grid(row=2, column=0, sticky='e', padx=5, pady=2)
        self.farmaco_combobox = ttk.Combobox(form_frame, state='readonly', width=40)
        self.farmaco_combobox.grid(row=2, column=1, sticky='w', padx=5, pady=2)
        self.farmaco_combobox.bind('<<ComboboxSelected>>', self.update_farmaco_info)
        
         # Adicionar evento para atualizar peso quando animal for selecionado
        self.animal_combobox.bind('<<ComboboxSelected>>', self.atualizar_peso_animal)
        
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
        
        # Adicione este botão
        ttk.Button(btn_frame, text="Registrar Sessão Protocolo", command=self.generate_protocol_prescription).pack(side='left', padx=5)

          # Novo botão para gerar prescrição de protocolo
        ttk.Button(btn_frame, text="Gerar Prescrição Protocolo", 
              command=self.generate_protocol_prescription).pack(side='left', padx=5)

        # Botões para gerar prescrição do protocolo
        presc_btn_frame = ttk.Frame(btn_frame)
        presc_btn_frame.pack(side='left', padx=5)
        ttk.Button(presc_btn_frame, text="Gerar Prescrição", command=self.generate_prescription).pack(side='left')
        ttk.Button(presc_btn_frame, text="Gerar Prescrição Protocolo", command=self.generate_protocol_prescription).pack(side='left', padx=(5,0))
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
        
    def atualizar_peso_animal(self, event=None):
        animal_str = self.animal_combobox.get()
        if animal_str:
            try:
                animal_id = int(animal_str.split(' - ')[0])
                with Session(engine) as session:
                    animal = session.get(Animal, animal_id)
                    if animal:
                        self.session_peso.config(text=f"{animal.peso_kg} kg")
            except:
                pass    
        
    def carregar_protocolo_sessao(self):
        """Carrega os fármacos de um protocolo na sessão"""
        protocolo_nome = self.protocolo_combobox.get()
        if not protocolo_nome:
            return
            
        protocolo_id = int(protocolo_nome.split(' - ')[0])
        
        with Session(engine) as session:
            protocolo = session.get(Protocolo, protocolo_id)
            if not protocolo:
                return
                
            farmacos = obter_farmacos_do_protocolo(session, protocolo_id)
            
            # Limpar treeview
            for item in self.protocolo_farmacos_tree.get_children():
                self.protocolo_farmacos_tree.delete(item)
                
            # Calcular doses para cada fármaco
            animal_str = self.animal_combobox.get()
            if not animal_str:
                messagebox.showinfo("Info", "Selecione um animal primeiro")
                return
                
            animal_id = int(animal_str.split(' - ')[0])
            animal = session.get(Animal, animal_id)
            
        for farmaco, ordem in farmacos:
        # Cálculo da dose
            if farmaco.modo_uso == "bolus":
                dose_ml = (animal.peso_kg * farmaco.dose) / farmaco.concentracao
                dose_text = f"{dose_ml:.2f} ml"
            else:  # infusão contínua
                multiplicador = 60 if "min" in farmaco.unidade_dose else 1
                taxa_ml_h = (animal.peso_kg * farmaco.dose * multiplicador) / farmaco.concentracao
                dose_ml = taxa_ml_h  # Para cálculo de volume se necessário
                dose_text = f"Taxa: {taxa_ml_h:.2f} ml/h"
            
            self.protocolo_farmacos_tree.insert('', 'end', values=(
                farmaco.nome,
                f"{farmaco.dose} {farmaco.unidade_dose}",
                farmaco.modo_uso,
                dose_text
            ))  

    def generate_protocol_prescription(self):
        """Gera prescrição para o protocolo selecionado"""
        try:
            # Obter animal selecionado
            animal_str = self.animal_combobox.get()
            if not animal_str:
                messagebox.showerror("Erro", "Selecione um animal!")
                return
            animal_id = int(animal_str.split(' - ')[0])
            
            # Obter protocolo selecionado
            protocolo_str = self.protocolo_combobox.get()
            if not protocolo_str:
                messagebox.showerror("Erro", "Selecione um protocolo!")
                return
            protocolo_id = int(protocolo_str.split(' - ')[0])
            
            with Session(engine) as session:
                animal = session.get(Animal, animal_id)
                protocolo = session.get(Protocolo, protocolo_id)
                farmacos = obter_farmacos_do_protocolo(session, protocolo_id)
                
                if not animal or not protocolo or not farmacos:
                    messagebox.showerror("Erro", "Dados incompletos para gerar prescrição!")
                    return
                
                # Gerar conteúdo da prescrição
                conteudo = f"PRESCRIÇÃO ANESTÉSICA - Protocolo: {protocolo.nome}\n"
                conteudo += "="*50 + "\n"
                conteudo += f"Animal: {animal.nome} ({animal.especie})\n"
                conteudo += f"Peso: {animal.peso_kg} kg\n"
                conteudo += f"Data: {datetime.now().strftime('%d/%m/%Y %H:%M')}\n\n"
                conteudo += "MEDICAÇÕES:\n"
                
                for farmaco, ordem in farmacos:
                    if farmaco.modo_uso == "bolus":
                        dose_ml = (animal.peso_kg * farmaco.dose) / farmaco.concentracao
                    else:
                        multiplicador = 60 if "min" in farmaco.unidade_dose else 1
                        dose_ml = (animal.peso_kg * farmaco.dose * multiplicador) / farmaco.concentracao
                    
                    conteudo += f"\n- {farmaco.nome}:\n"
                    conteudo += f"  Dose: {farmaco.dose} {farmaco.unidade_dose}\n"
                    conteudo += f"  Volume a administrar: {dose_ml:.2f} ml\n"
                    conteudo += f"  Modo de uso: {farmaco.modo_uso}\n"
                
                # Salvar arquivo
                os.makedirs("prescricoes", exist_ok=True)
                nome_arquivo = f"prescricoes/protocolo_{protocolo_id}_{animal_id}.txt"
                
                with open(nome_arquivo, "w", encoding="utf-8") as f:
                    f.write(conteudo)
                
                messagebox.showinfo("Sucesso", f"Prescrição gerada em:\n{nome_arquivo}")
                
        except Exception as e:
            messagebox.showerror("Erro", f"Falha ao gerar prescrição: {str(e)}")

    def toggle_infusion_fields(self, event):
        modo = self.infusion_modo.get()
        if "Solução" in modo:
            self.infusion_volume_label.grid()  # Mostrar campo volume
            self.infusion_volume.grid()
        else:
            self.infusion_volume_label.grid_remove()  # Esconder campo volume
            self.infusion_volume.grid_remove()
            

    def create_infusion_tab(self):
        """Cria a aba de configuração de infusão contínua"""
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="💉 Infusão")
        
        form_frame = ttk.LabelFrame(frame, text="Configuração de Infusão Contínua", padding=10)
        form_frame.pack(fill='x', pady=5)
        
        # Seleção de fármaco
        ttk.Label(form_frame, text="Fármaco:").grid(row=0, column=0, sticky='e', padx=5, pady=2)
        self.farmaco_combobox_infusao = ttk.Combobox(form_frame, state='readonly', width=40)
        self.farmaco_combobox_infusao.grid(row=0, column=1, sticky='w', padx=5, pady=2)
        self.farmaco_combobox_infusao.bind('<<ComboboxSelected>>', self.on_farmaco_selected_infusao)
        
        # Exibição da dose padrão
        ttk.Label(form_frame, text="Dose padrão:").grid(row=1, column=0, sticky='e', padx=5, pady=2)
        self.farmaco_dose_label = ttk.Label(form_frame, text="")
        self.farmaco_dose_label.grid(row=1, column=1, sticky='w', padx=5, pady=2)
        
        # Seleção de dose para fármacos com doses variáveis
        ttk.Label(form_frame, text="Selecionar dose:").grid(row=2, column=0, sticky='e', padx=5, pady=2)
        self.dose_var = tk.StringVar()
        self.dose_combobox = ttk.Combobox(form_frame, textvariable=self.dose_var, state='readonly', width=10)
        self.dose_combobox.grid(row=2, column=1, sticky='w', padx=5, pady=2)
        self.dose_combobox.grid_remove()  # Escondido inicialmente
        
        # Peso do paciente
        ttk.Label(form_frame, text="Peso (kg):").grid(row=3, column=0, sticky='e', padx=5, pady=2)
        self.infusion_peso = ttk.Entry(form_frame, width=10)
        self.infusion_peso.grid(row=3, column=1, sticky='w', padx=5, pady=2)

        # Peso do paciente (só obrigatório para modo peso)
        ttk.Label(form_frame, text="Peso (kg):").grid(row=3, column=0, sticky='e', padx=5, pady=2)
        self.infusion_peso = ttk.Entry(form_frame, width=10)
        self.infusion_peso.grid(row=3, column=1, sticky='w', padx=5, pady=2)
        
        # Adicionar validação
        self.infusion_peso.bind("<FocusOut>", self.validate_peso_field)
        
        # Volume da bolsa
        ttk.Label(form_frame, text="Volume da bolsa (ml):").grid(row=4, column=0, sticky='e', padx=5, pady=2)
        self.infusion_volume = ttk.Combobox(form_frame, values=[20, 50, 100, 250, 500, 1000], width=8)
        self.infusion_volume.grid(row=4, column=1, sticky='w', padx=5, pady=2)
        self.infusion_volume.current(0)
        
        # Tipo de equipo
        ttk.Label(form_frame, text="Tipo de equipo:").grid(row=5, column=0, sticky='e', padx=5, pady=2)
        self.infusion_equipo = ttk.Combobox(form_frame, values=["Macrogotas (20 gts/ml)", "Microgotas (60 gts/ml)"], width=20)
        self.infusion_equipo.grid(row=5, column=1, sticky='w', padx=5, pady=2)
        self.infusion_equipo.current(0)
        
        # Modo de cálculo
        ttk.Label(form_frame, text="Modo de cálculo:").grid(row=6, column=0, sticky='e', padx=5, pady=2)
        self.infusion_modo = ttk.Combobox(form_frame, values=["Taxa (ml/h) - Baseado no Peso", "Solução - Preparar Mistura"], width=30)
        self.infusion_modo.grid(row=6, column=1, sticky='w', padx=5, pady=2)
        self.infusion_modo.current(0)
        self.infusion_modo.bind("<<ComboboxSelected>>", self.toggle_infusion_fields)
        # Botão de cálculo
        btn_frame = ttk.Frame(form_frame)
        btn_frame.grid(row=7, column=0, columnspan=2, pady=10)
        ttk.Button(btn_frame, text="Calcular Infusão", command=self.calculate_infusion).pack(side='left', padx=5)
        
        # Resultados
        results_frame = ttk.LabelFrame(form_frame, text="Resultados", padding=10)
        results_frame.grid(row=8, column=0, columnspan=2, sticky='ew', pady=5)
        
        ttk.Label(results_frame, text="Taxa de infusão:").grid(row=0, column=0, sticky='e', padx=5, pady=2)
        self.result_taxa = ttk.Label(results_frame, text="", style='Header.TLabel')
        self.result_taxa.grid(row=0, column=1, sticky='w', padx=5, pady=2)
        
        ttk.Label(results_frame, text="Gotas/min:").grid(row=1, column=0, sticky='e', padx=5, pady=2)
        self.result_gotas = ttk.Label(results_frame, text="")
        self.result_gotas.grid(row=1, column=1, sticky='w', padx=5, pady=2)
        
        ttk.Label(results_frame, text="Duração estimada:").grid(row=2, column=0, sticky='e', padx=5, pady=2)
        self.result_duracao = ttk.Label(results_frame, text="")
        self.result_duracao.grid(row=2, column=1, sticky='w', padx=5, pady=2)
        
        # Carregar fármacos
        self.load_farmacos_infusao()

    def validate_peso_field(self, event):
        if self.infusion_modo.get().lower() == "peso":
            try:
                float(self.infusion_peso.get())
            except:
                messagebox.showerror("Erro", "Digite um peso válido para modo 'Peso'")
                self.infusion_peso.focus_set()

    def create_formulas_panel(self):
        """Cria o painel de fórmulas no canto inferior direito"""
        formula_frame = ttk.LabelFrame(self.main_frame, text="Fórmulas Utilizadas", padding=10)
        formula_frame.place(relx=0.75, rely=0.7, relwidth=0.25, relheight=0.3, anchor='nw')
        
        self.formula_text = tk.Text(formula_frame, wrap=tk.WORD, height=10, width=40)
        self.formula_text.pack(fill='both', expand=True)
        
        formulas = """
        [Formatação de Duração]
        Horas Inteiras = Parte inteira do valor
        Minutos = (Parte decimal × 60)
        
        [Infusão Específica]
        Volume do fármaco (ml) = (Dose × Peso × Volume Bolsa) / Concentração
        Taxa (ml/h) = (Dose × Peso) / Concentração
        Gotas/min = (Taxa × Fator Equipo) / 60
        """
        
        self.formula_text.insert(tk.END, formulas)
        self.formula_text.config(state=tk.DISABLED)
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
        """Janela para cadastrar novo fármaco com doses variáveis"""
        cadastro_window = tk.Toplevel(self.root)
        cadastro_window.title("Cadastrar Novo Fármaco")
        cadastro_window.geometry("500x500")
    
        
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

        ttk.Label(cadastro_window, text="Doses variáveis (separadas por vírgula):").pack()
        doses_variaveis_entry = ttk.Entry(cadastro_window, width=30)
        doses_variaveis_entry.pack()
        
        
        def salvar_farmaco():
            try:
                farmaco = Farmaco(
                    nome=nome_var.get(),
                    dose=float(dose_var.get()),
                    concentracao=float(conc_var.get()),
                    unidade_dose=unidade_var.get(),
                    modo_uso=modo_var.get(),
                    volume_seringa=float(volume_var.get()) if volume_var.get() else None,
                    comentario=comentario_entry.get("1.0", tk.END).strip() or None,
                    doses_variaveis=doses_variaveis_entry.get().strip() or None
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

    def load_farmacos_infusao(self):
        """Carrega fármacos na combobox de infusão"""
        with Session(engine) as session:
            farmacos = session.exec(select(Farmaco)).all()
            self.farmaco_combobox_infusao['values'] = [f"{f.id} - {f.nome}" for f in farmacos]
    
    def on_farmaco_selected_infusao(self, event):
        farmaco_str = self.farmaco_combobox_infusao.get()
        if not farmaco_str:
            return
            
        farmaco_id = int(farmaco_str.split(' - ')[0])
        
        with Session(engine) as session:
            farmaco = session.get(Farmaco, farmaco_id)
            if farmaco:
                self.farmaco_dose_label.config(text=f"{farmaco.dose} {farmaco.unidade_dose}")
                
                 # Atualizar combobox de doses se houver doses variáveis
            if farmaco.doses_variaveis:
                doses = [d.strip() for d in farmaco.doses_variaveis.split(',')]
                self.dose_combobox['values'] = doses
                self.dose_combobox.current(0)
                self.dose_combobox.grid()
            else:
                self.dose_combobox.grid_remove()
        

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
            
    def atualizar_campos_infusao(self, event):
        """Mostra/oculta campos com base no tipo de infusão selecionado"""
        tipo = self.infusion_tipo.get()
        if tipo == "Padrão":
            self.ocultar_campos_especificos()
        else:
            self.mostrar_campos_especificos()
            
    
    def calculate_infusion(self):
        try:
            farmaco_str = self.farmaco_combobox_infusao.get()
            if not farmaco_str:
                messagebox.showerror("Erro", "Selecione um fármaco primeiro!")
                return
                
            farmaco_id = int(farmaco_str.split(' - ')[0])
            
            # Obter valores dos campos
            try:
                peso = float(self.infusion_peso.get())
                taxa = float(self.infusion_taxa.get())  # Nova entrada: taxa ml/kg/h
                volume_bolsa = float(self.infusion_volume.get())
                if peso <= 0 or volume_bolsa <= 0 or taxa <= 0:
                    raise ValueError("Valores devem ser positivos")
            except:
                messagebox.showerror("Erro", "Digite valores válidos para peso, taxa e volume")
                return
            
            equipo = self.infusion_equipo.get()
            equipo_tipo = "microgotas" if "Micro" in equipo else "macrogotas"
            
            with Session(engine) as session:
                farmaco = session.get(Farmaco, farmaco_id)
                if not farmaco:
                    messagebox.showerror("Erro", "Fármaco não encontrado!")
                    return
                
                # Chamar função de cálculo
                resultados = calcular_infusao_planilha(
                    peso_kg=peso,
                    taxa_ml_kg_h=taxa,
                    volume_bolsa_ml=volume_bolsa,
                    equipo_tipo=equipo_tipo,
                    dose_farmaco=farmaco.dose,
                    unidade_dose=farmaco.unidade_dose,
                    concentracao=farmaco.concentracao
                )
                
                # Exibir resultados
                self.result_taxa.config(text=f"{resultados['vazao_ml_h']:.2f} ml/h")
                self.result_gotas.config(text=f"{resultados['gotas_min']:.2f} gts/min")
                self.result_duracao.config(text=resultados['duracao_h'])
                
                # Mostrar detalhes do fármaco
                details = (
                    f"Dose Total: {resultados['dose_total_ug']:.2f} µg\n"
                    f"Volume Fármaco: {resultados['volume_farmaco_ml']:.4f} ml"
                )
                self.formula_text.config(state=tk.NORMAL)
                self.formula_text.delete(1.0, tk.END)
                self.formula_text.insert(tk.END, details)
                self.formula_text.config(state=tk.DISABLED)
                    
        except Exception as e:
            messagebox.showerror("Erro", f"Falha ao calcular infusão: {str(e)}")
            import traceback
            traceback.print_exc()
    def calcular_infusao_especifica(
        peso_kg: float, 
        dose_mcg_kg_h: float, 
        concentracao_mcg_ml: float,
        volume_seringa_ml: float = 20.0,
        equipo_tipo: str = "macrogotas"
    ) -> dict:
        """
        Calcula parâmetros para infusões específicas como Remifentanil, Lidocaína, Cetamina
        
        Fórmulas:
        Volume do fármaco (ml) = (Dose * Peso * Volume da seringa) / Concentração
        Taxa de infusão (ml/h) = (Dose * Peso) / Concentração
        """
        # Cálculo do volume do fármaco na seringa
        volume_farmaco_ml = (dose_mcg_kg_h * peso_kg * volume_seringa_ml) / concentracao_mcg_ml
        
        # Verificar se o volume do fármaco não excede a capacidade da seringa
        if volume_farmaco_ml > volume_seringa_ml:
            raise ValueError("Volume do fármaco excede a capacidade da seringa!")
        
        # Cálculo da taxa de infusão em ml/h
        taxa_ml_h = (dose_mcg_kg_h * peso_kg) / concentracao_mcg_ml
        
        # Cálculo de gotas/min
        fator = 20 if equipo_tipo == "macrogotas" else 60
        gotas_min = (taxa_ml_h * fator) / 60
        
        return {
            'volume_farmaco_ml': volume_farmaco_ml,
            'volume_dilente_ml': volume_seringa_ml - volume_farmaco_ml,
            'taxa_ml_h': taxa_ml_h,
            'gotas_min': gotas_min,
            'fator_equipo': fator
        }        
            
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
            if hasattr(sessao, 'id_protocolo') and sessao.id_protocolo:
                protocolo = session.get(Protocolo, sessao.id_protocolo)
                conteudo += f"\n📋 PROTOCOLO UTILIZADO: {protocolo.nome}\n"
                farmacos_protocolo = obter_farmacos_do_protocolo(session, protocolo.id)
                
                for farmaco, ordem in farmacos_protocolo:
                    # Cálculo da dose para o animal
                    if animal:
                        if farmaco.modo_uso == "bolus":
                            dose_ml = (animal.peso_kg * farmaco.dose) / farmaco.concentracao
                        else:
                            mult = 60 if "min" in farmaco.unidade_dose else 1
                            dose_ml = (animal.peso_kg * farmaco.dose * mult) / farmaco.concentracao
                        
                        conteudo += (
                            f"\n - {farmaco.nome}: {dose_ml:.2f}ml "
                            f"({farmaco.dose} {farmaco.unidade_dose})"
                        )    
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
    
    root.mainloop() 