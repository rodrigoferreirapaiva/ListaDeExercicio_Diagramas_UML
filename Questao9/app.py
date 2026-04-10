import streamlit as st
import pandas as pd
import hashlib

# ==========================================
# CONFIGURAÇÕES E RNF002 (Desempenho <= 2s)
# ==========================================
st.set_page_config(page_title="Coleção de CDs V2 - Adriano", layout="wide")

# Inicialização do banco de dados em memória (Tabelas Relacionais)
if 'cds' not in st.session_state:
    st.session_state['cds'] = pd.DataFrame(columns=['idCd', 'nomeCantor', 'tituloCd', 'anoLancamento', 'coletanea', 'cdDuplo'])
if 'musicos' not in st.session_state:
    st.session_state['musicos'] = pd.DataFrame(columns=['idMusico', 'idCd', 'nome'])
if 'musicas' not in st.session_state:
    st.session_state['musicas'] = pd.DataFrame(columns=['idMusica', 'idCd', 'titulo', 'duracao'])
if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False

# ==========================================
# RNF001 - SEGURANÇA (Criptografia)
# ==========================================
def hash_password(password):
    """Criptografa a senha usando SHA-256."""
    return hashlib.sha256(str.encode(password)).hexdigest()

# Senha de acesso simulada no banco de dados ('adriano123')
USER_PASSWORD_HASH = hash_password('adriano123')

def tela_login():
    st.title("💿 Login - Coleção de CDs (V2)")
    st.info("Senha de acesso: **adriano123**")
    senha_input = st.text_input("Senha", type="password")
    
    if st.button("Entrar"):
        if hash_password(senha_input) == USER_PASSWORD_HASH:
            st.session_state['logged_in'] = True
            st.rerun()
        else:
            st.error("Senha incorreta!")

# ==========================================
# MÓDULOS DO SISTEMA (Baseados na UML e RFs)
# ==========================================

# RF001, RF002, RF003, RF004, RF006 - CADASTRAR CD E METADADOS
def cadastrar_cd():
    st.header("🎵 Novo CD")
    
    with st.form("form_cd"):
        col1, col2 = st.columns(2)
        with col1:
            nome_cantor = st.text_input("Nome do Cantor ou Conjunto")
            titulo_cd = st.text_input("Título do CD")
        with col2:
            ano_lancamento = st.number_input("Ano de Lançamento", min_value=1900, max_value=2100, step=1, value=2000)
            st.write("Configurações Adicionais:")
            coletanea = st.checkbox("É Coletânea? (Múltiplos artistas)")
            cd_duplo = st.checkbox("É CD Duplo?")
            
        submit = st.form_submit_button("Salvar CD")
        
        if submit:
            if nome_cantor and titulo_cd:
                novo_id = 1 if st.session_state['cds'].empty else st.session_state['cds']['idCd'].max() + 1
                novo_cd = pd.DataFrame([{
                    'idCd': novo_id, 
                    'nomeCantor': nome_cantor, 
                    'tituloCd': titulo_cd, 
                    'anoLancamento': ano_lancamento,
                    'coletanea': coletanea,
                    'cdDuplo': cd_duplo
                }])
                st.session_state['cds'] = pd.concat([st.session_state['cds'], novo_cd], ignore_index=True)
                st.success(f"CD '{titulo_cd}' cadastrado com sucesso!")
            else:
                st.error("Nome do Cantor e Título são obrigatórios.")

# RF007 e RF008 - GERENCIAR MÚSICO E MÚSICA (+addMusico, +addMusica)
def gerenciar_conteudo_cd():
    st.header("🎹 Gerenciar Conteúdo do CD (Músicos e Faixas)")
    
    if st.session_state['cds'].empty:
        st.warning("Cadastre um CD primeiro para adicionar músicos e faixas.")
        return

    opcoes_cd = dict(zip(st.session_state['cds']['idCd'], st.session_state['cds']['tituloCd'] + " - " + st.session_state['cds']['nomeCantor']))
    id_cd_selecionado = st.selectbox("Selecione o CD", options=opcoes_cd.keys(), format_func=lambda x: opcoes_cd[x])
    
    st.markdown("---")
    colA, colB = st.columns(2)
    
    # +addMusico()
    with colA:
        st.subheader("Adicionar Músico (Participação)")
        with st.form("form_musico"):
            nome_musico = st.text_input("Nome do Músico")
            submit_musico = st.form_submit_button("Adicionar Músico")
            
            if submit_musico and nome_musico:
                novo_id = 1 if st.session_state['musicos'].empty else st.session_state['musicos']['idMusico'].max() + 1
                novo_musico = pd.DataFrame([{'idMusico': novo_id, 'idCd': id_cd_selecionado, 'nome': nome_musico}])
                st.session_state['musicos'] = pd.concat([st.session_state['musicos'], novo_musico], ignore_index=True)
                st.success("Músico adicionado!")
                
        # Listar músicos do CD atual
        musicos_cd = st.session_state['musicos'][st.session_state['musicos']['idCd'] == id_cd_selecionado]
        if not musicos_cd.empty:
            st.dataframe(musicos_cd[['nome']], hide_index=True, use_container_width=True)

    # +addMusica()
    with colB:
        st.subheader("Adicionar Faixa (Música)")
        with st.form("form_musica"):
            titulo_musica = st.text_input("Título da Música")
            duracao = st.number_input("Duração (Minutos)", min_value=0.1, format="%.2f", step=0.1)
            submit_musica = st.form_submit_button("Adicionar Música")
            
            if submit_musica and titulo_musica:
                novo_id = 1 if st.session_state['musicas'].empty else st.session_state['musicas']['idMusica'].max() + 1
                nova_musica = pd.DataFrame([{'idMusica': novo_id, 'idCd': id_cd_selecionado, 'titulo': titulo_musica, 'duracao': duracao}])
                st.session_state['musicas'] = pd.concat([st.session_state['musicas'], nova_musica], ignore_index=True)
                st.success("Música adicionada!")
                
        # Listar músicas do CD atual (+listarMusica)
        musicas_cd = st.session_state['musicas'][st.session_state['musicas']['idCd'] == id_cd_selecionado]
        if not musicas_cd.empty:
            st.dataframe(musicas_cd[['titulo', 'duracao']], hide_index=True, use_container_width=True)

