import streamlit as st
import pandas as pd
import hashlib

# ==========================================
# CONFIGURAÇÕES E RNF002 (Desempenho <= 2s)
# ==========================================
st.set_page_config(page_title="PDV Doce Sabor do Seu Joaquim", layout="wide")

# Utilizando session_state para atuar como banco de dados em memória, garantindo alta performance
if 'produtos' not in st.session_state:
    st.session_state['produtos'] = pd.DataFrame(columns=['idProduto', 'nomeProduto', 'valorUnidade'])
if 'clientes' not in st.session_state:
    st.session_state['clientes'] = pd.DataFrame(columns=['idCliente', 'nome'])
if 'comandas' not in st.session_state:
    st.session_state['comandas'] = pd.DataFrame(columns=['idComanda', 'idCliente', 'status', 'valorTotal'])
if 'itens_comanda' not in st.session_state:
    st.session_state['itens_comanda'] = pd.DataFrame(columns=['idComanda', 'idProduto', 'nomeProduto', 'quantidade', 'subTotal'])
if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False

# ==========================================
# RNF001 - SEGURANÇA (Criptografia)
# ==========================================
def hash_password(password):
    """Criptografa a senha usando SHA-256 no banco."""
    return hashlib.sha256(str.encode(password)).hexdigest()

# Senha de administrador simulada no banco de dados (A senha é 'joaquim123')
USER_PASSWORD_HASH = hash_password('joaquim123')

def tela_login():
    st.title("🥖 Login - PDV Doce Sabor")
    st.info("Senha de acesso: **joaquim123**")
    senha_input = st.text_input("Senha do Sistema", type="password")
    
    if st.button("Acessar Caixa"):
        if hash_password(senha_input) == USER_PASSWORD_HASH:
            st.session_state['logged_in'] = True
            st.rerun()
        else:
            st.error("Senha incorreta! Acesso negado.")

# ==========================================
# MÓDULOS DO SISTEMA (Baseados no Diagrama UML)
# ==========================================

def gerenciar_produtos():
    """Referente à classe PRODUTO"""
    st.header("📦 Cadastro de Produtos")
    
    with st.form("form_produto"):
        nome = st.text_input("Nome do Produto")
        valor = st.number_input("Valor Unitário (R$)", min_value=0.01, format="%.2f")
        submit = st.form_submit_button("Cadastrar Produto")
        
        if submit and nome:
            novo_id = len(st.session_state['produtos']) + 1
            novo_produto = pd.DataFrame([{'idProduto': novo_id, 'nomeProduto': nome, 'valorUnidade': valor}])
            st.session_state['produtos'] = pd.concat([st.session_state['produtos'], novo_produto], ignore_index=True)
            st.success("Produto cadastrado com sucesso!")

    if not st.session_state['produtos'].empty:
        st.dataframe(st.session_state['produtos'], use_container_width=True, hide_index=True)

