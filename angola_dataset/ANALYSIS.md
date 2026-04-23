# Análise Preditiva de Sucessão Presidencial em Angola

## Resumo

Quem tem o perfil mais completo para suceder a João Lourenço? Em vez de apostar em 3 ou 4 nomes, este estudo pontua todos os 101 membros do Bureau Político do MPLA em 10 variáveis biográficas e políticas, com peso igual (10% cada). O ranking sai dos dados, não de uma escolha prévia. A análise é calibrada contra 12 casos históricos de sucessão em sistemas de partido dominante — de Angola e Moçambique à China, Rússia e Vietname.

---

## 1. Porquê este estudo

Angola é governada pelo MPLA desde 1975. O candidato presidencial do partido não é escolhido por primárias nem por eleição popular interna — é proposto pelo Bureau Político, conforme o Art. 120 dos estatutos (alterado em Dezembro 2024). Perceber quem reúne as condições para essa proposta é, na prática, perceber como funciona a sucessão em Angola.

A ideia de que a sucessão nestes sistemas é imprevisível não resiste à evidência. Brownlee (2007), Levitsky & Way (2010) e Magaloni (2006) mostram que há padrões recorrentes: controlo do aparelho de segurança, antiguidade no partido, proximidade ao líder incumbente. O que fizemos foi testar se esses padrões se aplicam ao caso angolano actual.

---

## 2. Como fizemos

### 2.1 Quem foi avaliado

Todos os **101 membros do Bureau Político do MPLA** (lista do VIII Congresso, Dezembro 2021, com actualizações até Dezembro 2024). João Lourenço foi excluído como incumbente. Adicionámos dois nomes relevantes que estão fora do BP actual — Fernando Miala (ex-chefe do SINSE) e Ana Dias Lourenço (ex-Ministra do Planeamento, candidata a VP do BAD). Total: **102 membros pontuados**.

A vantagem desta abordagem é simples: não há pré-selecção. O ranking emerge dos scores. Se alguém que não estava nos "favoritos" da comunicação social tiver um perfil forte, aparece.

### 2.2 O problema dos dados incompletos

Dos 101 membros do BP, cerca de 60 aparecem nas listas oficiais apenas como "Membro BP" — sem cargo governamental conhecido, sem data de nascimento publicada, sem biografia acessível. Para estes, usámos scores base conservadores (31/100). Não é ideal, mas é transparente: estão marcados no dataset e qualquer investigador pode melhorar os scores quando obtiver dados.

Os restantes ~40 membros têm scores detalhados (★), baseados em biografias verificadas em fontes como governo.gov.ao, MPLA.ao, Wikipedia, VOA Português, IMF Connect e Banco Africano de Desenvolvimento.

### 2.3 As 10 variáveis

| Variável | O que mede |
|---|---|
| **Cargo actual** | Importância do cargo presente (10 = PR/VP partido; 3 = cargo técnico) |
| **Antiguidade no partido** | Anos de militância + hierarquia atingida no MPLA |
| **Carteira de segurança** | Controlo sobre FAA, Interior ou serviços de informações |
| **Proximidade ao PR** | Relação de confiança directa com João Lourenço |
| **Posição no Bureau Político** | Hierarquia dentro do BP — o órgão que propõe o candidato |
| **Trajectória** | Quantas pastas diferentes ocupou e com que velocidade subiu (especialmente desde 2017) |
| **Capital militar** | Posto nas FAA + redes militares |
| **Capital académico** | Grau académico e relevância da formação |
| **Perfil internacional** | Visibilidade no exterior, línguas, formação fora de Angola |
| **Factor etário** | Faixa óptima 44–62 anos, calibrada nos 12 casos comparados |

### 2.4 Porquê pesos iguais

Todas as variáveis pesam 10%. A tentação de dar mais peso à segurança ou ao partido é grande, mas qualquer ponderação diferenciada reflecte uma opinião sobre o que "importa mais" — e opiniões variam. Com pesos iguais, o modelo é transparente e qualquer pessoa pode recalcular com os pesos que preferir. O código está disponível.

