# Base de Conhecimento

## Dados Utilizados

| Arquivo | Formato | Utilização no Agente |
|---------|---------|---------------------|
| `base_conhecimento_anna.md` | Markdown | Fonte única de conhecimento da Anna: 21 itens de perguntas e respostas sobre cartão de crédito, consórcio, CDB, seguro de vida, crédito pessoal, educação financeira e segurança, cada um com palavras-chave, cuidado e quando o produto não é indicado |
| Memória de sessão (`PERFIL`) | Dicionário Python em memória | Guarda nome, objetivo e perfil informados pelo cliente durante a conversa, para personalizar as respostas sem armazenar dados sensíveis |

Os arquivos de exemplo do template (`historico_atendimento.csv`, `perfil_investidor.json`, `produtos_financeiros.json` e `transacoes.csv`) **não foram utilizados** nesta versão. A Anna é uma assistente educativa que não acessa dados de clientes, contas ou transações; a personalização acontece apenas pelo que o cliente conta na própria conversa.

---

## Adaptações nos Dados

Em vez de adaptar os dados mockados, criei uma base própria, voltada ao objetivo da Anna: explicar produtos financeiros básicos e tratar dúvidas e resistências comuns dos clientes.

- **Conteúdo:** 21 itens em 7 categorias (cartão de crédito 4, consórcio 4, CDB 4, seguro de vida 3, crédito pessoal 3, educação financeira 2 e segurança 1).
- **Estrutura de cada item:** identificador, produto, palavras-chave, pergunta, resposta, cuidado e "não é indicado quando". Os campos de cuidado e de restrição ensinam a Anna a falar também dos riscos e de quando o produto não serve.
- **Perguntas baseadas em dúvidas reais de atendimento,** como "cartão com anuidade vale a pena?" e "consórcio demora demais?", escritas sem dados de clientes e sem informações internas de nenhuma instituição.
- **Sem números que mudam:** a base não traz taxas, limites nem alíquotas de nenhuma instituição. Para temas sujeitos a regras vigentes (como FGC e imposto de renda), ela orienta o cliente a consultar a fonte oficial.
- **Cálculos fora da base:** parcelas e rendimentos não ficam no texto, mas em funções em Python que o modelo chama durante a conversa.

---

## Estratégia de Integração

### Como os dados são carregados?

O arquivo `base_conhecimento_anna.md` é enviado ao ambiente do Google Colab e lido uma única vez, no início da execução do notebook, por meio de `Path("base_conhecimento_anna.md").read_text(encoding="utf-8")`. O resultado fica guardado na variável `BASE_CONHECIMENTO` . Se o arquivo não for encontrado, o notebook exibe uma mensagem pedindo que ele seja enviado.

### Como os dados são usados no prompt?

A base inteira vai no **system prompt**, a cada chamada ao modelo, junto com as regras de comportamento e a memória da sessão. A função `montar_system()` monta o prompt na seguinte ordem:

1. Prompt base da Anna (papel, regras, formato e exemplos de tom).
2. Base de conhecimento completa.
3. Contexto do cliente (memória de sessão: nome, objetivo e perfil).

**Por que não usar RAG (busca semântica):** a base é pequena e cabe com folga no contexto do modelo, o que simplifica a arquitetura e evita falhas de recuperação. Se a base crescer muito, o caminho natural é recuperar apenas os trechos relevantes a cada pergunta.

**Cálculos:** não passam pelos dados. O modelo aciona as ferramentas `simular_parcela` e `simular_rendimento` (function calling), e o resultado volta ao modelo como fonte do número apresentado ao cliente.

---

## Exemplo de Contexto Montado

```
# PROMPT BASE (resumo)
Você é a Anna, assistente virtual de relacionamento financeiro...
Responda apenas com base na BASE DE CONHECIMENTO e nos resultados das ferramentas.
Nunca prometa rentabilidade... Para cálculos, use as ferramentas.

# BASE DE CONHECIMENTO
### CC-01
- Produto: Cartão de crédito
- Palavras-chave: anuidade, vale a pena, custo
- Pergunta: Cartão com anuidade vale a pena?
- Resposta: Depende de quanto você usa e do que ganha em troca...
- Cuidado: benefícios que você não usa não compensam o custo...
- Não é indicado quando: você tem dificuldade de pagar a fatura em dia...

### CS-01
...(demais itens, até SG-01)

# CONTEXTO DO CLIENTE (memória da sessão)
{"nome": "Marina", "objetivo": "viagem em 12 meses"}
```

Mensagem do cliente: "Qual dos produtos que você explica combina mais com esse objetivo?"

A Anna responde com base nos itens da base e no objetivo guardado na memória, sem inventar condições e sem fazer recomendação personalizada de investimento.
