# Angola Succession Dataset

Dataset aberto para análise de sucessão presidencial em Angola. Pontua todos os 101 membros do Bureau Político do MPLA em 10 variáveis biográficas e políticas, com pesos iguais. Inclui 12 casos históricos internacionais para calibração.

A abordagem é simples: em vez de pré-seleccionar 3 ou 4 "favoritos", pontuamos toda a gente e deixamos o ranking sair dos dados.

---

## Como está organizado

```
angola_dataset/
├── data/
│   ├── angola_bp_scored.csv       # 102 membros scored (100 do BP + 2 extras)
│   ├── angola_bp_full.csv         # Lista original dos 101 membros do BP
│   ├── comparative_cases.csv      # 12 casos históricos internacionais
│   ├── variables_schema.csv       # Dicionário das variáveis e pesos
│   ├── angola_bp_scored.json      # Versão JSON
│   ├── comparative_cases.json     # Versão JSON
│   └── relatorio_analise.txt      # Relatório automático
├── figures/
│   ├── ranking_bars.png           # Top 15 — barras horizontais
│   ├── heatmap_scores.png         # Matriz de scores — top 15
│   ├── radar_candidatos.png       # Perfil radar por candidato — top 15
│   └── var_frequency.png          # Frequência de variáveis nos 12 casos
├── scripts/
│   ├── build_dataset.py           # Gera todos os CSVs e JSONs
│   └── analysis.py                # Gráficos + sensibilidade + modelo RF
├── ANALYSIS.md                    # Análise completa (o "paper")
├── LINKEDIN_POST.md               # Post para publicação
├── CITATION.cff                   # Para citação automática no GitHub
├── LICENSE                        # CC BY 4.0
└── README.md
```

---

## Para correr

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install pandas numpy matplotlib scikit-learn

python scripts/build_dataset.py    # gera os datasets (pontua os 102 membros)
python scripts/analysis.py         # gráficos + análise de sensibilidade
```

---

## O que é pontuado e como

Cada membro do BP recebe um score de 0 a 10 em cada uma destas variáveis:

| Variável | Exemplo de 10 | Exemplo de 1–2 |
|---|---|---|
| Cargo actual | PR, VP partido, Presidente AN | Sem cargo executivo |
| Antiguidade no partido | 30+ anos + fundador do BP | < 10 anos |
| Carteira de segurança | Chefia FAA + Min. Interior | Perfil puramente civil |
| Proximidade ao PR | Casa de Segurança, VP escolhida por JLo | Sem laço documentado |
| Posição no Bureau Político | VP do MPLA | Membro periférico |
| Trajectória | 4+ pastas em < 8 anos | 1 pasta, sem progressão |
| Capital militar | Tenente-General + ex-Chefe EM FAA | Sem passagem militar |
| Capital académico | Doutoramento em área estratégica | Formação básica |
| Perfil internacional | FMI/BM/ONU regular + 3 línguas | Formação nacional apenas |
| Factor etário | 44–52 anos | 70+ anos |

Todas pesam **10% cada**. Quem discordar dos pesos pode recalcular — o código está aí para isso.

Membros sem dados públicos suficientes recebem scores base conservadores (31/100) e estão identificados no dataset.

---

## Top 15 (Abril 2025)

| # | Candidato | Score | Cargo/Função |
|---|---|---|---|
| 1 | Manuel Homem | 72.0 | Ministro do Interior |
| 2 | Francisco Furtado | 72.0 | Casa de Segurança do PR |
| 3 | Mara Quiosa | 68.0 | Vice-Presidente do MPLA |
| 4 | Adão de Almeida | 68.0 | Presidente da Assembleia Nacional |
| 5 | Eugénio Laborinho | 65.0 | Ex-Min. Interior / Tenente-General |
| 6 | Vera Daves | 62.0 | Ministra das Finanças |
| 7 | Carlos Feijó | 59.0 | Prof. Catedrático / Ex-Casa Civil |
| 8 | Nunes Júnior | 58.0 | Min. Economia e Planeamento |
| 9 | Ana Dias Lourenço | 58.0 | Ex-Min. Planeamento / BAD |
| 10 | Paulo Pombolo | 56.0 | Secretário-Geral do MPLA |
| 11 | Rui Falcão Andrade | 56.0 | Procurador-Geral da República |
| 12 | Joana Lina | 55.0 | Governadora de Luanda |
| 13 | Tete António | 55.0 | Min. Relações Exteriores |
| 14 | Manuel Augusto | 55.0 | Sec. Rel. Internacionais BP |
| 15 | Bornito de Sousa | 54.0 | Ex-VP da República |

Para a análise completa — incluindo sensibilidade, casos comparados e limitações — ver [ANALYSIS.md](ANALYSIS.md).

---

## Fontes

- MPLA.ao (biográficos oficiais)
- governo.gov.ao (biografias ministeriais)
- Jornal ÉME (lista BP, VIII Congresso, Dez 2021)
- VOA Português (eleição VP MPLA, Dez 2024)
- Wikipedia PT/EN (perfis verificados)
- IMF Connect / World Bank Live (perfis internacionais)
- BAD (Ana Dias Lourenço)
- Literatura: Brownlee (2007), Levitsky & Way (2010), Magaloni (2006)

---

## Citação

```
"Predictive Analysis of Presidential Succession in Angola's Dominant-Party System",
Dataset v1.0, Angola Succession Dataset, 2025.
```

O GitHub reconhece automaticamente o ficheiro `CITATION.cff` — basta clicar em "Cite this repository".

---

## Licença

[CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) — Usar, adaptar e redistribuir livremente, com atribuição.