# RF005 - GERENCIAR LISTA (+consultarColecao, +consultarCdPorMusica, +consultarCdPorMusico)
def consultar_colecao():
    st.header("🗂️ Consultar Coleção")
    
    if st.session_state['cds'].empty:
        st.info("A coleção está vazia.")
        return

    tipo_busca = st.radio("Pesquisar por:", ["Geral (Título/Cantor)", "Por Música", "Por Músico (Participante)"], horizontal=True)
    termo = st.text_input("Digite o termo da busca:")
    
    df_resultados = pd.DataFrame()

    if termo:
        if tipo_busca == "Geral (Título/Cantor)":
            filtro = st.session_state['cds']['nomeCantor'].str.contains(termo, case=False, na=False) | \
                     st.session_state['cds']['tituloCd'].str.contains(termo, case=False, na=False)
            df_resultados = st.session_state['cds'][filtro]
            
        elif tipo_busca == "Por Música":
            # Lógica de +consultarCdPorMusica() da classe Adriano
            musicas_filtro = st.session_state['musicas'][st.session_state['musicas']['titulo'].str.contains(termo, case=False, na=False)]
            ids_cds = musicas_filtro['idCd'].unique()
            df_resultados = st.session_state['cds'][st.session_state['cds']['idCd'].isin(ids_cds)]
            
        elif tipo_busca == "Por Músico (Participante)":
            # Lógica de +consultarCdPorMusico() da classe Adriano
            musicos_filtro = st.session_state['musicos'][st.session_state['musicos']['nome'].str.contains(termo, case=False, na=False)]
            ids_cds = musicos_filtro['idCd'].unique()
            df_resultados = st.session_state['cds'][st.session_state['cds']['idCd'].isin(ids_cds)]
            
        st.subheader("Resultados da Busca")
        st.dataframe(df_resultados, use_container_width=True, hide_index=True)
    else:
        # +consultarColecao()
        st.subheader("Todos os CDs da Coleção")
        st.dataframe(st.session_state['cds'], use_container_width=True, hide_index=True)
        
        # +removerCD()
        st.markdown("---")
        opcoes_remover = dict(zip(st.session_state['cds']['idCd'], st.session_state['cds']['tituloCd']))
        id_remover = st.selectbox("Selecione um CD para Remover", options=opcoes_remover.keys(), format_func=lambda x: opcoes_remover[x])
        if st.button("Remover CD Selecionado"):
            # Remove o CD e as referências nas tabelas filhas (Integridade)
            st.session_state['cds'] = st.session_state['cds'][st.session_state['cds']['idCd'] != id_remover]
            st.session_state['musicos'] = st.session_state['musicos'][st.session_state['musicos']['idCd'] != id_remover]
            st.session_state['musicas'] = st.session_state['musicas'][st.session_state['musicas']['idCd'] != id_remover]
            st.success("CD e suas dependências foram removidos!")
            st.rerun()

# ==========================================
# FLUXO PRINCIPAL
# ==========================================
def main():
    if not st.session_state['logged_in']:
        tela_login()
    else:
        with st.sidebar:
            st.title("Menu V2")
            st.write("Usuário: **Adriano**")
            menu = st.radio("Navegação", ["1. Cadastrar CD", "2. Adicionar Faixas/Músicos", "3. Consultar Coleção"])
            
            st.markdown("---")
            if st.button("🔒 Logout"):
                st.session_state['logged_in'] = False
                st.rerun()

        if menu == "1. Cadastrar CD":
            cadastrar_cd()
        elif menu == "2. Adicionar Faixas/Músicos":
            gerenciar_conteudo_cd()
        elif menu == "3. Consultar Coleção":
            consultar_colecao()

if __name__ == '__main__':
    main()