def atendimento_comanda():
    """Referente às classes CLIENTE, COMANDA e ITEM_COMANDA"""
    st.header("📝 Atendimento e Comandas")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("1. Abrir Nova Comanda (+solicitarComanda)")
        nome_cliente = st.text_input("Nome do Cliente")
        if st.button("Abrir Comanda"):
            if nome_cliente:
                # Cria o cliente
                id_cliente = len(st.session_state['clientes']) + 1
                novo_cliente = pd.DataFrame([{'idCliente': id_cliente, 'nome': nome_cliente}])
                st.session_state['clientes'] = pd.concat([st.session_state['clientes'], novo_cliente], ignore_index=True)
                
                # Associa à nova comanda
                id_comanda = len(st.session_state['comandas']) + 1
                nova_comanda = pd.DataFrame([{'idComanda': id_comanda, 'idCliente': id_cliente, 'status': 'Aberta', 'valorTotal': 0.0}])
                st.session_state['comandas'] = pd.concat([st.session_state['comandas'], nova_comanda], ignore_index=True)
                st.success(f"Comanda #{id_comanda} aberta para {nome_cliente}!")
            else:
                st.error("Informe o nome do cliente.")

    with col2:
        st.subheader("2. Lançar Itens (+adicionarItem)")
        comandas_abertas = st.session_state['comandas'][st.session_state['comandas']['status'] == 'Aberta']
        
        if not comandas_abertas.empty and not st.session_state['produtos'].empty:
            with st.form("form_itens"):
                # Selectbox para comandas e produtos
                id_comanda_sel = st.selectbox("Selecione a Comanda", comandas_abertas['idComanda'].tolist())
                
                dict_produtos = dict(zip(st.session_state['produtos']['idProduto'], st.session_state['produtos']['nomeProduto']))
                id_produto_sel = st.selectbox("Selecione o Produto", options=dict_produtos.keys(), format_func=lambda x: dict_produtos[x])
                
                quantidade = st.number_input("Quantidade", min_value=1, step=1)
                submit_item = st.form_submit_button("Lançar Item")
                
                if submit_item:
                    # Lógica de +calcularSubtotal()
                    preco_unitario = st.session_state['produtos'].loc[st.session_state['produtos']['idProduto'] == id_produto_sel, 'valorUnidade'].values[0]
                    subtotal = preco_unitario * quantidade
                    nome_prod = dict_produtos[id_produto_sel]
                    
                    novo_item = pd.DataFrame([{
                        'idComanda': id_comanda_sel, 
                        'idProduto': id_produto_sel, 
                        'nomeProduto': nome_prod,
                        'quantidade': quantidade, 
                        'subTotal': subtotal
                    }])
                    st.session_state['itens_comanda'] = pd.concat([st.session_state['itens_comanda'], novo_item], ignore_index=True)
                    st.success(f"{quantidade}x {nome_prod} adicionado(s) à Comanda #{id_comanda_sel}.")
        else:
            st.warning("É necessário ter comandas abertas e produtos cadastrados.")

def modulo_caixa():
    """Referente à classe CAIXA (+lerComanda, +CalcularTotal, +finalizarCompra)"""
    st.header("💰 Frente de Caixa")
    
    comandas_abertas = st.session_state['comandas'][st.session_state['comandas']['status'] == 'Aberta']
    
    if comandas_abertas.empty:
        st.info("Nenhuma comanda aberta no momento.")
        return

    # +lerComanda()
    id_comanda_caixa = st.selectbox("Ler Comanda (ID)", comandas_abertas['idComanda'].tolist())
    
    if id_comanda_caixa:
        itens_desta_comanda = st.session_state['itens_comanda'][st.session_state['itens_comanda']['idComanda'] == id_comanda_caixa]
        
        st.subheader(f"Resumo da Comanda #{id_comanda_caixa}")
        if not itens_desta_comanda.empty:
            st.dataframe(itens_desta_comanda[['nomeProduto', 'quantidade', 'subTotal']], use_container_width=True, hide_index=True)
            
            # +CalcularTotal()
            valor_total = itens_desta_comanda['subTotal'].sum()
            st.metric(label="Total a Pagar", value=f"R$ {valor_total:.2f}")
            
            # +finalizarCompra() e +fecharComanda()
            if st.button("Finalizar Compra e Fechar Comanda"):
                # Atualiza o status da comanda no dataframe principal
                idx = st.session_state['comandas'].index[st.session_state['comandas']['idComanda'] == id_comanda_caixa].tolist()[0]
                st.session_state['comandas'].at[idx, 'status'] = 'Fechada'
                st.session_state['comandas'].at[idx, 'valorTotal'] = valor_total
                st.success("Compra finalizada com sucesso! Comanda fechada.")
                st.rerun()
        else:
            st.warning("Esta comanda ainda não possui itens lançados.")

# ==========================================
# FLUXO PRINCIPAL
# ==========================================
def main():
    if not st.session_state['logged_in']:
        tela_login()
    else:
        with st.sidebar:
            st.title("Sistema PDV")
            menu = st.radio("Navegação", ["Atendimento (Comandas)", "Caixa (Pagamento)", "Estoque (Produtos)"])
            
            st.markdown("---")
            if st.button("🔒 Sair do Sistema"):
                st.session_state['logged_in'] = False
                st.rerun()

        if menu == "Estoque (Produtos)":
            gerenciar_produtos()
        elif menu == "Atendimento (Comandas)":
            atendimento_comanda()
        elif menu == "Caixa (Pagamento)":
            modulo_caixa()

if __name__ == '__main__':
    main()
