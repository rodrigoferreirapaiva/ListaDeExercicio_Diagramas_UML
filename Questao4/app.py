import streamlit as st
import sqlite3
import hashlib
from datetime import datetime

# -------------------------------
# BANCO DE DADOS
# -------------------------------

conn = sqlite3.connect("clinica.db", check_same_thread=False)
cursor = conn.cursor()

def criar_tabelas():
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS usuarios(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE,
        senha TEXT
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS paciente(
        idPaciente INTEGER PRIMARY KEY AUTOINCREMENT,
        nomePaciente TEXT
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS medico(
        idMedico INTEGER PRIMARY KEY AUTOINCREMENT,
        crmMedico INTEGER,
        nomeMedico TEXT
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS remedio(
        idRemedio INTEGER PRIMARY KEY AUTOINCREMENT,
        nome_paciente TEXT,
        nome_remedio TEXT,
        data_inicio DATE,
        qtd_dias INTEGER,
        dose_remedio INTEGER,
        qtd_vezes_dia INTEGER
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS atendimento(
        idAtendimento INTEGER PRIMARY KEY AUTOINCREMENT,
        paciente TEXT,
        medico TEXT,
        horario TEXT,
        data_atend DATE
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS planilha_horarios(
        idPlanilha INTEGER PRIMARY KEY AUTOINCREMENT,
        data DATE,
        hora TEXT,
        observacoes TEXT
    )
    """)

    conn.commit()

criar_tabelas()

# -------------------------------
# SEGURANÇA (RNF001)
# -------------------------------

def hash_senha(senha):
    return hashlib.sha256(senha.encode()).hexdigest()

# cria usuário admin padrão
def criar_admin():
    cursor.execute("SELECT * FROM usuarios WHERE username='admin'")
    if not cursor.fetchone():
        cursor.execute("INSERT INTO usuarios(username,senha) VALUES(?,?)",
                       ("admin", hash_senha("admin123")))
        conn.commit()

criar_admin()

# -------------------------------
# LOGIN
# -------------------------------

def login():

    st.title("Sistema de Prontuário Eletrônico")

    user = st.text_input("Usuário")
    senha = st.text_input("Senha", type="password")

    if st.button("Entrar"):

        senha_hash = hash_senha(senha)

        cursor.execute(
            "SELECT * FROM usuarios WHERE username=? AND senha=?",
            (user, senha_hash)
        )

        if cursor.fetchone():
            st.session_state["logado"] = True
        else:
            st.error("Login inválido")

# -------------------------------
# CRUD PACIENTE
# -------------------------------

def gerenciar_paciente():

    st.subheader("Cadastro de Pacientes")

    nome = st.text_input("Nome do paciente")

    if st.button("Cadastrar paciente"):
        cursor.execute(
            "INSERT INTO paciente(nomePaciente) VALUES(?)",
            (nome,)
        )
        conn.commit()
        st.success("Paciente cadastrado")

    st.write("### Lista de pacientes")

    dados = cursor.execute("SELECT * FROM paciente").fetchall()

    st.table(dados)

# -------------------------------
# CRUD MEDICO
# -------------------------------

def gerenciar_medico():

    st.subheader("Cadastro de Médicos")

    nome = st.text_input("Nome do médico")
    crm = st.number_input("CRM")

    if st.button("Cadastrar médico"):
        cursor.execute(
            "INSERT INTO medico(nomeMedico,crmMedico) VALUES(?,?)",
            (nome, crm)
        )
        conn.commit()
        st.success("Médico cadastrado")

    st.write("### Lista de médicos")

    dados = cursor.execute("SELECT * FROM medico").fetchall()
    st.table(dados)

# -------------------------------
# REMEDIO
# -------------------------------

def gerenciar_remedio():

    st.subheader("Cadastro de Remédios")

    paciente = st.text_input("Paciente")
    nome = st.text_input("Nome do remédio")

    data_inicio = st.date_input("Data início")

    qtd_dias = st.number_input("Quantidade dias")

    dose = st.number_input("Dose")

    vezes = st.number_input("Vezes por dia")

    if st.button("Cadastrar remédio"):

        cursor.execute("""
        INSERT INTO remedio(
        nome_paciente,
        nome_remedio,
        data_inicio,
        qtd_dias,
        dose_remedio,
        qtd_vezes_dia)
        VALUES(?,?,?,?,?,?)
        """, (paciente, nome, data_inicio, qtd_dias, dose, vezes))

        conn.commit()

        st.success("Remédio registrado")

    st.write("### Lista")

    dados = cursor.execute("SELECT * FROM remedio").fetchall()

    st.table(dados)

# -------------------------------
# PLANILHA HORARIO
# -------------------------------

def gerenciar_planilha():

    st.subheader("Planilha de Horários")

    data = st.date_input("Data")

    hora = st.text_input("Hora")

    obs = st.text_area("Observações")

    if st.button("Salvar horário"):

        cursor.execute("""
        INSERT INTO planilha_horarios(data,hora,observacoes)
        VALUES(?,?,?)
        """, (data, hora, obs))

        conn.commit()

        st.success("Horário salvo")

    st.write("### Agenda")

    dados = cursor.execute("SELECT * FROM planilha_horarios").fetchall()

    st.table(dados)

# -------------------------------
# ATENDIMENTO
# -------------------------------

def realizar_atendimento():

    st.subheader("Registrar Atendimento")

    pacientes = [x[1] for x in cursor.execute(
        "SELECT * FROM paciente").fetchall()]

    medicos = [x[2] for x in cursor.execute(
        "SELECT * FROM medico").fetchall()]

    paciente = st.selectbox("Paciente", pacientes)

    medico = st.selectbox("Médico", medicos)

    data = st.date_input("Data atendimento")

    horario = st.text_input("Horário")

    if st.button("Registrar atendimento"):

        cursor.execute("""
        INSERT INTO atendimento(
        paciente,
        medico,
        horario,
        data_atend)
        VALUES(?,?,?,?)
        """, (paciente, medico, horario, data))

        conn.commit()

        st.success("Atendimento registrado")

    st.write("### Histórico")

    dados = cursor.execute("SELECT * FROM atendimento").fetchall()

    st.table(dados)

# -------------------------------
# MENU PRINCIPAL
# -------------------------------

def sistema():

    menu = st.sidebar.selectbox(
        "Menu",
        [
            "Paciente",
            "Medico",
            "Remedio",
            "Planilha Horarios",
            "Atendimento"
        ]
    )

    if menu == "Paciente":
        gerenciar_paciente()

    if menu == "Medico":
        gerenciar_medico()

    if menu == "Remedio":
        gerenciar_remedio()

    if menu == "Planilha Horarios":
        gerenciar_planilha()

    if menu == "Atendimento":
        realizar_atendimento()

# -------------------------------
# APP
# -------------------------------

if "logado" not in st.session_state:
    st.session_state["logado"] = False

if st.session_state["logado"] == False:
    login()
else:
    sistema()
