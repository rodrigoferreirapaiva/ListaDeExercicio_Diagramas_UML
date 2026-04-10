import streamlit as st
import pandas as pd
import hashlib
from datetime import datetime, date

# ==========================================
# CONFIGURAÇÕES E RNF002 (Desempenho <= 2s)
# ==========================================
st.set_page_config(page_title="Gestão de Reuniões - Patrícia", layout="wide")

# Inicialização do banco de dados em memória (Tabelas Relacionais)
if 'funcionarios' not in st.session_state:
    st.session_state['funcionarios'] = pd.DataFrame(columns=['idFunc', 'nome', 'cargo', 'ramal'])
if 'salas' not in st.session_state:
    st.session_state['salas'] = pd.DataFrame(columns=['idSala', 'numero', 'capacidade'])
if 'reunioes' not in st.session_state:
    st.session_state['reunioes'] = pd.DataFrame(columns=['idReuniao', 'assunto', 'data', 'horaInicio', 'horaFim', 'idSala', 'idFunc'])
if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False

# ==========================================
# RNF001 - SEGURANÇA (Criptografia)
# ==========================================
def hash_password(password):
    """Criptografa a senha usando SHA-256."""
    return hashlib.sha256(str.encode(password)).hexdigest()

# Senha de acesso da Patrícia simulada no banco ('patricia123')
USER_PASSWORD_HASH = hash_password('patricia123')

def tela_login():
    st.title("📅 Sistema de Agendamento - Patrícia")
    st.info("Senha de acesso: **patricia123**")
    senha_input = st.text_input("Senha", type="password")
    
    if st.button("Entrar"):
        if hash_password(senha_input) == USER_PASSWORD_HASH:
            st.session_state['logged_in'] = True
            st.rerun()
        else:
            st.error("Senha incorreta!")

# ==========================================
# MÓDULOS DO SISTEMA (Baseados na UML)
# ==========================================

def gerenciar_cadastros():
    st.header("🏢 Cadastros Básicos (Salas e Funcionários)")
    
    colA, colB = st.columns(2)
    
    # Cadastro de Sala de Reunião
    with colA:
        st.subheader("Nova Sala de Reunião")
        with st.form("form_sala"):
            numero_sala = st.number_input("Número da Sala", min_value=1, step=1)
            capacidade = st.number_input("Capacidade (Pessoas)", min_value=1, step=1)
            if st.form_submit_button("Cadastrar Sala"):
                if numero_sala in st.session_state['salas']['numero'].values:
                    st.error("Esta sala já está cadastrada.")
                else:
                    novo_id = 1 if st.session_state['salas'].empty else st.session_state['salas']['idSala'].max() + 1
                    nova_sala = pd.DataFrame([{'idSala': novo_id, 'numero': numero_sala, 'capacidade': capacidade}])
                    st.session_state['salas'] = pd.concat([st.session_state['salas'], nova_sala], ignore_index=True)
                    st.success(f"Sala {numero_sala} cadastrada!")
        
        if not st.session_state['salas'].empty:
            st.dataframe(st.session_state['salas'], hide_index=True, use_container_width=True)

    # Cadastro de Funcionário
    with colB:
        st.subheader("Novo Funcionário (Solicitante)")
        with st.form("form_func"):
            nome_func = st.text_input("Nome do Funcionário")
            cargo = st.text_input("Cargo")
            ramal = st.number_input("Ramal", min_value=1000, max_value=9999, step=1)
            if st.form_submit_button("Cadastrar Funcionário"):
                if nome_func:
                    novo_id = 1 if st.session_state['funcionarios'].empty else st.session_state['funcionarios']['idFunc'].max() + 1
                    novo_func = pd.DataFrame([{'idFunc': novo_id, 'nome': nome_func, 'cargo': cargo, 'ramal': ramal}])
                    st.session_state['funcionarios'] = pd.concat([st.session_state['funcionarios'], novo_func], ignore_index=True)
                    st.success("Funcionário cadastrado!")
                else:
                    st.error("O nome é obrigatório.")
                    
        if not st.session_state['funcionarios'].empty:
            st.dataframe(st.session_state['funcionarios'], hide_index=True, use_container_width=True)

def verificar_disponibilidade(data_alvo, hora_inicio, hora_fim, id_sala, id_reuniao_ignorada=None):
    """Método +verificarDisponibilidade() da classe DiaAgenda"""
    df_reunioes = st.session_state['reunioes']
    
    # Filtra as reuniões da mesma data e sala
    conflitos = df_reunioes[(df_reunioes['data'] == data_alvo) & (df_reunioes['idSala'] == id_sala)]
    
    if id_reuniao_ignorada is not None:
        conflitos = conflitos[conflitos['idReuniao'] != id_reuniao_ignorada]
        
    for _, row in conflitos.iterrows():
        # Lógica de sobreposição de horários
        if (hora_inicio < row['horaFim']) and (hora_fim > row['horaInicio']):
            return False # Indisponível (Conflito)
    return True # Disponível

