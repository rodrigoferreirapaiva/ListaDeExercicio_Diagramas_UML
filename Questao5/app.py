import streamlit as st
import pandas as pd
import hashlib
from datetime import datetime

# ==========================================
# CONFIGURAÇÕES INICIAIS E RNF002 (Desempenho)
# ==========================================
st.set_page_config(page_title="Controle de Gastos", layout="wide")

# Inicialização do "banco de dados" em memória (st.session_state garante acesso rápido - RNF002)
if 'tipos_gasto' not in st.session_state:
    st.session_state['tipos_gasto'] = pd.DataFrame(columns=['idTipo', 'des_tipo', 'obs'])
if 'gastos' not in st.session_state:
    st.session_state['gastos'] = pd.DataFrame(columns=['IdGasto', 'nome', 'data', 'valor', 'forma_pag', 'idTipo'])
if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False

# Enumeração (Conforme diagrama UML)
ENUM_FOR_PAG = ['dinheiro', 'pix', 'debito', 'credito', 'vale_refeicao']

# ==========================================
# RNF001 - SEGURANÇA (Criptografia de Senha)
# ==========================================
def hash_password(password):
    """Criptografa a senha usando SHA-256."""
    return hashlib.sha256(str.encode(password)).hexdigest()

# Senha mockada no "banco" (A senha original é 'admin123')
USER_PASSWORD_HASH = hash_password('admin123')

def login():
    st.title("🔒 Login do Sistema")
    st.info("Para testar, utilize a senha: **admin123**")
    senha_input = st.text_input("Senha", type="password")
    
    if st.button("Entrar"):
        if hash_password(senha_input) == USER_PASSWORD_HASH:
            st.session_state['logged_in'] = True
            st.rerun()
        else:
            st.error("Senha incorreta!")

# ==========================================
# MÓDULOS DO SISTEMA (Requisitos Funcionais)
# ==========================================

# RF001 - GERENCIAR TIPOS DE GASTOS
def gerenciar_tipos_gastos():
    st.header("Gerenciar Tipos de Gastos")
    
    with st.form("form_tipo_gasto"):
        st.subheader("Novo Tipo de Gasto")
        des_tipo = st.text_input("Descrição do Tipo")
        obs = st.text_area("Observações")
        submit = st.form_submit_button("Salvar Tipo")
        
        if submit:
            if des_tipo:
                novo_id = len(st.session_state['tipos_gasto']) + 1
                novo_tipo = pd.DataFrame([{'idTipo': novo_id, 'des_tipo': des_tipo, 'obs': obs}])
                st.session_state['tipos_gasto'] = pd.concat([st.session_state['tipos_gasto'], novo_tipo], ignore_index=True)
                st.success("Tipo de gasto cadastrado com sucesso!")
            else:
                st.error("A descrição é obrigatória.")

    st.subheader("Tipos de Gastos Cadastrados")
    if not st.session_state['tipos_gasto'].empty:
        st.dataframe(st.session_state['tipos_gasto'], use_container_width=True)
    else:
        st.warning("Nenhum tipo de gasto cadastrado ainda.")

