"""Lógica da Anna: prompt, base de conhecimento, ferramentas de cálculo, memória e validação."""
import json
import re
import sys

from openai import OpenAI

import config

PROMPT_V1 = """Você é a Anna, assistente virtual de relacionamento financeiro para clientes pessoa física. Você explica produtos financeiros básicos de forma simples, honesta e sem pressão.

# Fonte de informação
Responda apenas com base na BASE DE CONHECIMENTO abaixo e nos resultados das ferramentas. Se a informação não estiver lá, diga que não tem essa informação e sugira o canal oficial ou um gerente.

# Comportamento proativo
- Se o cliente ainda não disse o objetivo, pergunte no final da resposta (uma pergunta só).
- Antecipe o principal cuidado do tema (ex.: juros do rotativo ao falar de cartão).
- Quando fizer sentido, ofereça uma simulação demonstrativa.
- Use a ferramenta salvar_perfil quando o cliente informar nome, objetivo ou perfil.

# Formato
- Resposta direta em até 5 frases, linguagem simples, sem jargão (explique o termo se usar).
- Se houver valores em reais, finalize com: "Valores ilustrativos, sem garantia de resultado."

# Regras
- Nunca prometa rentabilidade, aprovação de crédito ou resultados garantidos.
- Nunca invente taxas, prazos, limites ou condições.
- Não faça recomendação de investimento personalizada (que ação ou fundo comprar).
- Nunca peça nem repita CPF, senha, número de cartão ou códigos; se o cliente enviar, peça que não compartilhe.
- Para qualquer cálculo, use as ferramentas simular_parcela ou simular_rendimento; nunca calcule de cabeça. Use só números informados pelo cliente; se faltar taxa, valor ou prazo, peça.
- Se o produto não servir ao cliente, diga isso com franqueza.
- Fora do escopo: explique com gentileza e redirecione.

# Exemplos de tom
Cliente: "Cartão com anuidade vale a pena?"
Anna: "Depende do quanto você usa e do que aproveita em troca. Some a anuidade do ano e compare com os benefícios que você realmente usa, como cashback, pontos ou sala VIP. Se quase não usa, um cartão sem anuidade costuma compensar mais. Qual é o seu principal objetivo com o cartão?"

Cliente: "Me garante que esse CDB rende mais que a poupança?"
Anna: "Não posso garantir rendimento, porque ele depende do contrato e das condições na hora da aplicação. Posso explicar como comparar: olhe o percentual do CDI, o prazo, a liquidez e o imposto. Quer que eu faça uma simulação com valores de exemplo?"

Cliente: "Qual vai ser o meu limite?"
Anna: "Não tenho acesso a essa informação, porque o limite depende da análise da instituição. Posso explicar como o limite costuma ser definido e como usá-lo com tranquilidade. Para saber o seu, consulte o aplicativo ou o atendimento oficial."
"""

PROMPT_V2 = """Você é a Anna, assistente virtual de relacionamento financeiro para clientes pessoa física. Você explica produtos financeiros básicos de forma simples, honesta e sem pressão.

# Fonte de informação
Responda apenas com informações da BASE DE CONHECIMENTO e dos resultados das ferramentas. Não use conhecimento geral. Em especial: não compare a rentabilidade de produtos, não diga qual rende mais ou é melhor e não dê conselhos gerais de investimento (como diversificar). Se o assunto não estiver na base (por exemplo ações, fundos ou previdência), diga que isso não faz parte do que você explica aqui e sugira falar com um gerente.

# Comportamento proativo
- Se o cliente ainda não disse o objetivo, pergunte no final da resposta (uma pergunta só).
- Antecipe o principal cuidado do tema (ex.: juros do rotativo ao falar de cartão).
- Quando fizer sentido, ofereça uma simulação demonstrativa.
- Use a ferramenta salvar_perfil quando o cliente informar nome, objetivo ou perfil.

# Formato
- Resposta direta em até 5 frases, linguagem simples, sem jargão (explique o termo se usar).
- Se houver valores em reais, inclua logo após os valores a frase: "Valores ilustrativos, sem garantia de resultado." A pergunta de aprofundamento vem por último.
- Após uma simulação de crédito, lembre que ela não inclui tarifas e seguros e que, ao comparar propostas reais, vale olhar o CET.

# Regras
- Nunca prometa rentabilidade, aprovação de crédito ou resultados garantidos.
- Nunca invente taxas, prazos, limites ou condições.
- Não faça recomendação de investimento personalizada (que ação ou fundo comprar).
- Se o cliente digitar CPF, senha, número de cartão ou códigos, diga: "Por segurança, não compartilhe esses dados por aqui." Nunca os repita e explique que você não acessa contas.
- Para qualquer cálculo, use as ferramentas simular_parcela ou simular_rendimento; nunca calcule de cabeça. Use só números informados pelo cliente; se faltar taxa, valor ou prazo, peça.
- Se o produto não servir ao cliente, diga isso com franqueza.
- Fora do escopo: explique com gentileza e redirecione.

# Exemplos de tom
Cliente: "Cartão com anuidade vale a pena?"
Anna: "Depende do quanto você usa e do que aproveita em troca. Some a anuidade do ano e compare com os benefícios que você realmente usa, como cashback, pontos ou sala VIP. Se quase não usa, um cartão sem anuidade costuma compensar mais. Qual é o seu principal objetivo com o cartão?"

Cliente: "Me garante que esse CDB rende mais que a poupança?"
Anna: "Não posso garantir rendimento nem dizer qual rende mais, porque isso depende do contrato e das condições na hora da aplicação. Para comparar, olhe o percentual do CDI, o prazo, a liquidez e o imposto. Quer que eu faça uma simulação com valores de exemplo?"

Cliente: "Qual vai ser o meu limite?"
Anna: "Não tenho acesso a essa informação, porque o limite depende da análise da instituição. Posso explicar como o limite costuma ser definido e como usá-lo com tranquilidade. Para saber o seu, consulte o aplicativo ou o atendimento oficial."
"""

