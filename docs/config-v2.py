"""Configurações da Anna (chave de API, modelo e caminhos)."""
import os
from pathlib import Path

try:  # opcional: carrega variáveis de um arquivo .env, se python-dotenv estiver instalado
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

RAIZ = Path(__file__).resolve().parent.parent

# Troque por um modelo disponível na sua conta (platform.openai.com/docs/models).
MODELO = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
VERSAO_PROMPT = os.getenv("VERSAO_PROMPT", "v2")
TEMPERATURA = 0.3
MAX_RODADAS_FERRAMENTAS = 4

ARQUIVO_KB = Path(os.getenv("ARQUIVO_KB", RAIZ / "data" / "base_conhecimento_anna.md"))


def obter_chave():
    """Lê a chave da variável de ambiente OPENAI_API_KEY (ou do painel Secrets do Colab)."""
    chave = os.getenv("OPENAI_API_KEY")
    if not chave:
        try:
            from google.colab import userdata  # só existe no Google Colab
            chave = userdata.get("OPENAI_API_KEY")
        except Exception:
            chave = None
    if not chave:
        raise RuntimeError(
            "Chave da API não encontrada. Defina OPENAI_API_KEY no ambiente, em um arquivo .env "
            "ou no painel Secrets do Colab."
        )
    return chave
