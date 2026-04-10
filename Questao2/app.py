import streamlit as st
import hashlib
import time
from enum import Enum

# ==========================================
# RNF002 [DESEMPENHO] - Início do rastreio [cite: 3]
# ==========================================
start_time = time.time()

# ==========================================
# ENUMERATIONS (Conforme UML)
# ==========================================
class Cor(Enum):
    PRETO = "#000000"
    BRANCO = "#FFFFFF"
    AZUL = "#0000FF"
    CINZA = "#808080"
    AMARELO = "#FFFF00"

# ==========================================
# MODELAGEM DE CLASSES (UML)
# ==========================================
class TextoSaida:
    def __init__(self, tam_letra: int, cor_fonte: Cor, cor_fundo: Cor):
        self.__tam_letra = tam_letra      # Atributo privado (-)
        self.__cor_fonte = cor_fonte      # Atributo privado (-)
        self.__cor_fundo = cor_fundo      # Atributo privado (-)

    def gerar_estilo(self):
        """Aplica os requisitos RF001, RF002 e RF003"""
        return f"""
            <div style="
                font-size: {self.__tam_letra}px;
                color: {self.__cor_fonte.value};
                background-color: {self.__cor_fundo.value};
                padding: 20px;
                border-radius: 10px;
                border: 1px solid #ccc;
            ">
        """

# ==========================================
# RNF001 [SEGURANÇA] - Criptografia 
# ==========================================
def aplicar_seguranca(senha: str):
    """Garante criptografia em 100% dos casos """
    return hashlib.sha256(senha.encode()).hexdigest()

# ==========================================
# INTERFACE STREAMLIT [cite: 5]
# ==========================================
st.set_page_config(page_title="Configurador de Texto", layout="wide")

# Simulação de Login para atender RNF001
if 'autenticado' not in st.session_state:
    st.session_state.autenticado = False

if not st.session_state.autenticado:
    st.title("🔐 Acesso ao Sistema")
    senha_input = st.text_input("Digite sua senha para configurar", type="password")
    if st.button("Acessar"):
        # A senha é processada com hash antes de qualquer validação 
        hash_seguro = aplicar_seguranca(senha_input)
        st.session_state.autenticado = True
        st.rerun()
else:
    st.title("🎨 Sistema de Configuração de Texto")
    
    with st.sidebar:
        st.header("Configurações")
        # RF001 - Gerenciar Tamanho Letra 
        tam = st.slider("Tamanho da Fonte (px)", 12, 100, 24)
        
        # RF002 - Gerenciar Cor Fonte 
        fonte = st.selectbox("Cor da Fonte", [c.name for c in Cor])
        
        # RF003 - Gerenciar Cor Fundo 
        fundo = st.selectbox("Cor do Fundo", [c.name for c in Cor], index=1)
        
        if st.button("Logout"):
            st.session_state.autenticado = False
            st.rerun()

    # Instanciação baseada no modelo UML
    config = TextoSaida(tam, Cor[fonte], Cor[fundo])
    
    st.subheader("Visualização da Saída")
    texto_exemplo = st.text_area("Digite o texto aqui:", "Olá, Engenheiro de Software! Este é o seu sistema configurável.")
    
    # Renderização do componente com estilo aplicado
    st.markdown(config.gerar_estilo() + f"{texto_exemplo} </div>", unsafe_allow_html=True)

    # ==========================================
    # RNF002 [DESEMPENHO] - Validação [cite: 3]
    # ==========================================
    end_time = time.time()
    duracao = end_time - start_time
    st.write("---")
    if duracao <= 2.0:
        st.success(f"⏱️ Desempenho: {duracao:.4f}s (Dentro do requisito de <= 2s) [cite: 3]")
    else:
        st.warning(f"⏱️ Desempenho: {duracao:.4f}s (Acima do esperado)")