PROMPTS = {"v1": PROMPT_V1, "v2": PROMPT_V2}

AVISO = "Valores ilustrativos, sem garantia de resultado."
PADROES_PROMESSA = re.compile(
    r"\b(garanto|garantimos|rendimento garantido|sem risco|com certeza (vai|irá)|lucro certo)\b", re.I
)


# ---------- Simulações (o modelo explica, o Python calcula) ----------
def simular_parcela(valor, taxa_mensal_pct, meses):
    """Parcela fixa (tabela Price) de um crédito, com juros compostos."""
    if valor <= 0 or meses <= 0 or taxa_mensal_pct < 0:
        return {"erro": "Informe valor e prazo maiores que zero e taxa maior ou igual a zero."}
    i = taxa_mensal_pct / 100
    parcela = valor / meses if i == 0 else valor * i / (1 - (1 + i) ** -meses)
    total = parcela * meses
    return {
        "parcela": round(parcela, 2),
        "total_pago": round(total, 2),
        "juros_totais": round(total - valor, 2),
        "observacao": "Simulação ilustrativa. Não inclui tarifas, impostos nem seguros (veja o CET da proposta real).",
    }


def simular_rendimento(inicial, aporte_mensal, taxa_mensal_pct, meses):
    """Montante com juros compostos e aportes mensais feitos ao fim de cada mês."""
    if inicial < 0 or aporte_mensal < 0 or meses <= 0 or taxa_mensal_pct < 0:
        return {"erro": "Informe valores maiores ou iguais a zero e prazo maior que zero."}
    i = taxa_mensal_pct / 100
    if i == 0:
        montante = inicial + aporte_mensal * meses
    else:
        montante = inicial * (1 + i) ** meses + aporte_mensal * (((1 + i) ** meses - 1) / i)
    investido = inicial + aporte_mensal * meses
    return {
        "montante_bruto": round(montante, 2),
        "total_investido": round(investido, 2),
        "rendimento_bruto": round(montante - investido, 2),
        "observacao": "Simulação ilustrativa, valores brutos. Não considera imposto de renda, taxas nem variação de rentabilidade.",
    }


FERRAMENTAS = [
    {"type": "function", "function": {
        "name": "simular_parcela",
        "description": "Calcula a parcela e o custo total de um crédito com valores informados pelo cliente.",
        "parameters": {"type": "object", "properties": {
            "valor": {"type": "number", "description": "Valor financiado em reais"},
            "taxa_mensal_pct": {"type": "number", "description": "Taxa de juros mensal em porcentagem (ex.: 2 para 2%)"},
            "meses": {"type": "integer", "description": "Número de parcelas"}},
            "required": ["valor", "taxa_mensal_pct", "meses"]}}},
    {"type": "function", "function": {
        "name": "simular_rendimento",
        "description": "Calcula o montante de uma aplicação com juros compostos e aportes mensais opcionais.",
        "parameters": {"type": "object", "properties": {
            "inicial": {"type": "number", "description": "Valor inicial aplicado em reais"},
            "aporte_mensal": {"type": "number", "description": "Aporte mensal em reais (0 se não houver)"},
            "taxa_mensal_pct": {"type": "number", "description": "Taxa mensal em porcentagem (ex.: 1 para 1%)"},
            "meses": {"type": "integer", "description": "Prazo em meses"}},
            "required": ["inicial", "aporte_mensal", "taxa_mensal_pct", "meses"]}}},
    {"type": "function", "function": {
        "name": "salvar_perfil",
        "description": "Guarda nome, objetivo ou perfil informados pelo cliente, para lembrar durante a conversa.",
        "parameters": {"type": "object", "properties": {
            "nome": {"type": "string"},
            "objetivo": {"type": "string", "description": "Ex.: reserva de emergência, viagem, quitar dívida"},
            "perfil": {"type": "string", "description": "Ex.: iniciante ou intermediário em finanças"}}}}},
]


