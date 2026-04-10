import streamlit as st
import pandas as pd
import hashlib

# ==========================================
# CONFIGURAÇÕES E RNF002 (Desempenho <= 2s)
# ==========================================
st.set_page_config(page_title="Coleção de CDs - Adriano", layout="wide")

# Inicialização do "banco de dados" em memória (Alta performance)
if 'cds' not in st.session_state:
    st.session_state['cds'] = pd.DataFrame(columns=['idCd', 'nomeCantor', 'tituloCd', 'anoLancamento'])
if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False

# ==========================================
# RNF001 - SEGURANÇA (Criptografia)
# ==========================================
def hash_password(password):
    """Criptografa a senha usando SHA-256."""
    return hashlib.sha256(str.encode(password)).hexdigest()

# Senha de acesso simulada no banco de dados (A senha é 'adriano123')
USER_PASSWORD_HASH = hash_password('adriano123')

def tela_login():
    st.title("💿 Acesso ao Sistema de Coleção")
    st.info("Senha de acesso: **adriano123**")
    senha_input = st.text_input("Senha", type="password")
    
    if st.button("Entrar"):
        if hash_password(senha_input) == USER_PASSWORD_HASH:
            st.session_state['logged_in'] = True
            st.rerun()
        else:
            st.error("Senha incorreta!")

# ==========================================
# MÓDULOS DO SISTEMA (Requisitos Funcionais e UML)
# ==========================================

# RF001, RF002, RF003, RF004 - CADASTRO DE CDs
def cadastrar_cd():
    st.header("🎵 Cadastrar Novo CD")
    st.write("Módulo responsável pelas funções de `+cadastrarCD()` e `+adicionarCD()`.")
    
    with st.form("form_cd"):
        col1, col2, col3 = st.columns(3)
        with col1:
            nome_cantor = st.text_input("Nome do Cantor ou Conjunto")
        with col2:
            titulo_cd = st.text_input("Título do CD")
        with col3:
            ano_lancamento = st.number_input("Ano de Lançamento", min_value=1900, max_value=2100, step=1, value=2000)
            
        submit = st.form_submit_button("Salvar CD na Coleção")
        
        if submit:
            if nome_cantor and titulo_cd:
                novo_id = len(st.session_state['cds']) + 1
                novo_cd = pd.DataFrame([{
                    'idCd': novo_id, 
                    'nomeCantor': nome_cantor, 
                    'tituloCd': titulo_cd, 
                    'anoLancamento': ano_lancamento
                }])
                st.session_state['cds'] = pd.concat([st.session_state['cds'], novo_cd], ignore_index=True)
                st.success("CD cadastrado com sucesso!")
            else:
                st.error("O Nome do Cantor e o Título do CD são obrigatórios.")

# RF005 - GERENCIAR LISTA DE COLEÇÃO DE CDs
def gerenciar_colecao():
    st.header("🗂️ Gerenciar Lista de Coleção")
    st.write("Módulo responsável por `+listarCD()`, `+buscarCD()`, `+removerCD()` e `+modificarCD()`.")
    
    if st.session_state['cds'].empty:
        st.info("A coleção de CDs está vazia.")
        return

    # +buscarCD()
    st.subheader("🔍 Buscar na Coleção")
    termo_busca = st.text_input("Pesquisar por Título ou Cantor:")
    
    df_filtrado = st.session_state['cds']
    if termo_busca:
        filtro = df_filtrado['nomeCantor'].str.contains(termo_busca, case=False, na=False) | \
                 df_filtrado['tituloCd'].str.contains(termo_busca, case=False, na=False)
        df_filtrado = df_filtrado[filtro]

    # +listarCD() / +exibirInformacoes()
    st.subheader(f"Lista de CDs ({len(df_filtrado)} encontrados)")
    st.dataframe(df_filtrado, use_container_width=True, hide_index=True)

    st.markdown("---")
    
    # +removerCD()
    st.subheader("🗑️ Remover CD")
    opcoes_cd = dict(zip(st.session_state['cds']['idCd'], st.session_state['cds']['tituloCd'] + " - " + st.session_state['cds']['nomeCantor']))
    id_remover = st.selectbox("Selecione o CD para remover:", options=opcoes_cd.keys(), format_func=lambda x: opcoes_cd[x])
    
    if st.button("Remover CD Selecionado"):
        st.session_state['cds'] = st.session_state['cds'][st.session_state['cds']['idCd'] != id_remover]
        st.success("CD removido da coleção!")
        st.rerun()

# ==========================================
# FLUXO PRINCIPAL DE NAVEGAÇÃO
# ==========================================
def main():
    if not st.session_state['logged_in']:
        tela_login()
    else:
        with st.sidebar:
            st.title("Menu do Sistema")
            st.write("Usuário: **Adriano**")
            menu = st.radio("Navegação", ["Cadastrar CD", "Gerenciar Coleção"])
            
            st.markdown("---")
            if st.button("🔒 Sair do Sistema"):
                st.session_state['logged_in'] = False
                st.rerun()

        if menu == "Cadastrar CD":
            cadastrar_cd()
        elif menu == "Gerenciar Coleção":
            gerenciar_colecao()

if __name__ == '__main__':
    main()
