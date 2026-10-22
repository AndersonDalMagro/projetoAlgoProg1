import os
import streamlit as st
from PIL import Image
from langchain.agents import AgentExecutor
from orquestrador import AgenteOrquestrador

# ------------------------------------------------------------------
# PERSONALIZE AQUI: titulo e descricao que aparecem na tela
# ------------------------------------------------------------------
TITULO = "Assistente Inteligente"
DESCRICAO = (
  "Faça uma pergunta ou envie uma imagem para análise. "
  "O agente decide sozinho qual ferramenta usar."
)

# As ferramentas leem as imagens da pasta "dados"
PASTA = os.path.dirname(os.path.abspath(__file__))
os.chdir(PASTA)
os.makedirs("dados", exist_ok=True)

st.set_page_config(page_title=TITULO, page_icon="🤖")
st.title(TITULO)
st.caption(DESCRICAO)


@st.cache_resource
def criar_orquestrador():
  agente = AgenteOrquestrador()
  return AgentExecutor(
    agent=agente.agente,
    tools=agente.tools,
    verbose=True,
    handle_parsing_errors=True
  )


def salvar_imagem(arquivo):
  nome = os.path.splitext(arquivo.name)[0].replace(" ", "_") + ".jpg"
  Image.open(arquivo).convert("RGB").save(os.path.join("dados", nome), "JPEG")
  return nome


# ---------------- Barra lateral: envio de imagem ----------------
with st.sidebar:
  st.header("📷 Imagem")
  arquivo = st.file_uploader("Envie uma imagem (JPG ou PNG)", type=["jpg", "jpeg", "png"])
  nome_imagem = None
  if arquivo is not None:
    nome_imagem = salvar_imagem(arquivo)
    st.image(arquivo, caption=nome_imagem)
    st.info("Agora escreva no chat o que deseja saber sobre a imagem, por exemplo: \"Analise a imagem\".")
  if st.button("Limpar conversa"):
    st.session_state.mensagens = []
    st.rerun()

# ---------------- Histórico da conversa ----------------
if "mensagens" not in st.session_state:
  st.session_state.mensagens = []

for msg in st.session_state.mensagens:
  with st.chat_message(msg["papel"]):
    st.markdown(msg["texto"])

# ---------------- Entrada do usuário ----------------
texto = st.chat_input("Digite sua dúvida...")

if texto:
  st.session_state.mensagens.append({"papel": "user", "texto": texto})
  with st.chat_message("user"):
    st.markdown(texto)

  pergunta = texto
  if nome_imagem:
    pergunta = f"{texto} (a imagem enviada se chama {nome_imagem})"

  with st.chat_message("assistant"):
    with st.spinner("Pensando..."):
      try:
        resposta = criar_orquestrador().invoke({"input": pergunta})["output"]
      except Exception as erro:
        resposta = f"⚠️ Ocorreu um erro: {erro}"
    if not isinstance(resposta, str):
      resposta = str(resposta)
    st.markdown(resposta)

  st.session_state.mensagens.append({"papel": "assistant", "texto": resposta})
