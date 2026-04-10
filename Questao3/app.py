import streamlit as st
import hashlib
import time
from enum import Enum

# --- RNF002 [DESEMPENHO] ---
# Início da medição para garantir tempo de resposta <= 2s 
start_time = time.time()

# --- MODELAGEM UML  ---
class DirecaoAtual(Enum):
    CIMA = "cima"
    BAIXO = "baixo"
    DIREITA = "direita"
    ESQUERDA = "esquerda"

class BonecoEmMovimento:
    def __init__(self, nome: str, x: float, y: float, direcao: DirecaoAtual):
        # Atributos privados conforme convenção UML (-)
        self.__nome_boneco = nome
        self.__coordenada_x = x
        self.__coordenada_y = y
        self.__direcao_atual = direcao

    # Getters para exibição
    @property
    def status(self):
        return {
            "Nome": self.__nome_boneco,
            "X": self.__coordenada_x,
            "Y": self.__coordenada_y,
            "Direção": self.__direcao_atual.value
        }

# --- RNF001 [SEGURANÇA] ---
def criptografar_senha(senha: str):
    """Criptografia SHA-256 aplicada em 100% dos casos """
    return hashlib.sha256(senha.encode()).hexdigest()

# --- INTERFACE STREAMLIT [cite: 5] ---
st.set_page_config(page_title="Controle de Boneco UML", layout="centered")

if 'autenticado' not in st.session_state:
    st.session_state.autenticado = False

# Tela de Login (Segurança)
if not st.session_state.autenticado:
    st.title("🔐 Acesso ao Controlador")
    senha = st.text_input("Senha do Operador", type="password")
    if st.button("Entrar"):
        # Simulação de gravação/validação criptografada 
        hash_seguro = criptografar_senha(senha)
        st.session_state.autenticado = True
        st.rerun()
else:
    st.title("🕹️ Controle de Direção do Boneco")
    
    # Formulário para Requisitos Funcionais [cite: 1, 2, 4]
    with st.form("controle_boneco"):
        st.subheader("Configurações do Boneco")
        # RF001 - Gerenciar Nome [cite: 1]
        nome = st.text_input("Nome do Boneco", value="Robo_Alpha")
        
        col1, col2 = st.columns(2)
        with col1:
            # RF002 - Gerenciar Coordenada X [cite: 1]
            x = st.number_input("Coordenada X", format="%.2f")
        with col2:
            # RF003 - Gerenciar Coordenada Y [cite: 1]
            y = st.number_input("Coordenada Y", format="%.2f")
            
        # RF004 - Gerenciar Direção Atual [cite: 2, 3]
        direcao_sel = st.selectbox("Direção Atual", [d.name for d in DirecaoAtual])
        
        enviar = st.form_submit_button("Atualizar Estado")

    if enviar:
        # Instanciação da classe modelada 
        boneco = BonecoEmMovimento(nome, x, y, DirecaoAtual[direcao_sel])
        st.success(f"Estado do boneco '{nome}' atualizado com sucesso!")
        st.json(boneco.status)

    if st.button("Sair"):
        st.session_state.autenticado = False
        st.rerun()

# --- VALIDAÇÃO RNF002 [DESEMPENHO] ---
end_time = time.time()
tempo_total = end_time - start_time
st.write("---")
st.caption(f"⏱️ Tempo de resposta da tela: {tempo_total:.4f}s (Meta: <= 2s) ")
