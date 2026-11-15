# Código da Aplicação

Esta pasta contém o código da **Anna**, assistente virtual de relacionamento financeiro (IA generativa com a API da OpenAI e interface em Gradio).

## Estrutura

```
src/
├── app.py              # Interface de chat (Gradio)
├── agente.py           # Lógica da Anna: prompt, simulações, memória e validação
├── config.py           # Configurações (chave de API, modelo, caminhos)
├── requirements.txt    # Dependências
└── Anna_Assistente_Virtual.ipynb   # Versão para Google Colab, com a avaliação (Etapa 5)
```

A base de conhecimento fica em `data/base_conhecimento_anna.md`, na raiz do repositório.

## Como funciona

1. `app.py` abre o chat e cria uma instância da Anna para cada sessão (cada conversa tem a sua memória).
2. `agente.py` monta o prompt de sistema (regras + base de conhecimento + memória), chama o modelo e executa as ferramentas pedidas por ele:
   - `simular_parcela` e `simular_rendimento`: cálculos em Python (o modelo explica, o Python calcula);
   - `salvar_perfil`: guarda nome, objetivo e perfil durante a conversa.
3. Antes de responder, a validação checa possíveis promessas de rendimento e inclui o aviso de valores ilustrativos quando há números em reais.
4. Se a chamada ao modelo falhar (chave, rede ou limite), a Anna devolve uma mensagem amigável e o erro técnico vai para o terminal.

## Como rodar

### Localmente

```bash
# A partir da pasta src/
pip install -r requirements.txt

# Crie um arquivo .env nesta pasta com a sua chave (não envie para o GitHub)
echo "OPENAI_API_KEY=sua-chave-aqui" > .env

python app.py
```

Abra o endereço que aparecer no terminal (normalmente http://127.0.0.1:7860).

Variáveis opcionais:

| Variável | Uso |
|---|---|
| `OPENAI_MODEL` | Modelo a usar (padrão definido em `config.py`) |
| `VERSAO_PROMPT` | Rótulo da versão do prompt (v1, v2) |
| `ARQUIVO_KB` | Caminho alternativo para a base de conhecimento |
| `GRADIO_SHARE=1` | Gera um link público temporário |

### No Google Colab

Abra `Anna_Assistente_Virtual.ipynb`, crie o segredo `OPENAI_API_KEY` no painel **Secrets**, baixe a base de conhecimento (célula com `wget` do link Raw) e execute as células em ordem. O notebook também traz a avaliação com os casos de teste.

## Segurança

- Nunca coloque a chave da API no código nem no GitHub. Inclua `.env` no `.gitignore`.
- O uso da API pode gerar custo pequeno na conta de quem executar.
- Não digite dados pessoais reais nos testes. A Anna é educativa e não acessa dados de clientes.