Para quem quer ver o efeito de pesos diferentes, incluímos uma análise de sensibilidade com 4 cenários alternativos.

---

## 3. O que os dados mostram

### 3.1 Top 20

| # | Candidato | Score | Porquê |
|---|---|---|---|
| 1 | **Manuel Homem** | 72.0 | Min. Interior + BP + trajectória rápida + 46 anos |
| 2 | **Francisco Furtado** | 72.0 | Casa Segurança PR + ex-Chefe EM FAA + General + proximidade 10 |
| 3 | **Mara Quiosa** | 68.0 | VP MPLA (95.7% votos) + 26 anos partido + 44 anos |
| 4 | **Adão de Almeida** | 68.0 | Presidente AN + ex-Casa Civil + trajectória diversa + 46 anos |
| 5 | **Eugénio Laborinho** | 65.0 | Ex-Min. Interior + Ten.-General + 50 anos partido — mas 70 anos |
| 6 | **Vera Daves** | 62.0 | Min. Finanças + FMI/BM + 1.ª mulher no cargo — mas sem segurança |
| 7 | **Carlos Feijó** | 59.0 | Doutoramento + ex-Casa Civil — mas perfil puramente civil |
| 8 | **Nunes Júnior** | 58.0 | Min. Economia + idade óptima — mas sem segurança |
| 9 | **Ana Dias Lourenço** | 58.0 | Doutoramento Lovaina + BAD — mas sem segurança nem militar |
| 10 | **Paulo Pombolo** | 56.0 | Sec. Geral MPLA (#3) + 45 anos partido — mas academia e internacional fracos |
| 11 | **Rui Falcão Andrade** | 56.0 | PGR + papel na anti-corrupção de JLo |
| 12 | **Joana Lina** | 55.0 | Gov. Luanda + nomeada por JLo + 55 anos |
| 13 | **Tete António** | 55.0 | MNE + ex-embaixador EUA + perfil internacional alto |
| 14 | **Manuel Augusto** | 55.0 | Ex-MNE + Sec. Relações Internacionais BP |
| 15 | **Bornito de Sousa** | 54.0 | Ex-VP República + Doutoramento — mas não reconduzido |
| 16 | **Sílvia Lutucuta** | 54.0 | Min. Saúde + Doutoramento + 55 anos |
| 17 | **Carolina Cerqueira** | 51.0 | Ex-Presidente AN — mas substituída por Almeida |
| 18 | **Pitra da Costa Neto** | 51.0 | Veterano + General — mas 70 anos |
| 19 | **Mpinda Simão** | 51.0 | Gov. Benguela + idade óptima |
| 20 | **Archer Mangueira** | 51.0 | Gov. Namibe + perfil económico |

### 3.2 O que salta à vista

**O eixo segurança domina.** Os três candidatos com carteira de segurança ou defesa (Homem, Furtado, Laborinho) ocupam os três primeiros lugares. Não é acidental: nos 12 casos internacionais, metade dos sucessores controlava o aparelho de segurança. O caso mais recente — Tô Lâm no Vietname (2024), que foi Ministro da Segurança Pública durante 16 anos — reforça o padrão.

**Manuel Homem é quase um decalque de Lourenço.** Ministro da pasta de segurança, no Bureau Político, promoção rápida desde 2017, idade favorável. O padrão que levou Lourenço ao poder em 2017 está a repetir-se.

**Mara Quiosa tem a vantagem institucional mas não a de segurança.** É VP do MPLA com 95.7% dos votos, o que lhe dá a posição formal mais forte. Mas o score em segurança (3/10) e militar (0/10) são os mais baixos do top 5. Se o BP seguir a hierarquia formal, ela é favorita. Se seguir o padrão histórico, não.

**Os tecnocratas (Daves, Feijó, Ana Dias Lourenço) têm tecto.** Perfil académico e internacional excelente, mas sem capital de segurança nem militar. Num sistema onde o controlo do aparelho coercivo pesa, este é um limite estrutural.

**Paulo Pombolo — o "homem do partido" — sofre com pesos iguais.** Como Secretário-Geral (#3 no MPLA), controla a máquina partidária. Mas com pesos iguais, os scores baixos em academia (4), internacional (3) e militar (0) arrastam-no para o 10.º lugar. Com pesos que privilegiem o partido e o BP, sobe significativamente.

**Fernando Miala é o caso-limite.** Ex-chefe do SINSE com scores de segurança (9) e militar (9) altíssimos, mas afastado do poder desde 2009. Score final: 49.0. Demonstra que capital técnico sem acesso ao aparelho político vale pouco.

### 3.3 E se os pesos fossem diferentes?

Testámos 4 cenários para os top 15:

| Cenário | O que muda | #1 | #2 |
|---|---|---|---|
| **Base (iguais)** | Tudo pesa 10% | Homem / Furtado (72) | Quiosa / Almeida (68) |
| **Abertura** | Academia e internacional sobem para 15% | Homem (76) | Almeida (74) |
| **Tensão** | Segurança sobe para 25%, militar para 12% | Furtado (87!) | Homem (71) |
| **Renovação** | Cargo 20%, trajectória 15% | Homem (79) | Furtado (77) |

Manuel Homem é o único candidato que fica no top 2 em todos os cenários. Furtado dispara no cenário de tensão (87 pontos!) mas a idade penaliza-o nos outros. Quiosa é consistentemente 3.ª ou 4.ª.

### 3.4 O que dizem os 12 casos históricos

| Padrão | Frequência |
|---|---|
| Estava na liderança do partido | 11/12 (92%) |
| Tinha carteira de segurança | 6/12 (50%) |
| Tinha capital militar | 6/12 (50%) |
| Era VP antes de presidir | 6/12 (50%) |
| Idade mediana de chegada | 56 anos |

Os casos mais análogos a Angola são Moçambique (Nyusi, 2015: Min. Defesa via Frelimo) e Vietname (Tô Lâm, 2024: Min. Segurança Pública via PCV). Ambos seguem o padrão segurança → presidência.

---

## 4. O que este estudo não consegue captar

1. **Redes informais** — Quem janta com quem, que favores foram trocados, que alianças existem entre bastidores. Nenhum dataset captura isto.
2. **Dados incompletos** — 60% dos membros do BP são fantasmas informacionais. Não temos biografias, idades, nem percursos. Os scores base de 31/100 são um placeholder honesto, não uma avaliação.
3. **Poucos casos comparados** — 12 é melhor do que 0, mas não chega para inferência estatística séria. O modelo Random Forest é exploratório.
4. **Dinheiro e negócios** — Capital económico pessoal, relações com o sector privado, interesses em sectores estratégicos (petróleo, diamantes, telecomunicações). Não está nos dados.
5. **O factor surpresa** — Lourenço não era o favorito óbvio em 2012. Quem emergir pode não ser quem hoje parece mais forte.
6. **Snapshot de Abril 2025** — Uma remodelação governamental pode alterar tudo. Os dados reflectem a configuração política actual.

---

## 5. Conclusão

Os dados apontam numa direcção clara: os perfis com carteira de segurança, proximidade ao Presidente e posição forte no Bureau Político dominam o ranking. Manuel Homem e Francisco Furtado lideram consistentemente, com Mara Quiosa e Adão de Almeida logo atrás.

Mas há uma tensão entre o padrão histórico e a realidade institucional de 2024. A eleição de Quiosa como VP do MPLA com 95.7% dos votos e a alteração do Art. 120 sugerem que Lourenço pode estar a preparar uma transição diferente. Se o BP seguir a hierarquia formal, Quiosa parte na frente. Se seguir o padrão que o próprio Lourenço usou em 2017, o eixo segurança prevalece.

O que este dataset oferece não é uma resposta definitiva — é uma base para discutir com dados em vez de intuições. Os scores são discutíveis, os pesos são ajustáveis, e o código está aberto. Que se discuta.

---

## Citação

```
"Predictive Analysis of Presidential Succession in Angola's Dominant-Party System",
Dataset v1.0, Angola Succession Dataset, 2026.
```

## Licença

CC BY 4.0 — Creative Commons Attribution 4.0 International