def modulo_agendamento():
    st.header("📅 Agendar Nova Reunião")
    st.write("Implementação do método `+agendarReuniao()` e validação `+verificarDisponibilidade()`.")
    
    if st.session_state['salas'].empty or st.session_state['funcionarios'].empty:
        st.warning("É necessário cadastrar ao menos uma sala e um funcionário antes de agendar.")
        return

    with st.form("form_agendamento"):
        assunto = st.text_input("Assunto da Reunião")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            data_reuniao = st.date_input("Data da Reunião", min_value=date.today())
        with col2:
            hora_inicio = st.time_input("Hora de Início")
        with col3:
            hora_fim = st.time_input("Hora de Término")
            
        colA, colB = st.columns(2)
        with colA:
            opcoes_sala = dict(zip(st.session_state['salas']['idSala'], "Sala " + st.session_state['salas']['numero'].astype(str) + " (Cap: " + st.session_state['salas']['capacidade'].astype(str) + ")"))
            id_sala = st.selectbox("Sala", options=opcoes_sala.keys(), format_func=lambda x: opcoes_sala[x])
        with colB:
            opcoes_func = dict(zip(st.session_state['funcionarios']['idFunc'], st.session_state['funcionarios']['nome'] + " - " + st.session_state['funcionarios']['cargo']))
            id_func = st.selectbox("Solicitante", options=opcoes_func.keys(), format_func=lambda x: opcoes_func[x])
            
        submit = st.form_submit_button("Agendar")
        
        if submit:
            if not assunto:
                st.error("O assunto é obrigatório.")
            elif hora_inicio >= hora_fim:
                st.error("A hora de término deve ser maior que a hora de início.")
            else:
                # Chama o método de verificação de disponibilidade do diagrama UML
                if verificar_disponibilidade(data_reuniao, hora_inicio, hora_fim, id_sala):
                    novo_id = 1 if st.session_state['reunioes'].empty else st.session_state['reunioes']['idReuniao'].max() + 1
                    nova_reuniao = pd.DataFrame([{
                        'idReuniao': novo_id,
                        'assunto': assunto,
                        'data': data_reuniao,
                        'horaInicio': hora_inicio,
                        'horaFim': hora_fim,
                        'idSala': id_sala,
                        'idFunc': id_func
                    }])
                    st.session_state['reunioes'] = pd.concat([st.session_state['reunioes'], nova_reuniao], ignore_index=True)
                    st.success("Reunião agendada com sucesso!")
                else:
                    st.error("Conflito de horário! A sala selecionada já possui uma reunião neste período.")

def consultar_e_realocar():
    st.header("🔄 Consultar e Realocar Reuniões")
    st.write("Implementação dos métodos `+realocarReuniao()`, `+alterarHora()`, `+alterarData()` e `+removerReuniao()`.")
    
    if st.session_state['reunioes'].empty:
        st.info("Não há reuniões agendadas.")
        return

    # Visualização da Agenda
    df_display = st.session_state['reunioes'].merge(st.session_state['salas'], on='idSala').merge(st.session_state['funcionarios'], on='idFunc')
    df_display = df_display[['idReuniao', 'data', 'horaInicio', 'horaFim', 'assunto', 'numero', 'nome']]
    df_display.columns = ['ID', 'Data', 'Início', 'Término', 'Assunto', 'Sala', 'Solicitante']
    st.dataframe(df_display.sort_values(by=['Data', 'Início']), hide_index=True, use_container_width=True)
    
    st.markdown("---")
    
    # Realocar ou Remover
    opcoes_reuniao = dict(zip(df_display['ID'], df_display['Data'].astype(str) + " | " + df_display['Assunto'] + " (Sala " + df_display['Sala'].astype(str) + ")"))
    id_selecionado = st.selectbox("Selecione uma Reunião para Gerenciar:", options=opcoes_reuniao.keys(), format_func=lambda x: opcoes_reuniao[x])
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Cancelar Reunião (+removerReuniao)")
        if st.button("Cancelar Reunião Selecionada"):
            st.session_state['reunioes'] = st.session_state['reunioes'][st.session_state['reunioes']['idReuniao'] != id_selecionado]
            st.success("Reunião cancelada!")
            st.rerun()
            
    with col2:
        st.subheader("Realocar (+alterarData/Hora)")
        with st.form("form_realocar"):
            nova_data = st.date_input("Nova Data", min_value=date.today())
            nova_hora_ini = st.time_input("Nova Hora Início")
            nova_hora_fim = st.time_input("Nova Hora Término")
            id_sala_atual = st.session_state['reunioes'].loc[st.session_state['reunioes']['idReuniao'] == id_selecionado, 'idSala'].values[0]
            
            if st.form_submit_button("Confirmar Realocação"):
                if nova_hora_ini >= nova_hora_fim:
                    st.error("A hora de término deve ser maior que a hora de início.")
                elif verificar_disponibilidade(nova_data, nova_hora_ini, nova_hora_fim, id_sala_atual, id_reuniao_ignorada=id_selecionado):
                    # Atualiza os dados
                    idx = st.session_state['reunioes'].index[st.session_state['reunioes']['idReuniao'] == id_selecionado].tolist()[0]
                    st.session_state['reunioes'].at[idx, 'data'] = nova_data
                    st.session_state['reunioes'].at[idx, 'horaInicio'] = nova_hora_ini
                    st.session_state['reunioes'].at[idx, 'horaFim'] = nova_hora_fim
                    st.success("Reunião realocada com sucesso!")
                    st.rerun()
                else:
                    st.error("Conflito! A sala não está livre neste novo horário.")

# ==========================================
# FLUXO PRINCIPAL
# ==========================================
def main():
    if not st.session_state['logged_in']:
        tela_login()
    else:
        with st.sidebar:
            st.title("Menu da Agenda")
            st.write("Usuária: **Patrícia**")
            menu = st.radio("Navegação", ["1. Cadastros Básicos", "2. Agendar Reunião", "3. Gerenciar Agenda"])
            
            st.markdown("---")
            if st.button("🔒 Sair do Sistema"):
                st.session_state['logged_in'] = False
                st.rerun()

        if menu == "1. Cadastros Básicos":
            gerenciar_cadastros()
        elif menu == "2. Agendar Reunião":
            modulo_agendamento()
        elif menu == "3. Gerenciar Agenda":
            consultar_e_realocar()

if __name__ == '__main__':
    main()
