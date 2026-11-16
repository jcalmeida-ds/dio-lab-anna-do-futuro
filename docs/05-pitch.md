# Pitch (3 minutos)

> [!TIP]
> Os slides apoiam a fala e a demonstração mostra a solução na prática. O passo a passo de gravação está em `roteiro-video-pitch.md`.

## Roteiro Sugerido

### 1. O Problema (30 seg)
> Qual dor do cliente você resolve?

Clientes pessoa física têm dúvidas e resistências sobre produtos financeiros básicos (cartão, consórcio, CDB, seguro de vida e crédito pessoal). A informação costuma ser confusa, o que leva a decisões ruins ou adiadas e ao risco de endividamento, como pagar só o mínimo da fatura. Além disso, o atendimento humano nem sempre está disponível no momento da dúvida.

---

### 2. A Solução (1 min)
> Como seu agente resolve esse problema?

A Anna é uma assistente virtual de IA generativa para relacionamento financeiro. Ela explica produtos em linguagem simples, usando apenas uma base de conhecimento controlada, faz simulações calculadas por funções em Python, lembra o nome e o objetivo do cliente durante a conversa e segue regras de segurança (sem promessas de rendimento, sem recomendação personalizada de investimento e sem pedir dados sensíveis). Foi construída no Google Colab, com Python, a API da OpenAI e interface em Gradio.

---

### 3. Demonstração (1 min)
> Mostre o agente funcionando (pode ser gravação de tela)

Gravação de tela do chat da Anna, com quatro interações:

1. **Dúvida sobre produto:** "Cartão com anuidade vale a pena?" A Anna responde em poucas frases e pergunta o objetivo do cliente.
2. **Objetivo e simulação:** o cliente informa o nome e o objetivo (viagem em 12 meses) e pede a simulação de R$ 5.000 a 1% ao mês por 12 meses. O valor de R$ 5.634,13 vem da função em Python, com o aviso de valores ilustrativos.
3. **Memória de contexto:** "Qual era mesmo o meu objetivo?" A Anna lembra.
4. **Segurança:** "Me garante que um CDB rende mais que a poupança?" A Anna recusa a garantia e explica como comparar.

---

### 4. Diferencial e Impacto (30 seg)
> Por que essa solução é inovadora e qual é o impacto dela na sociedade?

**Diferencial:** a confiança. A Anna combina uma base de conhecimento controlada, cálculos determinísticos em Python e regras de segurança, e teve a qualidade medida: duas versões do prompt foram avaliadas com 17 casos de teste, e a segunda corrigiu falhas da primeira.

**Impacto:** levar educação financeira clara e sem pressão a mais pessoas, para que decidam com consciência e evitem dívidas desnecessárias.

---

## Checklist do Pitch

- [X] Duração máxima de 3 minutos
- [X] Problema claramente definido
- [X] Solução demonstrada na prática
- [X] Diferencial explicado
- [X] Áudio e vídeo com boa qualidade

---

## Link do Vídeo

[Link do vídeo]
