import streamlit as st
import pandas as pd
import hashlib

# ==========================================
# CONFIGURAÇÕES E RNF002 (Desempenho <= 2s)
# ==========================================
st.set_page_config(page_title="Lista de Compras - Carolina", layout="wide")

# Inicialização do banco de dados em memória (Alta performance)
if 'produtos' not in st.session_state:
    st.session_state['produtos'] = pd.DataFrame(columns=['idProduto', 'nome', 'unidadeCompra', 'precoEstimado'])
if 'listas' not in st.session_state:
    st.session_state['listas'] = pd.DataFrame(columns=['idLista', 'mes', 'valorTotal'])
if 'itens_compra' not in st.session_state:
    st.session_state['itens_compra'] = pd.DataFrame(columns=['idItem', 'idLista', 'idProduto', 'nomeProduto', 'qtdMes', 'qtdCompra', 'subTotal'])
if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False

# ==========================================
# RNF001 - SEGURANÇA (Criptografia)
# ==========================================
def hash_password(password):
    """Criptografa a senha usando SHA-256."""
    return hashlib.sha256(str.encode(password)).hexdigest()

# Senha de acesso simulada no banco de dados (A senha é 'carolina123')
USER_PASSWORD_HASH = hash_password('carolina123')

def tela_login():
    st.title("🛒 Acesso ao Sistema")
    st.info("Senha de acesso: **carolina123**")
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

# RF001 e RF002 - GERENCIAR PRODUTO E UNIDADE DE COMPRA
def gerenciar_produtos():
    st.header("📦 Gerenciar Produtos")
    
    with st.form("form_produto"):
        col1, col2, col3 = st.columns(3)
        with col1:
            nome = st.text_input("Nome do Produto")
        with col2:
            # Atende ao RF002 (Gerenciar Unidade de Compra)
            unidades = ['Kg', 'Litro', 'Unidade', 'Caixa', 'Pacote', 'Grama']
            unidade = st.selectbox("Unidade de Compra", unidades)
        with col3:
            preco = st.number_input("Preço Estimado (R$)", min_value=0.01, format="%.2f")
            
        submit = st.form_submit_button("Salvar Produto")
        
        if submit:
            if nome:
                novo_id = len(st.session_state['produtos']) + 1
                novo_produto = pd.DataFrame([{
                    'idProduto': novo_id, 
                    'nome': nome, 
                    'unidadeCompra': unidade, 
                    'precoEstimado': preco
                }])
                st.session_state['produtos'] = pd.concat([st.session_state['produtos'], novo_produto], ignore_index=True)
                st.success("Produto cadastrado com sucesso!")
            else:
                st.error("O nome do produto é obrigatório.")

    st.subheader("Produtos Cadastrados")
    if not st.session_state['produtos'].empty:
        st.dataframe(st.session_state['produtos'], use_container_width=True, hide_index=True)
    else:
        st.info("Nenhum produto cadastrado.")

