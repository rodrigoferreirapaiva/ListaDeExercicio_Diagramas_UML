import streamlit as st
import pandas as pd
import hashlib
from datetime import datetime

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Sistema de Gerenciamento Corporativo", layout="wide")

# --- SIMULAÇÃO DE BANCO DE DADOS (STATE) ---
# Em um ambiente de produção, substituiríamos isso por conexões reais (ex: PostgreSQL/SQL Server)
def init_db():
    tabelas = {
        'usuarios': pd.DataFrame(columns=['login', 'senha_hash']),
        'pessoas': pd.DataFrame(columns=['id', 'nome', 'dtnasc']),
        'enderecos': pd.DataFrame(columns=['cod', 'pessoa_id', 'logradouro', 'bairro']),
        'telefones': pd.DataFrame(columns=['pessoa_id', 'ddd', 'ddi', 'numero']),
        'cargos': pd.DataFrame(columns=['id_cargo', 'nome_cargo']),
        'profissoes': pd.DataFrame(columns=['id_prof', 'nome_prof']),
        'funcionarios': pd.DataFrame(columns=['matricula', 'pessoa_id', 'cargo_id', 'salario', 'dt_admin']),
        'clientes': pd.DataFrame(columns=['cod', 'pessoa_id', 'limite_cred', 'dt_compra'])
    }
    for nome, df in tabelas.items():
        if nome not in st.session_state:
            st.session_state[nome] = df

init_db()

# --- RNF001: SEGURANÇA (CRIPTOGRAFIA) ---
def hash_senha(senha: str) -> str:
    """Retorna o hash SHA-256 da senha."""
    return hashlib.sha256(senha.encode()).hexdigest()

# --- FUNÇÕES AUXILIARES ---
def salvar_registro(tabela: str, dados: dict):
    novo_df = pd.DataFrame([dados])
    st.session_state[tabela] = pd.concat([st.session_state[tabela], novo_df], ignore_index=True)
    st.success("Registro salvo com sucesso!")

# --- INTERFACE DO USUÁRIO ---
st.title("💻 Sistema de Gerenciamento")

st.sidebar.header("Navegação")
menu = st.sidebar.radio(
    "Módulos do Sistema",
    [
        "Segurança (RNF001)",
        "RF001 - Gerenciar Pessoa",
        "RF002 - Gerenciar Endereço",
        "RF003 - Gerenciar Telefone",
        "RF005 - Gerenciar Cargo",
        "RF007 - Gerenciar Profissão",
        "RF004 - Gerenciar Funcionário",
        "RF006 - Gerenciar Cliente"
    ]
)

# --- MÓDULO: SEGURANÇA / USUÁRIOS ---
if menu == "Segurança (RNF001)":
    st.header("Gestão de Acesso Segura")
    st.info("Demonstração do RNF001: As senhas são criptografadas antes de serem salvas.")
    
    with st.form("form_usuario"):
        login = st.text_input("Login")
        senha = st.text_input("Senha", type="password")
        if st.form_submit_button("Cadastrar Usuário"):
            if login and senha:
                salvar_registro('usuarios', {'login': login, 'senha_hash': hash_senha(senha)})
            else:
                st.error("Preencha todos os campos.")
                
    st.write("Usuários no Banco (Senhas Criptografadas):")
    st.dataframe(st.session_state['usuarios'])

# --- MÓDULO: PESSOA ---
elif menu == "RF001 - Gerenciar Pessoa":
    st.header("RF001 - Pessoas (Entidade Base)")
    
    with st.form("form_pessoa"):
        nome = st.text_input("Nome")
        dtnasc = st.date_input("Data de Nascimento")
        if st.form_submit_button("Salvar Pessoa"):
            novo_id = len(st.session_state['pessoas']) + 1
            salvar_registro('pessoas', {'id': novo_id, 'nome': nome, 'dtnasc': dtnasc})
            
    st.dataframe(st.session_state['pessoas'])

# --- MÓDULO: ENDEREÇO ---
elif menu == "RF002 - Gerenciar Endereço":
    st.header("RF002 - Endereços")
    pessoas_disponiveis = st.session_state['pessoas']['id'].tolist()
    
    with st.form("form_endereco"):
        pessoa_id = st.selectbox("ID da Pessoa", pessoas_disponiveis)
        cod = st.number_input("Código do Endereço", min_value=1, step=1)
        logradouro = st.text_input("Logradouro")
        bairro = st.text_input("Bairro")
        if st.form_submit_button("Salvar Endereço") and pessoas_disponiveis:
            salvar_registro('enderecos', {'cod': cod, 'pessoa_id': pessoa_id, 'logradouro': logradouro, 'bairro': bairro})
            
    st.dataframe(st.session_state['enderecos'])