# RF002 - GERENCIAR GASTOS
def gerenciar_gastos():
    st.header("Gerenciar Gastos")
    
    if st.session_state['tipos_gasto'].empty:
        st.error("Cadastre pelo menos um 'Tipo de Gasto' antes de lançar uma despesa.")
        return

    with st.form("form_gasto"):
        st.subheader("Lançar Novo Gasto")
        nome = st.text_input("Nome/Descrição do Gasto")
        data = st.date_input("Data", datetime.today())
        valor = st.number_input("Valor (R$)", min_value=0.01, format="%.2f")
        
        # Selectbox baseada na Enumeração e na tabela Tipo_Gasto
        forma_pag = st.selectbox("Forma de Pagamento", ENUM_FOR_PAG)
        opcoes_tipos = dict(zip(st.session_state['tipos_gasto']['idTipo'], st.session_state['tipos_gasto']['des_tipo']))
        id_tipo_selecionado = st.selectbox("Tipo de Gasto", options=opcoes_tipos.keys(), format_func=lambda x: opcoes_tipos[x])
        
        submit = st.form_submit_button("Salvar Gasto")
        
        if submit:
            if nome and valor > 0:
                novo_id = len(st.session_state['gastos']) + 1
                novo_gasto = pd.DataFrame([{
                    'IdGasto': novo_id, 
                    'nome': nome, 
                    'data': pd.to_datetime(data), 
                    'valor': float(valor), 
                    'forma_pag': forma_pag, 
                    'idTipo': id_tipo_selecionado
                }])
                st.session_state['gastos'] = pd.concat([st.session_state['gastos'], novo_gasto], ignore_index=True)
                st.success("Gasto lançado com sucesso!")
            else:
                st.error("Preencha o nome e um valor válido.")

    st.subheader("Histórico de Gastos")
    if not st.session_state['gastos'].empty:
        # Fazendo um merge (Join) para mostrar o nome do tipo de gasto na tabela
        df_display = pd.merge(st.session_state['gastos'], st.session_state['tipos_gasto'][['idTipo', 'des_tipo']], on='idTipo', how='left')
        df_display['data'] = df_display['data'].dt.strftime('%d/%m/%Y')
        st.dataframe(df_display[['IdGasto', 'data', 'nome', 'des_tipo', 'valor', 'forma_pag']], use_container_width=True)
    else:
        st.info("Nenhum gasto lançado.")

# RF003 - LISTAR FORMAS DE PAGAMENTO
def listar_formas_pagamento():
    st.header("Formas de Pagamento Disponíveis")
    st.write("Esta listagem provém diretamente da Enumeração `ENUM FOR_PAG` definida na modelagem UML.")
    
    # Exibição estilizada
    for forma in ENUM_FOR_PAG:
        st.markdown(f"- 💳 **{forma.upper().replace('_', ' ')}**")

# RF004 - GERAR RELATÓRIO MENSAL DOS GASTOS
def gerar_relatorio_mensal():
    st.header("Relatório Mensal de Gastos")
    
    if st.session_state['gastos'].empty:
        st.warning("Não há dados suficientes para gerar relatório.")
        return

    df_gastos = st.session_state['gastos'].copy()
    df_gastos['mes_ano'] = df_gastos['data'].dt.to_period('M')
    
    meses_disponiveis = df_gastos['mes_ano'].unique().astype(str).tolist()
    meses_disponiveis.sort(reverse=True)
    
    mes_selecionado = st.selectbox("Selecione o Mês/Ano", meses_disponiveis)
    
    if mes_selecionado:
        # Filtrar pelo mês selecionado
        df_filtrado = df_gastos[df_gastos['mes_ano'].astype(str) == mes_selecionado]
        
        total_mes = df_filtrado['valor'].sum()
        
        st.metric(label=f"Total Gasto em {mes_selecionado}", value=f"R$ {total_mes:.2f}")
        
        # Gráfico simples
        st.subheader("Resumo por Forma de Pagamento")
        resumo_pag = df_filtrado.groupby('forma_pag')['valor'].sum().reset_index()
        st.bar_chart(data=resumo_pag.set_index('forma_pag'))

        # Detalhamento
        st.subheader("Detalhamento")
        df_filtrado['data'] = df_filtrado['data'].dt.strftime('%d/%m/%Y')
        st.dataframe(df_filtrado[['data', 'nome', 'valor', 'forma_pag']], use_container_width=True)


# ==========================================
# FLUXO PRINCIPAL DE EXECUÇÃO
# ==========================================
def main():
    if not st.session_state['logged_in']:
        login()
    else:
        with st.sidebar:
            st.title("Menu de Navegação")
            escolha = st.radio("Selecione uma opção:", 
                               ["Gastos (RF002)", 
                                "Tipos de Gastos (RF001)", 
                                "Formas de Pagamento (RF003)", 
                                "Relatório Mensal (RF004)"])
            
            st.markdown("---")
            if st.button("Sair (Logout)"):
                st.session_state['logged_in'] = False
                st.rerun()

        if escolha == "Tipos de Gastos (RF001)":
            gerenciar_tipos_gastos()
        elif escolha == "Gastos (RF002)":
            gerenciar_gastos()
        elif escolha == "Formas de Pagamento (RF003)":
            listar_formas_pagamento()
        elif escolha == "Relatório Mensal (RF004)":
            gerar_relatorio_mensal()

if __name__ == '__main__':
    main()