# RF003 e RF004 - GERENCIAR QUANTIDADES, CALCULAR VALOR E TOTAL
def gerenciar_lista_compras():
    st.header("📝 Lista de Compras Mensal")
    
    # +criarLista() da classe Carolina
    with st.expander("Criar Nova Lista Mensal", expanded=False):
        meses = ['Janeiro', 'Fevereiro', 'Março', 'Abril', 'Maio', 'Junho', 'Julho', 'Agosto', 'Setembro', 'Outubro', 'Novembro', 'Dezembro']
        mes_selecionado = st.selectbox("Mês de Referência", meses)
        
        if st.button("Criar Lista"):
            if not st.session_state['listas'][st.session_state['listas']['mes'] == mes_selecionado].empty:
                st.warning(f"Já existe uma lista para o mês de {mes_selecionado}.")
            else:
                novo_id = len(st.session_state['listas']) + 1
                nova_lista = pd.DataFrame([{'idLista': novo_id, 'mes': mes_selecionado, 'valorTotal': 0.0}])
                st.session_state['listas'] = pd.concat([st.session_state['listas'], nova_lista], ignore_index=True)
                st.success(f"Lista de {mes_selecionado} criada!")

    # Selecionar lista ativa para gerenciar
    if st.session_state['listas'].empty:
        st.info("Crie uma lista mensal para começar a adicionar itens.")
        return

    lista_opcoes = dict(zip(st.session_state['listas']['idLista'], st.session_state['listas']['mes']))
    id_lista_ativa = st.selectbox("Selecione a Lista para Gerenciar", options=lista_opcoes.keys(), format_func=lambda x: lista_opcoes[x])
    
    st.markdown("---")
    
    # +adicionarItem() da classe ListaCompras
    if not st.session_state['produtos'].empty:
        st.subheader("Adicionar Item à Lista")
        with st.form("form_item"):
            col1, col2, col3 = st.columns(3)
            with col1:
                dict_produtos = dict(zip(st.session_state['produtos']['idProduto'], st.session_state['produtos']['nome']))
                id_produto = st.selectbox("Produto", options=dict_produtos.keys(), format_func=lambda x: dict_produtos[x])
            with col2:
                # Atende ao RF003
                qtd_mes = st.number_input("Quantidade Prevista (Mês)", min_value=1, step=1)
            with col3:
                # Atende ao RF004 (Gerenciar Quantidade Total)
                qtd_compra = st.number_input("Quantidade Real Comprada", min_value=0.0, step=0.5)
                
            submit_item = st.form_submit_button("Inserir na Lista")
            
            if submit_item:
                preco_est = st.session_state['produtos'].loc[st.session_state['produtos']['idProduto'] == id_produto, 'precoEstimado'].values[0]
                
                # +CalcularSubtotal() da classe ItemCompra
                subtotal = preco_est * qtd_compra
                nome_prod = dict_produtos[id_produto]
                
                novo_item_id = len(st.session_state['itens_compra']) + 1
                novo_item = pd.DataFrame([{
                    'idItem': novo_item_id,
                    'idLista': id_lista_ativa,
                    'idProduto': id_produto,
                    'nomeProduto': nome_prod,
                    'qtdMes': qtd_mes,
                    'qtdCompra': qtd_compra,
                    'subTotal': subtotal
                }])
                st.session_state['itens_compra'] = pd.concat([st.session_state['itens_compra'], novo_item], ignore_index=True)
                st.success(f"{nome_prod} adicionado à lista!")
    else:
        st.warning("Cadastre produtos primeiro para poder inseri-los na lista.")

    # Exibição da Lista Atual e +calcularTotal() (RF004)
    st.markdown("---")
    st.subheader(f"Resumo da Lista: {lista_opcoes[id_lista_ativa]}")
    
    itens_da_lista = st.session_state['itens_compra'][st.session_state['itens_compra']['idLista'] == id_lista_ativa]
    
    if not itens_da_lista.empty:
        st.dataframe(itens_da_lista[['nomeProduto', 'qtdMes', 'qtdCompra', 'subTotal']], use_container_width=True, hide_index=True)
        
        # Atende ao RF004 (Calcular Valor Total da Compra)
        valor_total_calculado = itens_da_lista['subTotal'].sum()
        qtd_total_calculada = itens_da_lista['qtdCompra'].sum()
        
        col_t1, col_t2 = st.columns(2)
        col_t1.metric("Quantidade Total de Itens Comprados", f"{qtd_total_calculada}")
        col_t2.metric("Valor Total da Lista", f"R$ {valor_total_calculado:.2f}")
    else:
        st.info("A lista está vazia.")

# ==========================================
# FLUXO PRINCIPAL DE NAVEGAÇÃO
# ==========================================
def main():
    if not st.session_state['logged_in']:
        tela_login()
    else:
        with st.sidebar:
            st.title("Menu do Sistema")
            st.write("Usuária: **Carolina**")
            menu = st.radio("Navegação", ["Minha Lista de Compras", "Cadastro de Produtos"])
            
            st.markdown("---")
            if st.button("🔒 Sair do Sistema"):
                st.session_state['logged_in'] = False
                st.rerun()

        if menu == "Cadastro de Produtos":
            gerenciar_produtos()
        elif menu == "Minha Lista de Compras":
            gerenciar_lista_compras()

if __name__ == '__main__':
    main()