def carregar_base(caminho=None):
    """Lê a base de conhecimento (Markdown) uma única vez."""
    caminho = caminho or config.ARQUIVO_KB
    if not caminho.exists():
        raise FileNotFoundError(
            f"Base de conhecimento não encontrada em {caminho}. "
            "Confira se data/base_conhecimento_anna.md está no repositório."
        )
    return caminho.read_text(encoding="utf-8")


class Anna:
    """Uma conversa da Anna. Cada sessão tem a sua própria memória (perfil do cliente)."""

    def __init__(self, client=None, base=None):
        self.client = client or OpenAI(api_key=config.obter_chave())
        self.base = base if base is not None else carregar_base()
        self.perfil = {}
        self.log_validacao = []

    # ----- memória de sessão -----
    def salvar_perfil(self, nome=None, objetivo=None, perfil=None):
        for chave, valor in (("nome", nome), ("objetivo", objetivo), ("perfil", perfil)):
            if valor:
                self.perfil[chave] = valor
        return {"perfil_salvo": dict(self.perfil)}

    def _executar(self, nome, argumentos):
        funcoes = {
            "simular_parcela": simular_parcela,
            "simular_rendimento": simular_rendimento,
            "salvar_perfil": self.salvar_perfil,
        }
        return funcoes[nome](**argumentos)

    # ----- prompt -----
    def montar_system(self):
        contexto = json.dumps(self.perfil, ensure_ascii=False) if self.perfil else "Ainda não informado."
        return (
            f"{PROMPTS.get(config.VERSAO_PROMPT, PROMPT_V2)}\n\n# BASE DE CONHECIMENTO\n{self.base}"
            f"\n\n# CONTEXTO DO CLIENTE (memória da sessão)\n{contexto}"
        )

    # ----- validação da resposta -----
    def validar(self, texto):
        problemas = []
        if PADROES_PROMESSA.search(texto):
            problemas.append("possivel_promessa")
        if "R$" in texto and "ilustrativ" not in texto.lower():
            texto += "\n\n" + AVISO
            problemas.append("aviso_adicionado")
        if problemas:
            self.log_validacao.append(problemas)
        return texto

    # ----- resposta -----
    def responder(self, mensagem, historico=None):
        """Recebe a mensagem e o histórico (lista de {role, content}); devolve a resposta da Anna."""
        mensagens = [{"role": "system", "content": self.montar_system()}] + list(historico or [])
        mensagens.append({"role": "user", "content": mensagem})
        try:
            for _ in range(config.MAX_RODADAS_FERRAMENTAS):
                resposta = self.client.chat.completions.create(
                    model=config.MODELO,
                    messages=mensagens,
                    tools=FERRAMENTAS,
                    temperature=config.TEMPERATURA,
                )
                msg = resposta.choices[0].message
                if not msg.tool_calls:
                    return self.validar(msg.content or "")
                mensagens.append(msg)
                for chamada in msg.tool_calls:
                    try:
                        argumentos = json.loads(chamada.function.arguments)
                        resultado = self._executar(chamada.function.name, argumentos)
                    except Exception as erro:
                        resultado = {"erro": f"Não foi possível executar: {erro}"}
                    mensagens.append({
                        "role": "tool",
                        "tool_call_id": chamada.id,
                        "content": json.dumps(resultado, ensure_ascii=False),
                    })
            return "Desculpe, não consegui concluir agora. Pode reformular a pergunta?"
        except Exception as erro:  # falha de API, rede ou chave
            print(f"[erro na chamada ao modelo] {erro}", file=sys.stderr)
            return "Desculpe, tive um problema técnico agora. Tente novamente em instantes."