# --- MÓDULO: TELEFONE ---
elif menu == "RF003 - Gerenciar Telefone":
    st.header("RF003 - Telefones")
    pessoas_disponiveis = st.session_state['pessoas']['id'].tolist()
    
    with st.form("form_telefone"):
        pessoa_id = st.selectbox("ID da Pessoa", pessoas_disponiveis)
        ddi = st.text_input("DDI (ex: +55)")
        ddd = st.text_input("DDD (ex: 11)")
        numero = st.text_input("Número")
        if st.form_submit_button("Salvar Telefone") and pessoas_disponiveis:
            salvar_registro('telefones', {'pessoa_id': pessoa_id, 'ddd': ddd, 'ddi': ddi, 'numero': numero})
            
    st.dataframe(st.session_state['telefones'])

# --- MÓDULO: CARGO ---
elif menu == "RF005 - Gerenciar Cargo":
    st.header("RF005 - Cargos")
    
    with st.form("form_cargo"):
        id_cargo = st.number_input("ID do Cargo", min_value=1, step=1)
        nome_cargo = st.text_input("Nome do Cargo")
        if st.form_submit_button("Salvar Cargo"):
            salvar_registro('cargos', {'id_cargo': id_cargo, 'nome_cargo': nome_cargo})
            
    st.dataframe(st.session_state['cargos'])

# --- MÓDULO: PROFISSÃO ---
elif menu == "RF007 - Gerenciar Profissão":
    st.header("RF007 - Profissões")
    
    with st.form("form_profissao"):
        id_prof = st.number_input("ID da Profissão", min_value=1, step=1)
        nome_prof = st.text_input("Nome da Profissão")
        if st.form_submit_button("Salvar Profissão"):
            salvar_registro('profissoes', {'id_prof': id_prof, 'nome_prof': nome_prof})
            
    st.dataframe(st.session_state['profissoes'])

# --- MÓDULO: FUNCIONÁRIO ---
elif menu == "RF004 - Gerenciar Funcionário":
    st.header("RF004 - Funcionários (Herda de Pessoa)")
    pessoas_disp = st.session_state['pessoas']['id'].tolist()
    cargos_disp = st.session_state['cargos']['id_cargo'].tolist()
    
    with st.form("form_funcionario"):
        pessoa_id = st.selectbox("ID da Pessoa (Herança)", pessoas_disp)
        cargo_id = st.selectbox("ID do Cargo", cargos_disp)
        matricula = st.text_input("Matrícula")
        salario = st.number_input("Salário", min_value=0.0, format="%.2f")
        dt_admin = st.date_input("Data de Admissão")
        
        if st.form_submit_button("Salvar Funcionário"):
            if not pessoas_disp or not cargos_disp:
                st.error("É necessário ter uma Pessoa e um Cargo cadastrados primeiro.")
            else:
                salvar_registro('funcionarios', {
                    'matricula': matricula, 'pessoa_id': pessoa_id, 
                    'cargo_id': cargo_id, 'salario': salario, 'dt_admin': dt_admin
                })
                
    st.dataframe(st.session_state['funcionarios'])

# --- MÓDULO: CLIENTE ---
elif menu == "RF006 - Gerenciar Cliente":
    st.header("RF006 - Clientes (Herda de Pessoa)")
    pessoas_disp = st.session_state['pessoas']['id'].tolist()
    
    with st.form("form_cliente"):
        pessoa_id = st.selectbox("ID da Pessoa (Herança)", pessoas_disp)
        cod = st.number_input("Código do Cliente", min_value=1, step=1)
        limite_cred = st.number_input("Limite de Crédito", min_value=0.0, format="%.2f")
        dt_compra = st.date_input("Data da Última Compra")
        
        if st.form_submit_button("Salvar Cliente"):
            if not pessoas_disp:
                st.error("É necessário cadastrar uma Pessoa primeiro.")
            else:
                salvar_registro('clientes', {
                    'cod': cod, 'pessoa_id': pessoa_id,
                    'limite_cred': limite_cred, 'dt_compra': dt_compra
                })
                
    st.dataframe(st.session_state['clientes'])
