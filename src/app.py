"""Interface de chat da Anna (Gradio). Execute: python app.py"""
import os

import gradio as gr

import config
from agente import Anna, carregar_base
from openai import OpenAI

BASE = carregar_base()
CLIENTE = OpenAI(api_key=config.obter_chave())
SESSOES = {}  # uma instância da Anna por sessão do navegador, com memória própria


def chat_fn(mensagem, historico, request: gr.Request = None):
    sessao = getattr(request, "session_hash", None) or "padrao"
    if sessao not in SESSOES:
        SESSOES[sessao] = Anna(client=CLIENTE, base=BASE)
    limpo = [{"role": h["role"], "content": str(h["content"])} for h in historico]
    return SESSOES[sessao].responder(mensagem, limpo)


demo = gr.ChatInterface(
    chat_fn,
    type="messages",
    title="Anna | Assistente de relacionamento financeiro",
    description="Conteúdo educativo, valores ilustrativos. Não compartilhe CPF, senhas ou dados de cartão.",
    examples=[
        "Cartão com anuidade vale a pena?",
        "Como funciona o consórcio?",
        "Quanto rende R$ 5.000 em 12 meses a 1% ao mês?",
        "Qual a parcela de R$ 10.000 em 24 meses a 2% ao mês?",
    ],
)

if __name__ == "__main__":
    demo.launch(share=os.getenv("GRADIO_SHARE") == "1")
