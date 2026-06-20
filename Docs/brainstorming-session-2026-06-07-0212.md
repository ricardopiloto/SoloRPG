---
stepsCompleted: [1, 2, 3, 4]
session_topic: 'RPG Solo Online baseado em WFRP4e com LLM como GM'
session_goals: 'Explorar e estruturar a ideia central do produto'
selected_approach: 'Analogical Thinking + SCAMPER + First Principles + Assumption Reversal'
techniques_used: ['Analogical Thinking', 'SCAMPER', 'First Principles', 'Assumption Reversal']
---

# Brainstorming Session Results

**Date:** 2026-06-06
**Topic:** RPG Solo Online — WFRP4e com LLM como GM

---

## Visão Central

Aplicação web de RPG solo onde uma LLM atua como GM real — com agenda própria, memória persistente e campanhas com começo, meio e fim. A experiência se inspira nos livros-jogo clássicos (estilo Bandeirantes/Fighting Fantasy) mas transcende o modelo de bifurcações fixas.

**Princípio-guia:** Para o jogador, deve ser irrelevante se o mestre é humano ou IA.

---

## A LLM como GM

- Define o tom e os objetivos da campanha na primeira sessão — sem revelar ao jogador
- Mantém banco de dados persistente: história, pontos marcantes, NPCs, decisões do jogador
- Usa esse contexto para guiar sessões futuras com coerência narrativa
- Cria situações desafiadoras mas não impossíveis — filosofia de GM justo
- Tem autonomia narrativa real: pode surpreender, subverter, recompensar

---

## Estrutura de Campanha

- **Primeira sessão:** LLM gera a campanha (cenário, tom, objetivos secretos, NPCs iniciais)
- **Sessões seguintes:** continuação com o mesmo personagem e história
- **Fim de campanha:** morte permanente do personagem OU conclusão da história central
- **Nova campanha:** LLM pergunta — continuar com mesmo personagem (nova história) ou gerar tudo do zero
- **Campanhas sem conclusão:** ficam registradas como histórias inacabadas — narrativamente significativo

---

## Estrutura de Sessão

- A LLM define a duração antes de começar e avisa que não é possível pausar
- Ao fim: resumo narrativo do que aconteceu + XP ganho
- O jogador pode gastar XP para comprar perícias e talentos (fiel ao WFRP4e)
- Loop: Sessão → XP → Progressão → Próxima Sessão

---

## Sistema de Jogo (WFRP4e Adaptado)

**Mantidos:**
- Rolagem de dados
- Sistema de Careers (carreiras)
- Ferimentos (wounds)
- Pontos de Fate (última defesa contra morte permanente)

**Removido:**
- Insanidade (Corruption/Insanity points)

**Morte:**
- Permanente quando Fate Points se esgotam
- A campanha fica sem conclusão — o mundo segue sem o herói

---

## Interface e Experiência

**Princípio central:** Sem controles de videogame. Sem mouse/teclado como input de ação.
O jogador conversa livremente com a LLM em linguagem natural — como num RPG de mesa real.

**Elementos visuais de apoio (não de controle):**
- Ilustrações de cenas geradas contextualmente
- Mapa que se revela conforme exploração
- Inventário visual do personagem
- Diário do personagem (log narrativo)

---

## Camadas de Identidade do Personagem

- **Criação:** personagem customizado pelo jogador OU personagem pré-gerado para entrada rápida
- **Reputação com facções:** o mundo reage às escolhas
- **Percepção social:** como NPCs e grupos enxergam o personagem
- **Karma:** eixo moral implícito (bom/mau) que influencia o mundo
- **Diário:** registro pessoal da jornada
- **Inventário visual:** itens com representação visual

---

## Imersão

- Remoção de elementos "videogame" preserva a sensação de RPG de mesa
- Impacto de decisões é imediato e narrativo, não mecânico-visual
- A LLM nunca quebra o personagem de GM — sem meta-comentários sobre ser IA
- A jornada deve se tornar pessoal para o jogador

---

## Questões em Aberto

- Stack técnica para memória persistente da LLM entre sessões
- Como estruturar o banco de dados narrativo (eventos, NPCs, decisões)
- Geração de imagens: on-demand ou pré-geradas por cena-tipo?
- Fidelidade das rolagens: o jogador vê os dados? A LLM rola internamente?
- Moderação: como garantir que a LLM não quebre o tom da campanha

