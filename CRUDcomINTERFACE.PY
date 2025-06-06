import datetime
import pandas as pd
import tkinter as tk
from tkinter import messagebox, simpledialog, Toplevel, Label, Entry, Button, ttk
import sqlite3

# --- Global dictionaries (now primarily for in-memory caching) ---
usuarios = {}
locais = {}
DB_NAME = 'vertical_farm.db'

# --- Hardcoded Admin Credentials ---
ADMIN_EMAIL = "admin"
ADMIN_PASSWORD = "admin"

# --- Database Functions ---
def create_tables():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    # Removed registered_users table as roles are now handled by hardcoded admin login

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS usuarios (
            nome TEXT PRIMARY KEY,
            idade INTEGER,
            endereco TEXT,
            pessoas_casa INTEGER,
            renda REAL,
            profissao TEXT,
            apto TEXT,
            local_designado TEXT,
            prazo_comparecimento TEXT
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS locais (
            nome_local TEXT PRIMARY KEY,
            endereco TEXT,
            responsavel TEXT,
            contato TEXT,
            andares INTEGER,
            area REAL,
            capacidade_producao REAL,
            apto TEXT,
            mensagem TEXT
        )
    ''')
    conn.commit()
    conn.close()

def save_user_to_db(user_data):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT OR REPLACE INTO usuarios (nome, idade, endereco, pessoas_casa, renda, profissao, apto, local_designado, prazo_comparecimento)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (user_data['nome'], user_data['idade'], user_data['endereco'], user_data['pessoas_casa'],
          user_data['renda'], user_data['profissao'], user_data['apto'], user_data['local_designado'],
          user_data['prazo_comparecimento']))
    conn.commit()
    conn.close()

def delete_user_from_db(nome):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('DELETE FROM usuarios WHERE nome = ?', (nome,))
    conn.commit()
    conn.close()

def save_local_to_db(local_data):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT OR REPLACE INTO locais (nome_local, endereco, responsavel, contato, andares, area, capacidade_producao, apto, mensagem)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (local_data['nome_local'], local_data['endereco'], local_data['responsavel'],
          local_data['contato'], local_data['andares'], local_data['area'],
          local_data['capacidade_producao'], local_data['apto'], local_data['mensagem']))
    conn.commit()
    conn.close()

def delete_local_from_db(nome_local):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('DELETE FROM locais WHERE nome_local = ?', (nome_local,))
    conn.commit()
    conn.close()

def load_data():
    global usuarios, locais
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    # Load usuarios
    cursor.execute('SELECT * FROM usuarios')
    for row in cursor.fetchall():
        user_dict = {
            "nome": row[0],
            "idade": row[1],
            "endereco": row[2],
            "pessoas_casa": row[3],
            "renda": row[4],
            "profissao": row[5],
            "apto": row[6],
            "local_designado": row[7],
            "prazo_comparecimento": row[8]
        }
        usuarios[row[0]] = user_dict

    # Load locais
    cursor.execute('SELECT * FROM locais')
    for row in cursor.fetchall():
        local_dict = {
            "nome_local": row[0],
            "endereco": row[1],
            "responsavel": row[2],
            "contato": row[3],
            "andares": row[4],
            "area": row[5],
            "capacidade_producao": row[6],
            "apto": row[7],
            "mensagem": row[8]
        }
        locais[row[0]] = local_dict
    conn.close()

def verificar_aptidao_usuario(idade, renda):
    return idade >= 18 and renda <= 2000

def calcular_capacidade_producao(andares, area):
    return andares * area * 2

# --- Login Function ---
def login_user_gui():
    def login():
        email = email_entry.get()
        password = password_entry.get()

        if email == ADMIN_EMAIL and password == ADMIN_PASSWORD:
            current_user_info['role'] = 'colaborador'
            messagebox.showinfo("Login", f"Bem-vindo, {email}! Você é um Colaborador.")
            login_window.destroy()
            show_main_menu()
        else:
            current_user_info['role'] = 'usuario'
            messagebox.showinfo("Login", f"Bem-vindo, {email}! Você é um Usuário comum.")
            login_window.destroy()
            show_main_menu()

    login_window = Toplevel(root)
    login_window.title("Login")
    login_window.geometry("300x150")

    Label(login_window, text="Email:").pack(pady=5)
    email_entry = Entry(login_window)
    email_entry.pack(pady=5)

    Label(login_window, text="Senha:").pack(pady=5)
    password_entry = Entry(login_window, show="*")
    password_entry.pack(pady=5)

    Button(login_window, text="Entrar", command=login).pack(pady=10)

# --- User Management Functions (GUI) ---
def add_user_gui():
    def add():
        nome = nome_entry.get()
        try:
            idade = int(idade_entry.get())
            endereco = endereco_entry.get()
            pessoas_casa = int(pessoas_casa_entry.get())
            renda = float(renda_entry.get())
            profissao = profissao_entry.get()
        except ValueError:
            messagebox.showerror("Erro", "Por favor, insira valores numéricos válidos para idade, pessoas na casa e renda.")
            return
        
        if nome in usuarios:
            messagebox.showerror("Erro", "Já existe um usuário com este nome.")
            return

        # Calculate apto, local_designado, prazo_comparecimento
        apto_status = verificar_aptidao_usuario(idade, renda)
        local_designado_val = endereco if apto_status else "N/A"
        prazo_comparecimento_val = (datetime.date.today() + datetime.timedelta(days=15)).isoformat() if apto_status else "N/A"

        usuario = {
            "nome": nome,
            "idade": idade,
            "endereco": endereco,
            "pessoas_casa": pessoas_casa,
            "renda": renda,
            "profissao": profissao,
            "apto": "Sim" if apto_status else "Não", # Store as "Sim" or "Não" for display
            "local_designado": local_designado_val,
            "prazo_comparecimento": prazo_comparecimento_val
        }
        
        save_user_to_db(usuario) # Save to database
        usuarios[nome] = usuario # Update in-memory
        messagebox.showinfo("Sucesso", "Usuário adicionado com sucesso!")
        add_user_window.destroy()
        list_users_gui() # Refresh the list

    add_user_window = Toplevel(root)
    add_user_window.title("Adicionar Usuário")
    add_user_window.geometry("350x400")

    Label(add_user_window, text="Nome:").pack(pady=2)
    nome_entry = Entry(add_user_window)
    nome_entry.pack(pady=2)

    Label(add_user_window, text="Idade:").pack(pady=2)
    idade_entry = Entry(add_user_window)
    idade_entry.pack(pady=2)

    Label(add_user_window, text="Endereço:").pack(pady=2)
    endereco_entry = Entry(add_user_window)
    endereco_entry.pack(pady=2)

    Label(add_user_window, text="Pessoas na casa:").pack(pady=2)
    pessoas_casa_entry = Entry(add_user_window)
    pessoas_casa_entry.pack(pady=2)

    Label(add_user_window, text="Renda familiar:").pack(pady=2)
    renda_entry = Entry(add_user_window)
    renda_entry.pack(pady=2)

    Label(add_user_window, text="Profissão:").pack(pady=2)
    profissao_entry = Entry(add_user_window)
    profissao_entry.pack(pady=2)

    Button(add_user_window, text="Adicionar", command=add).pack(pady=10)

def list_users_gui():
    list_users_window = Toplevel(root)
    list_users_window.title("Lista de Usuários")
    list_users_window.geometry("800x400")

    if not usuarios:
        Label(list_users_window, text="Nenhum usuário cadastrado.").pack(pady=20)
        return

    df = pd.DataFrame(usuarios.values())
    
    tree = ttk.Treeview(list_users_window, columns=list(df.columns), show='headings')
    tree.pack(fill='both', expand=True)

    for col in df.columns:
        tree.heading(col, text=col)
        tree.column(col, width=100)

    for index, row in df.iterrows():
        tree.insert("", "end", values=list(row))

    if current_user_info['role'] == 'colaborador':
        Button(list_users_window, text="Atualizar Usuário Selecionado", command=lambda: update_user_gui(tree)).pack(pady=10)
        Button(list_users_window, text="Remover Usuário Selecionado", command=lambda: remove_user_gui(tree)).pack(pady=5)

def update_user_gui(tree_widget):
    if current_user_info['role'] != 'colaborador':
        messagebox.showwarning("Acesso Negado", "Você não tem permissão para atualizar usuários.")
        return

    selected_item = tree_widget.selection()
    if not selected_item:
        messagebox.showwarning("Atenção", "Selecione um usuário para atualizar.")
        return

    values = tree_widget.item(selected_item, 'values')
    nome_to_update = values[0]

    if nome_to_update not in usuarios:
        messagebox.showerror("Erro", "Usuário não encontrado na base de dados.")
        return

    user_data = usuarios[nome_to_update]

    def update():
        try:
            new_idade = idade_entry.get()
            if new_idade: user_data['idade'] = int(new_idade)

            new_endereco = endereco_entry.get()
            if new_endereco: user_data['endereco'] = new_endereco

            new_pessoas_casa = pessoas_casa_entry.get()
            if new_pessoas_casa: user_data['pessoas_casa'] = int(new_pessoas_casa)

            new_renda = renda_entry.get()
            if new_renda: user_data['renda'] = float(new_renda)

            new_profissao = profissao_entry.get()
            if new_profissao: user_data['profissao'] = new_profissao

            apto_status = verificar_aptidao_usuario(user_data['idade'], user_data['renda'])
            user_data['apto'] = "Sim" if apto_status else "Não"
            user_data['local_designado'] = user_data['endereco'] if apto_status else "N/A"
            user_data['prazo_comparecimento'] = (datetime.date.today() + datetime.timedelta(days=30)).isoformat() if apto_status else "N/A"

            save_user_to_db(user_data)
            messagebox.showinfo("Sucesso", "Usuário atualizado com sucesso!")
            update_user_window.destroy()
            for widget in root.winfo_children():
                if isinstance(widget, Toplevel) and widget.title() == "Lista de Usuários":
                    widget.destroy()
                    break
            list_users_gui()

        except ValueError:
            messagebox.showerror("Erro", "Por favor, insira valores numéricos válidos.")

    update_user_window = Toplevel(root)
    update_user_window.title(f"Atualizar Usuário: {nome_to_update}")
    update_user_window.geometry("350x450")

    Label(update_user_window, text=f"Nome: {nome_to_update}").pack(pady=5)
    Label(update_user_window, text="Deixe em branco para manter o valor atual.").pack(pady=5)

    Label(update_user_window, text=f"Nova idade (atual: {user_data['idade']}):").pack(pady=2)
    idade_entry = Entry(update_user_window)
    idade_entry.pack(pady=2)
    idade_entry.insert(0, str(user_data['idade']))

    Label(update_user_window, text=f"Novo endereço (atual: {user_data['endereco']}):").pack(pady=2)
    endereco_entry = Entry(update_user_window)
    endereco_entry.pack(pady=2)
    endereco_entry.insert(0, str(user_data['endereco']))

    Label(update_user_window, text=f"Novas pessoas na casa (atual: {user_data['pessoas_casa']}):").pack(pady=2)
    pessoas_casa_entry = Entry(update_user_window)
    pessoas_casa_entry.pack(pady=2)
    pessoas_casa_entry.insert(0, str(user_data['pessoas_casa']))

    Label(update_user_window, text=f"Nova renda (atual: {user_data['renda']}):").pack(pady=2)
    renda_entry = Entry(update_user_window)
    renda_entry.pack(pady=2)
    renda_entry.insert(0, str(user_data['renda']))

    Label(update_user_window, text=f"Nova profissão (atual: {user_data['profissao']}):").pack(pady=2)
    profissao_entry = Entry(update_user_window)
    profissao_entry.pack(pady=2)
    profissao_entry.insert(0, str(user_data['profissao']))

    Button(update_user_window, text="Atualizar", command=update).pack(pady=10)

def remove_user_gui(tree_widget):
    if current_user_info['role'] != 'colaborador':
        messagebox.showwarning("Acesso Negado", "Você não tem permissão para remover usuários.")
        return

    selected_item = tree_widget.selection()
    if not selected_item:
        messagebox.showwarning("Atenção", "Selecione um usuário para remover.")
        return

    values = tree_widget.item(selected_item, 'values')
    nome_to_remove = values[0]

    if messagebox.askyesno("Confirmar Remoção", f"Tem certeza que deseja remover {nome_to_remove}?"):
        delete_user_from_db(nome_to_remove)
        usuarios.pop(nome_to_remove, None)
        messagebox.showinfo("Sucesso", "Usuário removido.")
        tree_widget.delete(selected_item)

# --- Location Management Functions (GUI) ---
def add_local_gui():
    # This function should only be accessible by 'colaborador'
    if current_user_info['role'] != 'colaborador':
        messagebox.showwarning("Acesso Negado", "Você não tem permissão para adicionar locais.")
        return

    def add():
        nome_local = nome_local_entry.get()
        try:
            endereco = endereco_entry.get()
            responsavel = responsavel_entry.get()
            contato = contato_entry.get()
            andares = int(andares_entry.get())
            area = float(area_entry.get())
        except ValueError:
            messagebox.showerror("Erro", "Por favor, insira valores numéricos válidos para andares e área.")
            return

        if nome_local in locais:
            messagebox.showerror("Erro", "Já existe um local com este nome.")
            return

        capacidade = calcular_capacidade_producao(andares, area)
        apto = "Sim" if capacidade >= 1000 else "Não"

        local = {
            "nome_local": nome_local,
            "endereco": endereco,
            "responsavel": responsavel,
            "contato": contato,
            "andares": andares,
            "area": area,
            "capacidade_producao": capacidade,
            "apto": apto,
            "mensagem": "O responsável será contatado para mais informações."
        }
        save_local_to_db(local)
        locais[nome_local] = local
        messagebox.showinfo("Sucesso", "Local adicionado com sucesso!")
        add_local_window.destroy()
        list_locais_gui()

    add_local_window = Toplevel(root)
    add_local_window.title("Adicionar Local")
    add_local_window.geometry("350x400")

    Label(add_local_window, text="Nome do local:").pack(pady=2)
    nome_local_entry = Entry(add_local_window)
    nome_local_entry.pack(pady=2)

    Label(add_local_window, text="Endereço:").pack(pady=2)
    endereco_entry = Entry(add_local_window)
    endereco_entry.pack(pady=2)

    Label(add_local_window, text="Responsável:").pack(pady=2)
    responsavel_entry = Entry(add_local_window)
    responsavel_entry.pack(pady=2)

    Label(add_local_window, text="Contato:").pack(pady=2)
    contato_entry = Entry(add_local_window)
    contato_entry.pack(pady=2)

    Label(add_local_window, text="Quantidade de andares:").pack(pady=2)
    andares_entry = Entry(add_local_window)
    andares_entry.pack(pady=2)

    Label(add_local_window, text="Área do local (m²):").pack(pady=2)
    area_entry = Entry(add_local_window)
    area_entry.pack(pady=2)

    Button(add_local_window, text="Adicionar", command=add).pack(pady=10)

def list_locais_gui():
    list_locais_window = Toplevel(root)
    list_locais_window.title("Lista de Locais")
    list_locais_window.geometry("800x400")

    if not locais:
        Label(list_locais_window, text="Nenhum local cadastrado.").pack(pady=20)
        return

    df = pd.DataFrame(locais.values())
    tree = ttk.Treeview(list_locais_window, columns=list(df.columns), show='headings')
    tree.pack(fill='both', expand=True)

    for col in df.columns:
        tree.heading(col, text=col)
        tree.column(col, width=100)

    for index, row in df.iterrows():
        tree.insert("", "end", values=list(row))

    if current_user_info['role'] == 'colaborador':
        Button(list_locais_window, text="Atualizar Local Selecionado", command=lambda: update_local_gui(tree)).pack(pady=10)
        Button(list_locais_window, text="Remover Local Selecionado", command=lambda: remove_local_gui(tree)).pack(pady=5)

def update_local_gui(tree_widget):
    if current_user_info['role'] != 'colaborador':
        messagebox.showwarning("Acesso Negado", "Você não tem permissão para atualizar locais.")
        return

    selected_item = tree_widget.selection()
    if not selected_item:
        messagebox.showwarning("Atenção", "Selecione um local para atualizar.")
        return

    values = tree_widget.item(selected_item, 'values')
    nome_local_to_update = values[0]

    if nome_local_to_update not in locais:
        messagebox.showerror("Erro", "Local não encontrado na base de dados.")
        return

    local_data = locais[nome_local_to_update]

    def update():
        try:
            new_andares = andares_entry.get()
            if new_andares: local_data['andares'] = int(new_andares)

            new_area = area_entry.get()
            if new_area: local_data['area'] = float(new_area)

            local_data['capacidade_producao'] = calcular_capacidade_producao(local_data['andares'], local_data['area'])
            local_data['apto'] = "Sim" if local_data['capacidade_producao'] >= 1000 else "Não"

            save_local_to_db(local_data)
            messagebox.showinfo("Sucesso", "Local atualizado com sucesso!")
            update_local_window.destroy()
            for widget in root.winfo_children():
                if isinstance(widget, Toplevel) and widget.title() == "Lista de Locais":
                    widget.destroy()
                    break
            list_locais_gui()

        except ValueError:
            messagebox.showerror("Erro", "Por favor, insira valores numéricos válidos.")

    update_local_window = Toplevel(root)
    update_local_window.title(f"Atualizar Local: {nome_local_to_update}")
    update_local_window.geometry("300x200")

    Label(update_local_window, text=f"Nome do Local: {nome_local_to_update}").pack(pady=5)
    Label(update_local_window, text="Deixe em branco para manter o valor atual.").pack(pady=5)

    Label(update_local_window, text=f"Novos andares (atual: {local_data['andares']}):").pack(pady=2)
    andares_entry = Entry(update_local_window)
    andares_entry.pack(pady=2)
    andares_entry.insert(0, str(local_data['andares']))

    Label(update_local_window, text=f"Nova área (atual: {local_data['area']}):").pack(pady=2)
    area_entry = Entry(update_local_window)
    area_entry.pack(pady=2)
    area_entry.insert(0, str(local_data['area']))

    Button(update_local_window, text="Atualizar", command=update).pack(pady=10)

def remove_local_gui(tree_widget):
    if current_user_info['role'] != 'colaborador':
        messagebox.showwarning("Acesso Negado", "Você não tem permissão para remover locais.")
        return

    selected_item = tree_widget.selection()
    if not selected_item:
        messagebox.showwarning("Atenção", "Selecione um local para remover.")
        return

    values = tree_widget.item(selected_item, 'values')
    nome_local_to_remove = values[0]

    if messagebox.askyesno("Confirmar Remoção", f"Tem certeza que deseja remover {nome_local_to_remove}?"):
        delete_local_from_db(nome_local_to_remove)
        locais.pop(nome_local_to_remove, None)
        messagebox.showinfo("Sucesso", "Local removido.")
        tree_widget.delete(selected_item)

# --- Main Menu Functions ---
def show_user_management_menu():
    user_menu_window = Toplevel(root)
    user_menu_window.title("Gerenciar Usuários")
    user_menu_window.geometry("300x300")

    # Both users can add, but with different permissions on the form
    Button(user_menu_window, text="Adicionar Meu Cadastro", command=add_user_gui, pady=5).pack(fill='x', padx=20, pady=5)
    Button(user_menu_window, text="Listar Usuários Cadastrados", command=list_users_gui, pady=5).pack(fill='x', padx=20, pady=5)
    
    # Only show update/remove if the user is a collaborator
    if current_user_info['role'] == 'colaborador':
        Button(user_menu_window, text="Atualizar Usuário Existente", command=lambda: list_users_gui_for_update_or_remove(action='update'), pady=5).pack(fill='x', padx=20, pady=5)
        Button(user_menu_window, text="Remover Usuário Existente", command=lambda: list_users_gui_for_update_or_remove(action='remove'), pady=5).pack(fill='x', padx=20, pady=5)
    
    Button(user_menu_window, text="Voltar", command=user_menu_window.destroy, pady=5).pack(fill='x', padx=20, pady=5)

def list_users_gui_for_update_or_remove(action):
    if current_user_info['role'] != 'colaborador':
        messagebox.showwarning("Acesso Negado", "Você não tem permissão para realizar esta ação.")
        return

    list_window = Toplevel(root)
    list_window.title(f"{'Atualizar' if action == 'update' else 'Remover'} Usuário")
    list_window.geometry("800x400")

    if not usuarios:
        Label(list_window, text="Nenhum usuário cadastrado.").pack(pady=20)
        return

    df = pd.DataFrame(usuarios.values())
    tree = ttk.Treeview(list_window, columns=list(df.columns), show='headings')
    tree.pack(fill='both', expand=True)

    for col in df.columns:
        tree.heading(col, text=col)
        tree.column(col, width=100)

    for index, row in df.iterrows():
        tree.insert("", "end", values=list(row))

    if action == 'update':
        Button(list_window, text="Atualizar Selecionado", command=lambda: update_user_gui(tree)).pack(pady=10)
    elif action == 'remove':
        Button(list_window, text="Remover Selecionado", command=lambda: remove_user_gui(tree)).pack(pady=10)


def show_local_management_menu():
    if current_user_info['role'] != 'colaborador':
        messagebox.showwarning("Acesso Negado", "Você não tem permissão para gerenciar locais.")
        return

    local_menu_window = Toplevel(root)
    local_menu_window.title("Gerenciar Locais para Fazendas Verticais")
    local_menu_window.geometry("300x300")

    Button(local_menu_window, text="Adicionar Local", command=add_local_gui, pady=5).pack(fill='x', padx=20, pady=5)
    Button(local_menu_window, text="Listar Locais", command=list_locais_gui, pady=5).pack(fill='x', padx=20, pady=5)

    # These buttons are always shown if you're a collaborator
    Button(local_menu_window, text="Atualizar Local", command=lambda: list_locais_gui_for_update_or_remove(action='update'), pady=5).pack(fill='x', padx=20, pady=5)
    Button(local_menu_window, text="Remover Local", command=lambda: list_locais_gui_for_update_or_remove(action='remove'), pady=5).pack(fill='x', padx=20, pady=5)

    Button(local_menu_window, text="Voltar", command=local_menu_window.destroy, pady=5).pack(fill='x', padx=20, pady=5)

def list_locais_gui_for_update_or_remove(action):
    if current_user_info['role'] != 'colaborador':
        messagebox.showwarning("Acesso Negado", "Você não tem permissão para realizar esta ação.")
        return

    list_window = Toplevel(root)
    list_window.title(f"{'Atualizar' if action == 'update' else 'Remover'} Local")
    list_window.geometry("800x400")

    if not locais:
        Label(list_window, text="Nenhum local cadastrado.").pack(pady=20)
        return

    df = pd.DataFrame(locais.values())
    tree = ttk.Treeview(list_window, columns=list(df.columns), show='headings')
    tree.pack(fill='both', expand=True)

    for col in df.columns:
        tree.heading(col, text=col)
        tree.column(col, width=100)

    for index, row in df.iterrows():
        tree.insert("", "end", values=list(row))

    if action == 'update':
        Button(list_window, text="Atualizar Selecionado", command=lambda: update_local_gui(tree)).pack(pady=10)
    elif action == 'remove':
        Button(list_window, text="Remover Selecionado", command=lambda: remove_local_gui(tree)).pack(pady=10)


def show_main_menu():
    for widget in root.winfo_children():
        widget.destroy() # Clear previous widgets

    Label(root, text="--- MENU PRINCIPAL ---", font=("Arial", 16)).pack(pady=20)
    
    # User Management is always available
    Button(root, text="Gerenciar Usuários", command=show_user_management_menu, width=30, height=2).pack(pady=10)
    
    # Location Management is only available for collaborators
    if current_user_info['role'] == 'colaborador':
        Button(root, text="Gerenciar Locais para Fazendas Verticais", command=show_local_management_menu, width=30, height=2).pack(pady=10)
    else:
        # Optionally, you can show a disabled button or just omit it for regular users
        Label(root, text="Gerenciamento de Locais (Acesso Restrito)", fg="grey", width=30, height=2).pack(pady=10)

    Button(root, text="Sair", command=root.quit, width=30, height=2).pack(pady=10)

# --- Main Application Setup ---
root = tk.Tk()
root.title("Sistema de Gestão de Fazendas Verticais")
root.geometry("400x400")

# Store current user information (role will be set after login)
current_user_info = {'email': None, 'role': None}

# Initialize database and load existing data
create_tables()
load_data()

# Initial state: show login screen
login_user_gui()

root.mainloop()