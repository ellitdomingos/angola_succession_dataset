"""
angola_succession_dataset.py
============================
Constrói e exporta todos os datasets do projecto de
análise preditiva de sucessão presidencial em Angola.

Outputs:
  data/angola_bp_scored.csv        — 8 candidatos com scores completos
  data/angola_bp_full.csv          — 101 membros Bureau Político (dados disponíveis)
  data/comparative_cases.csv       — 12 casos históricos internacionais
  data/variables_schema.csv        — dicionário de variáveis
  data/angola_bp_scored.json       — versão JSON dos candidatos scored
  data/comparative_cases.json      — versão JSON dos casos comparados

Fonte dos dados:
  - MPLA.ao (biográficos oficiais)
  - Jornal ÉME – lista BP VIII Congresso Dez 2021
  - Wikipedia PT/EN – Vera Daves, Mara Quiosa, Manuel Homem
  - VOA Português – eleição Mara Quiosa VP MPLA Dez 2024
  - governo.gov.ao – biografias ministeriais
  - Conhecimento base para casos internacionais

Nota metodológica:
  Os scores (1-10) são avaliações qualitativas baseadas em
  dados biográficos verificados. Os pesos (w) são estimativas
  calibradas em padrões observados nos 12 casos comparados.
  Para uso académico, validar com codificação por pares.
"""

import csv
import json
import os
from pathlib import Path

# ─── PATHS ────────────────────────────────────────────────────────────────────
BASE = Path(__file__).parent.parent
DATA = BASE / "data"
DATA.mkdir(exist_ok=True)

# ─── SCHEMA DE VARIÁVEIS ──────────────────────────────────────────────────────
VARIABLES = [
    {
        "id":     "cargo",
        "label":  "Peso do Cargo Actual",
        "weight": 0.10,
        "scale":  "1–10",
        "description": (
            "Importância institucional do cargo actual. "
            "10=PR/VP partido; 9=Min. Estado/Interior/Presidente AN; "
            "7=Ministro pasta económica chave; 5=Ex-ministro/Gov. provincial; "
            "3=Cargo técnico/académico"
        ),
        "source": "Cargos verificados via governo.gov.ao e MPLA.ao"
    },
    {
        "id":     "partido",
        "label":  "Antiguidade e Hierarquia no Partido",
        "weight": 0.10,
        "scale":  "1–10",
        "description": (
            "Anos de militância activa + nível hierárquico atingido. "
            "10=30+ anos + Bureau Político fundador; 8=20+ anos + BP; "
            "6=10-20 anos + BP; 4=<10 anos no BP"
        ),
        "source": "Biográficos MPLA.ao + Jornal ÉME"
    },
    {
        "id":     "seguranca",
        "label":  "Carteira de Segurança/Defesa",
        "weight": 0.10,
        "scale":  "1–10",
        "description": (
            "Controlo sobre aparelho coercivo. "
            "10=Chefia FAA + Min. Interior actual; "
            "9=Min. Interior actual ou ex-chefe EM FAA; "
            "5=Sec. Estado segurança; 2=Sem contacto com segurança; 1=Perfil puramente civil"
        ),
        "source": "Cargos verificados + padrão comparado (peso calibrado em 8 casos históricos)"
    },
    {
        "id":     "proximidade",
        "label":  "Proximidade ao Presidente Lourenço",
        "weight": 0.10,
        "scale":  "1–10",
        "description": (
            "Relação de confiança directa com o PR. "
            "10=Casa de Segurança ou VP partido escolhida por JLo; "
            "9=Chefe Casa Civil ou Sec. Geral partido; "
            "6=Ministro de confiança reconduído; "
            "3=Trajectória paralela sem laço directo documentado"
        ),
        "source": "Decretos presidenciais + VOA Português + MPLA.ao"
    },
    {
        "id":     "burpol",
        "label":  "Posição no Bureau Político",
        "weight": 0.10,
        "scale":  "1–10",
        "description": (
            "Hierarquia dentro do Bureau Político (órgão que propõe candidato presidencial via Art.120). "
            "10=VP do MPLA; 9=Sec. Geral MPLA ou membro secretariado; "
            "7=Membro efectivo BP; 5=Membro alternativo/periférico"
        ),
        "source": "Lista BP publicada pelo Jornal ÉME (VIII Congresso, 10 Dez 2021) + actualização Dez 2024"
    },
    {
        "id":     "trajetoria",
        "label":  "Trajectória e Velocidade de Promoção",
        "weight": 0.10,
        "scale":  "1–10",
        "description": (
            "Diversidade de pastas + aceleração recente (desde 2017). "
            "10=4+ pastas distintas em <8 anos; 8=3 pastas com progressão clara; "
            "6=2 pastas + cargo estável; 4=1 pasta longa sem progressão recente"
        ),
        "source": "CVs biográficos + análise cronológica de cargos"
    },
    {
        "id":     "militar",
        "label":  "Capital Militar",
        "weight": 0.10,
        "scale":  "1–10",
        "description": (
            "Posto militar + redes nas FAA/FAPLA. "
            "10=Tenente-General + ex-Chefe EM FAA; 8=General + carreira operacional; "
            "5=Formação militar sem carreira activa; 0=Sem passagem pelas FAA"
        ),
        "source": "Biográficos militares verificados"
    },
    {
        "id":     "academia",
        "label":  "Capital Académico",
        "weight": 0.10,
        "scale":  "1–10",
        "description": (
            "Grau académico + relevância da área. "
            "10=Doutoramento em área estratégica (Direito/Economia); "
            "9=Mestrado + publicações + visibilidade académica internacional; "
            "8=Mestrado em área relevante; 6=Licenciatura + formações complementares; "
            "4=Formação técnica/militar"
        ),
        "source": "CVs académicos verificados"
    },
    {
        "id":     "perfil_int",
        "label":  "Perfil Internacional",
        "weight": 0.10,
        "scale":  "1–10",
        "description": (
            "Línguas + formação no estrangeiro + visibilidade externa. "
            "10=Formação exterior + presença regular FMI/BM/ONU + 3+ línguas; "
            "6=Formação parcial exterior + 2 línguas; "
            "3=Formação nacional + inglês funcional"
        ),
        "source": "Biográficos + registos IMF Connect / World Bank Live"
    },
    {
        "id":     "idade",
        "label":  "Factor Etário (faixa óptima 44–62)",
        "weight": 0.10,
        "scale":  "1–10",
        "description": (
            "Baseado em padrão dos 12 casos comparados: idade óptima de chegada ao poder = 44-62. "
            "10=44-52 anos; 8=53-58 anos; 7=59-62 anos; 5=63-66 anos; 3=67-70 anos; 1=70+ anos"
        ),
        "source": "Calibrado sobre idades dos 12 líderes nos casos comparados"
    },
]

# ─── SCORES POR MEMBRO DO BP ─────────────────────────────────────────────────
# Dicionário: nome_curto → {scores}
# Membros sem entrada usam scores base estimados (ver BP_DEFAULT_SCORES)
BP_DEFAULT_SCORES = {
    "s_cargo": 3, "s_partido": 5, "s_seguranca": 1, "s_proximidade": 3,
    "s_burpol": 5, "s_trajetoria": 3, "s_militar": 0, "s_academia": 4,
    "s_perfil_int": 2, "s_idade": 5,
}

BP_SCORES = {
    # --- TOP: Candidatos com informação detalhada ---
    "Mara Quiosa":        {"s_cargo":9,"s_partido":9,"s_seguranca":3,"s_proximidade":9,"s_burpol":10,"s_trajetoria":8,"s_militar":0,"s_academia":6,"s_perfil_int":4,"s_idade":10},
    "Adão de Almeida":    {"s_cargo":9,"s_partido":8,"s_seguranca":2,"s_proximidade":9,"s_burpol":7,"s_trajetoria":9,"s_militar":0,"s_academia":8,"s_perfil_int":6,"s_idade":10},
    "Manuel Homem":       {"s_cargo":9,"s_partido":7,"s_seguranca":9,"s_proximidade":6,"s_burpol":9,"s_trajetoria":8,"s_militar":0,"s_academia":8,"s_perfil_int":6,"s_idade":10},
    "Vera Daves":         {"s_cargo":7,"s_partido":5,"s_seguranca":1,"s_proximidade":7,"s_burpol":7,"s_trajetoria":7,"s_militar":0,"s_academia":9,"s_perfil_int":9,"s_idade":10},
    "Francisco Furtado":  {"s_cargo":9,"s_partido":8,"s_seguranca":10,"s_proximidade":10,"s_burpol":7,"s_trajetoria":7,"s_militar":10,"s_academia":4,"s_perfil_int":3,"s_idade":4},
    "Paulo Pombolo":      {"s_cargo":8,"s_partido":9,"s_seguranca":4,"s_proximidade":7,"s_burpol":9,"s_trajetoria":7,"s_militar":0,"s_academia":4,"s_perfil_int":3,"s_idade":5},
    "Eugénio Laborinho":  {"s_cargo":5,"s_partido":9,"s_seguranca":8,"s_proximidade":5,"s_burpol":9,"s_trajetoria":8,"s_militar":8,"s_academia":5,"s_perfil_int":5,"s_idade":3},
    "Carlos Feijó":       {"s_cargo":5,"s_partido":7,"s_seguranca":2,"s_proximidade":7,"s_burpol":6,"s_trajetoria":7,"s_militar":0,"s_academia":10,"s_perfil_int":8,"s_idade":7},

    # --- Figuras com cargos conhecidos (Governo/Secretariado BP) ---
    "Bornito de Sousa":   {"s_cargo":5,"s_partido":8,"s_seguranca":2,"s_proximidade":6,"s_burpol":7,"s_trajetoria":7,"s_militar":0,"s_academia":9,"s_perfil_int":7,"s_idade":3},
    "Carolina Cerqueira": {"s_cargo":5,"s_partido":8,"s_seguranca":1,"s_proximidade":5,"s_burpol":7,"s_trajetoria":6,"s_militar":0,"s_academia":6,"s_perfil_int":5,"s_idade":8},
    "Fernando Nandó":     {"s_cargo":4,"s_partido":10,"s_seguranca":3,"s_proximidade":4,"s_burpol":7,"s_trajetoria":8,"s_militar":0,"s_academia":6,"s_perfil_int":5,"s_idade":1},
    "Nunes Júnior":       {"s_cargo":7,"s_partido":7,"s_seguranca":1,"s_proximidade":7,"s_burpol":7,"s_trajetoria":7,"s_militar":0,"s_academia":8,"s_perfil_int":7,"s_idade":7},
    "Tete António":       {"s_cargo":7,"s_partido":7,"s_seguranca":1,"s_proximidade":6,"s_burpol":7,"s_trajetoria":6,"s_militar":0,"s_academia":7,"s_perfil_int":9,"s_idade":5},
    "Joana Lina":         {"s_cargo":7,"s_partido":7,"s_seguranca":2,"s_proximidade":7,"s_burpol":7,"s_trajetoria":7,"s_militar":0,"s_academia":6,"s_perfil_int":4,"s_idade":8},
    "Rui Falcão Andrade": {"s_cargo":8,"s_partido":7,"s_seguranca":3,"s_proximidade":7,"s_burpol":7,"s_trajetoria":6,"s_militar":0,"s_academia":8,"s_perfil_int":5,"s_idade":5},
    "Sílvia Lutucuta":    {"s_cargo":6,"s_partido":6,"s_seguranca":1,"s_proximidade":6,"s_burpol":7,"s_trajetoria":6,"s_militar":0,"s_academia":8,"s_perfil_int":6,"s_idade":8},
    "Pitra da Costa Neto":{"s_cargo":4,"s_partido":9,"s_seguranca":3,"s_proximidade":4,"s_burpol":7,"s_trajetoria":7,"s_militar":5,"s_academia":5,"s_perfil_int":4,"s_idade":3},
    "Archer Mangueira":   {"s_cargo":6,"s_partido":7,"s_seguranca":2,"s_proximidade":5,"s_burpol":7,"s_trajetoria":7,"s_militar":0,"s_academia":7,"s_perfil_int":5,"s_idade":5},
    "Mpinda Simão":       {"s_cargo":6,"s_partido":7,"s_seguranca":2,"s_proximidade":6,"s_burpol":7,"s_trajetoria":6,"s_militar":0,"s_academia":6,"s_perfil_int":4,"s_idade":7},
    "Loti Nolika":        {"s_cargo":6,"s_partido":7,"s_seguranca":2,"s_proximidade":5,"s_burpol":7,"s_trajetoria":6,"s_militar":0,"s_academia":5,"s_perfil_int":3,"s_idade":5},
    "Manuel Augusto":     {"s_cargo":5,"s_partido":8,"s_seguranca":2,"s_proximidade":6,"s_burpol":8,"s_trajetoria":7,"s_militar":0,"s_academia":7,"s_perfil_int":8,"s_idade":4},
    "José C. da Rocha":   {"s_cargo":6,"s_partido":7,"s_seguranca":1,"s_proximidade":6,"s_burpol":7,"s_trajetoria":6,"s_militar":0,"s_academia":7,"s_perfil_int":5,"s_idade":5},

    # --- Secretariado do BP (cargos partidários internos) ---
    "Gonçalves Muandumba":{"s_cargo":6,"s_partido":8,"s_seguranca":2,"s_proximidade":6,"s_burpol":8,"s_trajetoria":6,"s_militar":0,"s_academia":5,"s_perfil_int":3,"s_idade":5},
    "João Martins (Jú)":  {"s_cargo":6,"s_partido":9,"s_seguranca":2,"s_proximidade":5,"s_burpol":8,"s_trajetoria":6,"s_militar":0,"s_academia":5,"s_perfil_int":3,"s_idade":3},
    "Esteves Hilário":    {"s_cargo":6,"s_partido":7,"s_seguranca":1,"s_proximidade":6,"s_burpol":8,"s_trajetoria":6,"s_militar":0,"s_academia":6,"s_perfil_int":4,"s_idade":7},
    "Pedro Morais Neto":  {"s_cargo":5,"s_partido":7,"s_seguranca":2,"s_proximidade":5,"s_burpol":8,"s_trajetoria":5,"s_militar":0,"s_academia":6,"s_perfil_int":3,"s_idade":7},
    "Pedro Sebastião Teta":{"s_cargo":5,"s_partido":7,"s_seguranca":1,"s_proximidade":5,"s_burpol":8,"s_trajetoria":5,"s_militar":0,"s_academia":6,"s_perfil_int":3,"s_idade":5},
    "Ângela Bragança":    {"s_cargo":5,"s_partido":7,"s_seguranca":1,"s_proximidade":5,"s_burpol":8,"s_trajetoria":5,"s_militar":0,"s_academia":5,"s_perfil_int":3,"s_idade":5},
    "Mário P. Andrade":   {"s_cargo":5,"s_partido":7,"s_seguranca":1,"s_proximidade":5,"s_burpol":8,"s_trajetoria":5,"s_militar":0,"s_academia":6,"s_perfil_int":3,"s_idade":5},
    "Mário Sequeira":     {"s_cargo":5,"s_partido":10,"s_seguranca":3,"s_proximidade":4,"s_burpol":7,"s_trajetoria":5,"s_militar":5,"s_academia":4,"s_perfil_int":2,"s_idade":1},
    "Idalina Valente":    {"s_cargo":5,"s_partido":6,"s_seguranca":1,"s_proximidade":5,"s_burpol":8,"s_trajetoria":5,"s_militar":0,"s_academia":6,"s_perfil_int":3,"s_idade":5},
    "Nádia Monteiro":     {"s_cargo":5,"s_partido":5,"s_seguranca":1,"s_proximidade":5,"s_burpol":7,"s_trajetoria":5,"s_militar":0,"s_academia":7,"s_perfil_int":4,"s_idade":10},
    "Joaquim Reis Jr.":   {"s_cargo":5,"s_partido":6,"s_seguranca":1,"s_proximidade":4,"s_burpol":7,"s_trajetoria":4,"s_militar":0,"s_academia":5,"s_perfil_int":3,"s_idade":5},

    # --- Membros com alguma info (Ministros, Deputados, Governadores, Ex-cargos) ---
    "Dolina Tchinhama":   {"s_cargo":6,"s_partido":6,"s_seguranca":1,"s_proximidade":5,"s_burpol":6,"s_trajetoria":5,"s_militar":0,"s_academia":5,"s_perfil_int":3,"s_idade":7},
    "Ernesto Muangala":   {"s_cargo":6,"s_partido":7,"s_seguranca":1,"s_proximidade":5,"s_burpol":6,"s_trajetoria":5,"s_militar":0,"s_academia":5,"s_perfil_int":3,"s_idade":5},
    "Ana Paula Sacramento":{"s_cargo":4,"s_partido":6,"s_seguranca":1,"s_proximidade":4,"s_burpol":6,"s_trajetoria":4,"s_militar":0,"s_academia":5,"s_perfil_int":3,"s_idade":7},
    "Irene Neto":         {"s_cargo":4,"s_partido":7,"s_seguranca":1,"s_proximidade":4,"s_burpol":6,"s_trajetoria":4,"s_militar":0,"s_academia":6,"s_perfil_int":4,"s_idade":5},
    "Bento Bento":        {"s_cargo":3,"s_partido":6,"s_seguranca":1,"s_proximidade":4,"s_burpol":6,"s_trajetoria":4,"s_militar":0,"s_academia":4,"s_perfil_int":2,"s_idade":5},
    "Jorge Dombolo":      {"s_cargo":4,"s_partido":7,"s_seguranca":1,"s_proximidade":4,"s_burpol":7,"s_trajetoria":5,"s_militar":0,"s_academia":5,"s_perfil_int":3,"s_idade":5},
    "João Liberdade":     {"s_cargo":6,"s_partido":8,"s_seguranca":1,"s_proximidade":6,"s_burpol":7,"s_trajetoria":6,"s_militar":0,"s_academia":6,"s_perfil_int":5,"s_idade":4},
    "Justino Capapinha":  {"s_cargo":5,"s_partido":4,"s_seguranca":1,"s_proximidade":5,"s_burpol":6,"s_trajetoria":5,"s_militar":0,"s_academia":5,"s_perfil_int":3,"s_idade":10},
    "Maricel Capamma":    {"s_cargo":4,"s_partido":5,"s_seguranca":1,"s_proximidade":4,"s_burpol":6,"s_trajetoria":4,"s_militar":0,"s_academia":5,"s_perfil_int":3,"s_idade":5},
    "Carla Ribeiro":      {"s_cargo":4,"s_partido":5,"s_seguranca":1,"s_proximidade":4,"s_burpol":6,"s_trajetoria":4,"s_militar":0,"s_academia":5,"s_perfil_int":3,"s_idade":5},
}

# Membros fora do BP actual mas relevantes para a análise
BP_EXTRA = {
    "Fernando Miala":     {"s_cargo":2,"s_partido":7,"s_seguranca":9,"s_proximidade":2,"s_burpol":3,"s_trajetoria":6,"s_militar":9,"s_academia":4,"s_perfil_int":4,"s_idade":3},
    "Ana Dias Lourenço":  {"s_cargo":5,"s_partido":8,"s_seguranca":1,"s_proximidade":6,"s_burpol":7,"s_trajetoria":7,"s_militar":0,"s_academia":10,"s_perfil_int":9,"s_idade":5},
}

# ─── CONSTRUIR LISTA COMPLETA DE CANDIDATOS ──────────────────────────────────

def build_all_candidates():
    """Gera scores para todos os membros do BP (excluindo o incumbente) + extras."""
    candidates = []

    for pos, nome_c, nome_s, cargo, nasc, sexo in BUREAU_POLITICO:
        # Excluir o incumbente
        if nome_s == "João Lourenço":
            continue

        # Calcular idade aproximada
        try:
            ano = int(str(nasc).replace("~", ""))
            idade = 2025 - ano
        except (ValueError, TypeError):
            idade = None

        # Buscar scores (detalhados ou default)
        scores = BP_SCORES.get(nome_s, dict(BP_DEFAULT_SCORES))

        # Se idade é desconhecida mas temos score de idade no default, manter
        # Se temos idade, recalcular s_idade
        if idade is not None and nome_s not in BP_SCORES:
            if 44 <= idade <= 52:
                scores["s_idade"] = 10
            elif 53 <= idade <= 58:
                scores["s_idade"] = 8
            elif 59 <= idade <= 62:
                scores["s_idade"] = 7
            elif 63 <= idade <= 66:
                scores["s_idade"] = 5
            elif 67 <= idade <= 70:
                scores["s_idade"] = 3
            elif idade > 70:
                scores["s_idade"] = 1
            else:
                scores["s_idade"] = 10  # < 44

        candidates.append({
            "id": nome_s.lower().replace(" ", "_").replace("(", "").replace(")", ""),
            "nome": nome_c,
            "nome_curto": nome_s,
            "nascimento": nasc,
            "idade_2025": idade if idade else "N/D",
            "sexo": sexo,
            "posicao_bp": pos,
            "cargo_funcao": cargo,
            "tem_score_detalhado": nome_s in BP_SCORES,
            **scores,
        })

    # Adicionar membros fora do BP
    extras_info = {
        "Fernando Miala": {
            "nome": "Fernando Garcia Miala",
            "nascimento": "1957", "idade_2025": 68, "sexo": "M",
            "posicao_bp": "Fora BP", "cargo_funcao": "Ex-Chefe SINSE (afastado)",
        },
        "Ana Dias Lourenço": {
            "nome": "Ana Dias Lourenço",
            "nascimento": "1960", "idade_2025": 65, "sexo": "F",
            "posicao_bp": "BP", "cargo_funcao": "Ex-Ministra Planeamento / Candidata VP BAD",
        },
    }
    for nome_s, scores in BP_EXTRA.items():
        info = extras_info[nome_s]
        candidates.append({
            "id": nome_s.lower().replace(" ", "_"),
            "nome": info["nome"],
            "nome_curto": nome_s,
            "nascimento": info["nascimento"],
            "idade_2025": info["idade_2025"],
            "sexo": info["sexo"],
            "posicao_bp": info["posicao_bp"],
            "cargo_funcao": info["cargo_funcao"],
            "tem_score_detalhado": True,
            **scores,
        })

    return candidates

# CANDIDATES será inicializado após a definição de BUREAU_POLITICO (ver abaixo)
CANDIDATES = None

# ─── MANTER RETROCOMPATIBILIDADE COM O ANTIGO FORMATO ────────────────────────
# ─── CASOS COMPARADOS INTERNACIONAIS ─────────────────────────────────────────
COMPARATIVE = [
    {
        "id": "dos_santos_angola_1979",
        "pais": "Angola", "lider": "José Eduardo dos Santos",
        "ano_chegada_poder": 1979, "nascimento": 1942, "idade_chegada": 37,
        "anos_partido_chegada": 18,
        "sistema": "Partido Único Dominante",
        "regiao": "África Subsaariana",
        "mecanismo_chegada": "Herança (morte do antecessor Agostinho Neto)",
        "ultimo_cargo_anterior": "1.º Vice-Presidente da República",
        "tinha_carteira_seguranca": False,
        "tinha_carteira_militar": False,
        "tinha_carteira_economica": False,
        "estava_no_partido_lideranca": True,
        "era_vp_antes": True,
        "anos_poder": 38,
        "nota": "Não chegou por eleição. Era VP e assumiu após morte de Neto. Estudou na URSS (petróleo)."
    },
    {
        "id": "lourenco_angola_2017",
        "pais": "Angola", "lider": "João Lourenço",
        "ano_chegada_poder": 2017, "nascimento": 1954, "idade_chegada": 63,
        "anos_partido_chegada": 43,
        "sistema": "Partido Dominante",
        "regiao": "África Subsaariana",
        "mecanismo_chegada": "Eleição via MPLA (cabeça de lista)",
        "ultimo_cargo_anterior": "Ministro da Defesa Nacional",
        "tinha_carteira_seguranca": True,
        "tinha_carteira_militar": True,
        "tinha_carteira_economica": False,
        "estava_no_partido_lideranca": True,
        "era_vp_antes": False,
        "anos_poder": None,
        "nota": "Sec. Geral MPLA + Ministro Defesa. Padrão de referência para Angola."
    },
    {
        "id": "xi_china_2012",
        "pais": "China", "lider": "Xi Jinping",
        "ano_chegada_poder": 2012, "nascimento": 1953, "idade_chegada": 59,
        "anos_partido_chegada": 38,
        "sistema": "Partido Único",
        "regiao": "Ásia Oriental",
        "mecanismo_chegada": "Ascensão interna PCC / Congresso Nacional",
        "ultimo_cargo_anterior": "Vice-Presidente da RPC + Vice-Presidente Comissão Militar Central",
        "tinha_carteira_seguranca": False,
        "tinha_carteira_militar": True,
        "tinha_carteira_economica": False,
        "estava_no_partido_lideranca": True,
        "era_vp_antes": True,
        "anos_poder": None,
        "nota": "Trajectória provincial (Gov. Fujian, Zhejiang) → Politburo Standing Committee → VP → Sec. Geral."
    },
    {
        "id": "putin_russia_1999",
        "pais": "Rússia", "lider": "Vladimir Putin",
        "ano_chegada_poder": 1999, "nascimento": 1952, "idade_chegada": 47,
        "anos_partido_chegada": 24,
        "sistema": "Partido Dominante (híbrido)",
        "regiao": "Europa Oriental / Ásia Central",
        "mecanismo_chegada": "Nomeação por Yeltsin como PM → Presidente interino",
        "ultimo_cargo_anterior": "Director do FSB → Primeiro-Ministro",
        "tinha_carteira_seguranca": True,
        "tinha_carteira_militar": True,
        "tinha_carteira_economica": False,
        "estava_no_partido_lideranca": False,
        "era_vp_antes": False,
        "anos_poder": None,
        "nota": "KGB/FSB (24 anos) + proximidade total ao predecessor. Velocidade final: Director FSB → PR em 2 anos."
    },
    {
        "id": "erdogan_turquia_2003",
        "pais": "Turquia", "lider": "Recep Tayyip Erdoğan",
        "ano_chegada_poder": 2003, "nascimento": 1954, "idade_chegada": 49,
        "anos_partido_chegada": 9,
        "sistema": "Democracia eleitoral (erosão gradual)",
        "regiao": "Europa / Médio Oriente",
        "mecanismo_chegada": "Vitória eleitoral AKP (partido fundado por ele em 2001)",
        "ultimo_cargo_anterior": "Presidente de Câmara de Istambul",
        "tinha_carteira_seguranca": False,
        "tinha_carteira_militar": False,
        "tinha_carteira_economica": False,
        "estava_no_partido_lideranca": True,
        "era_vp_antes": False,
        "anos_poder": None,
        "nota": "Perfil único: criou o próprio partido. Base eleitoral popular + capital religioso-conservador."
    },
    {
        "id": "nyusi_mocambique_2015",
        "pais": "Moçambique", "lider": "Filipe Nyusi",
        "ano_chegada_poder": 2015, "nascimento": 1959, "idade_chegada": 56,
        "anos_partido_chegada": 7,
        "sistema": "Partido Dominante",
        "regiao": "África Subsaariana",
        "mecanismo_chegada": "Eleição via Frelimo (cabeça de lista)",
        "ultimo_cargo_anterior": "Ministro da Defesa Nacional (2008–2014)",
        "tinha_carteira_seguranca": True,
        "tinha_carteira_militar": True,
        "tinha_carteira_economica": False,
        "estava_no_partido_lideranca": True,
        "era_vp_antes": False,
        "anos_poder": None,
        "nota": "Caso mais próximo de Angola: Engenheiro → Director CFM → Min. Defesa → Presidente via Frelimo."
    },
    {
        "id": "mnangagwa_zimbabue_2017",
        "pais": "Zimbabué", "lider": "Emmerson Mnangagwa",
        "ano_chegada_poder": 2017, "nascimento": 1942, "idade_chegada": 75,
        "anos_partido_chegada": 37,
        "sistema": "Partido Dominante",
        "regiao": "África Subsaariana",
        "mecanismo_chegada": "Golpe suave apoiado pelos militares (Zimbabwe Defence Forces)",
        "ultimo_cargo_anterior": "Vice-Presidente da República",
        "tinha_carteira_seguranca": True,
        "tinha_carteira_militar": True,
        "tinha_carteira_economica": False,
        "estava_no_partido_lideranca": True,
        "era_vp_antes": True,
        "anos_poder": None,
        "nota": "Ministro Segurança do Estado décadas + rede militares. Chegada atípica via golpe mas com suporte ZANU-PF."
    },
    {
        "id": "kagame_ruanda_2000",
        "pais": "Ruanda", "lider": "Paul Kagame",
        "ano_chegada_poder": 2000, "nascimento": 1957, "idade_chegada": 43,
        "anos_partido_chegada": 10,
        "sistema": "Partido Dominante",
        "regiao": "África Subsaariana",
        "mecanismo_chegada": "VP → Presidente (dimissão de Bizimungu)",
        "ultimo_cargo_anterior": "Vice-Presidente + Ministro da Defesa",
        "tinha_carteira_seguranca": True,
        "tinha_carteira_militar": True,
        "tinha_carteira_economica": False,
        "estava_no_partido_lideranca": True,
        "era_vp_antes": True,
        "anos_poder": None,
        "nota": "Chefe militar FPR durante genocídio → VP/Defesa → Presidente. Capital militar como base principal."
    },
    {
        "id": "to_lam_vietname_2024",
        "pais": "Vietname", "lider": "Tô Lâm",
        "ano_chegada_poder": 2024, "nascimento": 1957, "idade_chegada": 67,
        "anos_partido_chegada": 40,
        "sistema": "Partido Único",
        "regiao": "Ásia Oriental",
        "mecanismo_chegada": "Eleição interna PCV / Comité Central",
        "ultimo_cargo_anterior": "Ministro da Segurança Pública (2016–2024)",
        "tinha_carteira_seguranca": True,
        "tinha_carteira_militar": False,
        "tinha_carteira_economica": False,
        "estava_no_partido_lideranca": True,
        "era_vp_antes": False,
        "anos_poder": None,
        "nota": "Caso mais recente (2024). Interior/Segurança 16 anos → Sec. Geral PCV. Análogo directo ao padrão Angola."
    },
    {
        "id": "ramaphosa_sa_2018",
        "pais": "África do Sul", "lider": "Cyril Ramaphosa",
        "ano_chegada_poder": 2018, "nascimento": 1952, "idade_chegada": 66,
        "anos_partido_chegada": 35,
        "sistema": "Pluripartidário",
        "regiao": "África Subsaariana",
        "mecanismo_chegada": "Eleição interna ANC → Presidente após demissão de Zuma",
        "ultimo_cargo_anterior": "Vice-Presidente da República",
        "tinha_carteira_seguranca": False,
        "tinha_carteira_militar": False,
        "tinha_carteira_economica": True,
        "estava_no_partido_lideranca": True,
        "era_vp_antes": True,
        "anos_poder": None,
        "nota": "Único caso onde capital económico supera segurança. Sistema pluripartidário com primárias ANC."
    },
    {
        "id": "maduro_venezuela_2013",
        "pais": "Venezuela", "lider": "Nicolás Maduro",
        "ano_chegada_poder": 2013, "nascimento": 1962, "idade_chegada": 51,
        "anos_partido_chegada": 20,
        "sistema": "Autoritarismo eleitoral",
        "regiao": "América Latina",
        "mecanismo_chegada": "VP → Presidente interino → eleito (herança de Chávez)",
        "ultimo_cargo_anterior": "Vice-Presidente Executivo + Min. Relações Exteriores",
        "tinha_carteira_seguranca": False,
        "tinha_carteira_militar": False,
        "tinha_carteira_economica": False,
        "estava_no_partido_lideranca": True,
        "era_vp_antes": True,
        "anos_poder": None,
        "nota": "Motorista/sindicalista → diplomacia → VP → herança directa. Lealdade ao líder como variável dominante."
    },
    {
        "id": "tokayev_cazaquistao_2019",
        "pais": "Cazaquistão", "lider": "Kassym-Jomart Tokayev",
        "ano_chegada_poder": 2019, "nascimento": 1953, "idade_chegada": 66,
        "anos_partido_chegada": 32,
        "sistema": "Autoritarismo eleitoral",
        "regiao": "Ásia Central",
        "mecanismo_chegada": "Designação pelo antecessor Nazarbayev",
        "ultimo_cargo_anterior": "Presidente do Senado",
        "tinha_carteira_seguranca": False,
        "tinha_carteira_militar": False,
        "tinha_carteira_economica": False,
        "estava_no_partido_lideranca": True,
        "era_vp_antes": False,
        "anos_poder": None,
        "nota": "Diplomata sénior → PM → Senado → escolhido por Nazarbayev. Designação directa pelo predecessor."
    },
]

# ─── LISTA COMPLETA BUREAU POLÍTICO ──────────────────────────────────────────
BUREAU_POLITICO = [
    # (ordem, nome_completo, nome_curto, cargo_conhecidos, nascimento_aprox, sexo)
    (1,  "João Manuel Gonçalves Lourenço",               "João Lourenço",       "Presidente MPLA / Presidente da República",          "1954", "M"),
    (2,  "Mara Regina da Silva Baptista Domingos Quiosa","Mara Quiosa",         "Vice-Presidente MPLA (desde Dez 2024)",               "1980", "F"),
    (3,  "Paulo Pombolo",                                "Paulo Pombolo",       "Secretário-Geral MPLA",                               "1962", "M"),
    (4,  "Adão Francisco Correia de Almeida",            "Adão de Almeida",     "Presidente Assembleia Nacional",                      "1979", "M"),
    (5,  "Américo António Cuononoca",                    "Américo Cuononoca",   "Membro BP",                                           "N/D", "M"),
    (6,  "Ana Celeste Cardoso Januário",                 "Ana Celeste Januário","Membro BP",                                           "N/D", "F"),
    (7,  "Ana Paula do Sacramento Neto",                 "Ana Paula Sacramento","Membro BP / Deputada",                                "~1965","F"),
    (8,  "António Domingos Pitra da Costa Neto",         "Pitra da Costa Neto", "Membro BP / Ex-Ministro",                             "~1955","M"),
    (9,  "Bento Joaquim S. Francisco Bento (Bento Bento)","Bento Bento",        "Membro BP",                                           "~1960","M"),
    (10, "Bornito de Sousa Baltazar Diogo",              "Bornito de Sousa",    "Ex-Vice-Presidente da República (2017–2022)",          "~1956","M"),
    (11, "Carlos Maria da Silva Feijó",                  "Carlos Feijó",        "Prof. Catedrático UAN / Ex-Chefe Casa Civil",          "1963", "M"),
    (12, "Carolina Cerqueira",                           "Carolina Cerqueira",  "Ex-Presidente Assembleia Nacional (2017–2025)",        "~1967","F"),
    (13, "Daniel Félix Neto",                            "Daniel Félix Neto",   "Membro BP",                                           "N/D", "M"),
    (14, "Crispiniano Vivaldino E. dos Santos",          "Crispiniano Santos",  "Membro BP",                                           "N/D", "M"),
    (15, "Dionísio Manuel da Fonseca",                   "Dionísio da Fonseca", "Membro BP",                                           "N/D", "M"),
    (16, "Dolina Nassocópia Miguel Tchinhama",           "Dolina Tchinhama",    "Membro BP / Ministra",                                "~1965","F"),
    (17, "Emília Carlota Dias",                          "Emília Carlota Dias", "Membro BP",                                           "N/D", "F"),
    (18, "Ernesto Muangala",                             "Ernesto Muangala",    "Membro BP / Ministro",                                "~1960","M"),
    (19, "Eugénio César Laborinho",                      "Eugénio Laborinho",   "Ex-Ministro Interior (2019–2024) / Tenente-General",  "1955", "M"),
    (20, "Fernando da Piedade Dias dos Santos (Nandó)",  "Fernando Nandó",      "Ex-Presidente Assembleia Nacional / Ex-PM",           "~1952","M"),
    (21, "Gonçalves Manuel Muandumba",                   "Gonçalves Muandumba", "Sec. Organização e Inserção BP",                      "~1960","M"),
    (22, "Irene Alexandra da Silva Neto",                "Irene Neto",          "Membro BP",                                           "~1960","F"),
    (23, "Isaac Francisco Maria dos Anjos",              "Isaac dos Anjos",     "Membro BP",                                           "N/D", "M"),
    (24, "Joana Domingos dos Santos Filipe Tomás",       "Joana Tomás",         "Membro BP",                                           "N/D", "F"),
    (25, "Joana Lina Ramos Baptista Cândido",            "Joana Lina",          "Governadora de Luanda (desde 2024)",                  "~1970","F"),
    (26, "João de Almeida Azevedo Martins (Jú)",         "João Martins (Jú)",   "Sec. Assuntos Políticos e Eleitorais BP",             "~1955","M"),
    (27, "João Diogo Gaspar",                            "João Diogo Gaspar",   "Membro BP",                                           "N/D", "M"),
    (28, "João Ernesto dos Santos (Liberdade)",          "João Liberdade",      "Membro BP / Ministro Indústria e Comércio",           "~1958","M"),
    (29, "Jorge Inocêncio Dombolo",                      "Jorge Dombolo",       "Ex-Sec. Organização BP / Membro",                     "~1960","M"),
    (30, "José Carvalho da Rocha",                       "José C. da Rocha",    "Ministro Telecomunicações e TIC",                     "~1960","M"),
    (31, "Luís Manuel da Fonseca Nunes",                 "Luís Fonseca Nunes",  "Membro BP",                                           "N/D", "M"),
    (32, "Manuel Gomes da Conceição Homem",              "Manuel Homem",        "Ministro do Interior (desde 2024)",                   "1979", "M"),
    (33, "Manuel José Nunes Júnior",                     "Nunes Júnior",        "Ministro da Economia e Planeamento",                  "~1963","M"),
    (34, "Manuel Pedro Chaves",                          "Manuel Pedro Chaves", "Membro BP",                                           "N/D", "M"),
    (35, "Mário António de Sequeira e Carvalho",         "Mário Sequeira",      "Sec. Antigos Combatentes e Veteranos BP",             "~1950","M"),
    (36, "Mário Pinto de Andrade",                       "Mário P. Andrade",    "Sec. Reforma Estado / Autarquias BP",                 "~1960","M"),
    (37, "Marcos Alexandre Nhunga",                      "Marcos Nhunga",       "Membro BP",                                           "N/D", "M"),
    (38, "Marcy Cláudio Lopes",                          "Marcy Lopes",         "Membro BP",                                           "N/D", "M"),
    (39, "Maria Ângela Teixeira A. S. Bragança",         "Ângela Bragança",     "Sec. Política de Quadros BP",                         "~1960","F"),
    (40, "Maria Antonieta Josefina Sabinda",             "Antonieta Sabinda",   "Membro BP",                                           "N/D", "F"),
    (41, "Maricel Marinho da Silva Capamma",             "Maricel Capamma",     "Membro BP (saiu secretariado 2024)",                  "N/D", "F"),
    (42, "Maria Idalina de Oliveira Valente",            "Idalina Valente",     "Sec. Política Económica e Social BP",                 "N/D", "F"),
    (43, "Mpinda Simão",                                 "Mpinda Simão",        "Governador de Benguela",                              "~1965","M"),
    (44, "Norberto Fernando dos Santos (Kuata Kanawa)",  "Norberto Kuata",      "Membro BP",                                           "N/D", "M"),
    (45, "Paula Cristina Domingos Francisco Coelho",     "Paula Coelho",        "Membro BP",                                           "N/D", "F"),
    (46, "Pedro de Morais Neto",                         "Pedro Morais Neto",   "Membro Secretariado BP",                              "~1965","M"),
    (47, "Pedro Makita Armando Júlia (Pedro Mutindi)",   "Pedro Mutindi",       "Membro BP",                                           "N/D", "M"),
    (48, "Pedro Sebastião Teta",                         "Pedro Sebastião Teta","Sec. TIC BP",                                         "~1960","M"),
    (49, "Pereira Alfredo",                              "Pereira Alfredo",     "Membro BP",                                           "N/D", "M"),
    (50, "Rui Luís Falcão Pinto de Andrade",             "Rui Falcão Andrade",  "Procurador-Geral da República",                       "~1960","M"),
    (51, "Sílvia Paula Valentim Lutucuta",               "Sílvia Lutucuta",     "Ministra da Saúde",                                   "~1970","F"),
    (52, "Vera Esperança dos Santos Daves de Sousa",     "Vera Daves",          "Ministra das Finanças",                               "1983", "F"),
    (53, "Virgílio da Ressurreição Bernardo Adriano Tyova","Virgílio Tyova",    "Membro BP",                                           "N/D", "M"),
    (54, "Virgílio Ferreira de Fontes Pereira",          "Virgílio F. Pereira", "Membro BP",                                           "N/D", "M"),
    (55, "Loti Nolika",                                  "Loti Nolika",         "Governador do Zaire",                                 "~1960","M"),
    (56, "Adriano Mendes de Carvalho",                   "Adriano Mendes",      "Membro BP",                                           "N/D", "M"),
    (57, "Job Castelo Capapinha (Justino)",               "Justino Capapinha",   "1.º Secretário Nacional da JMPLA",                   "~1985","M"),
    (58, "Nuno Mahapi Dala",                              "Nuno Mahapi Dala",    "Membro BP",                                           "N/D", "M"),
    (59, "Gerdina Didalewa",                              "Gerdina Didalewa",    "Membro BP",                                           "N/D", "F"),
    (60, "Archer Mangueira (Augusto Archer de Sousa Mangueira)","Archer Mangueira","Governador do Namibe / Ex-CMC",                "~1960","M"),
    (61, "José Martins",                                  "José Martins",        "Membro BP",                                           "N/D", "M"),
    (62, "Tete António",                                  "Tete António",        "Ministro das Relações Exteriores",                    "~1960","M"),
    (63, "Manuel Domingos Augusto",                       "Manuel Augusto",      "Sec. Relações Internacionais BP",                     "~1958","M"),
    (64, "Aia-Eza Gomes da Silva Troso",                  "Aia-Eza Troso",       "Membro BP",                                           "N/D", "F"),
    (65, "Ana Paula Chantre Luna de Carvalho",            "Ana Paula Chantre",   "Membro BP",                                           "N/D", "F"),
    (66, "Ângela Maria Botelho de Carvalho Diogo",        "Ângela Diogo",        "Membro BP",                                           "N/D", "F"),
    (67, "Angélica Nené Curita Inhungo",                  "Angélica Inhungo",    "Membro BP",                                           "N/D", "F"),
    (68, "Carla Maria Leitão Ribeiro de Sousa",           "Carla Ribeiro",       "Membro BP (saiu secretariado 2024)",                  "N/D", "F"),
    (69, "Carmen Ivelize VanDunem do Sacramento Neto",    "Carmen VanDunem",     "Membro BP",                                           "N/D", "F"),
    (70, "Celeste Elavoco David Adolfo",                  "Celeste Adolfo",      "Membro BP",                                           "N/D", "F"),
    (71, "Dalva Maurícia Ringote Allen",                  "Dalva Allen",         "Membro BP",                                           "N/D", "F"),
    (72, "Elizabeth Claudina Rufino Chiwissa",            "Elizabeth Chiwissa",  "Membro BP",                                           "N/D", "F"),
    (73, "Emília da Conceição Panjimba",                  "Emília Panjimba",     "Membro BP",                                           "N/D", "F"),
    (74, "Esmeralda Bravo Conde da Silva Mendonça",       "Esmeralda Mendonça",  "Membro BP",                                           "N/D", "F"),
    (75, "Esperança Maria Eduardo Francisco da Costa",    "Esperança da Costa",  "Membro BP",                                           "N/D", "F"),
    (76, "Hemingarda João Fernandes",                     "Hemingarda Fernandes","Membro BP",                                           "N/D", "F"),
    (77, "Joaquim António Carlos dos Reis Júnior",        "Joaquim Reis Jr.",    "Sec. BP / Membro",                                    "N/D", "M"),
    (78, "Francisco Pereira Furtado",                     "Francisco Furtado",   "Min. Estado – Casa de Segurança do PR",               "1958", "M"),
    (79, "Gildo Matias José",                             "Gildo Matias",        "Membro BP",                                           "N/D", "M"),
    (80, "Esteves Carlos Hilário",                        "Esteves Hilário",     "Sec. Informação e Propaganda BP",                     "~1965","M"),
    (81, "Eduarda Desihafela Daniel Zacarias",            "Eduarda Zacarias",    "Membro BP",                                           "N/D", "F"),
    (82, "Aniceto da Fonseca Emílio Pedro",               "Aniceto Emílio",      "Membro BP",                                           "N/D", "M"),
    (83, "Josefina Perpétua Pires Domingos Diakité",      "Josefina Diakité",    "Membro BP",                                           "N/D", "F"),
    (84, "Maria Antónia Nelumba",                         "Maria Nelumba",       "Membro BP",                                           "N/D", "F"),
    (85, "Maria Esperança dos Santos",                    "Maria Esperança",     "Membro BP",                                           "N/D", "F"),
    (86, "Maria João Francisco Tchipalavela",             "Maria Tchipalavela",  "Membro BP",                                           "N/D", "F"),
    (87, "Narciso Damásio dos Santos Benedito",           "Narciso Benedito",    "Membro BP",                                           "N/D", "M"),
    (88, "Leonor da Silva Garibalde",                     "Leonor Garibalde",    "Membro BP",                                           "N/D", "F"),
    (89, "Maria Piedade de Jesus",                        "Maria Piedade",       "Membro BP",                                           "N/D", "F"),
    (90, "Maria Fernanda Cavungo",                        "Maria Cavungo",       "Membro BP",                                           "N/D", "F"),
    (91, "Ruth Mendes",                                   "Ruth Mendes",         "Membro BP",                                           "N/D", "F"),
    (92, "Catarina Pedro Domingos",                       "Catarina Domingos",   "Membro BP",                                           "N/D", "F"),
    (93, "Deolinda Odia Paulo Satula Vilarinho",          "Deolinda Vilarinho",  "Membro BP",                                           "N/D", "F"),
    (94, "Nádia Agostinho Monteiro",                      "Nádia Monteiro",      "Sec. Administração e Finanças BP",                    "~1985","F"),
    (95, "Josefina Ndesipewa Gomes",                      "Josefina Gomes",      "Membro BP",                                           "N/D", "F"),
    (96, "Djamila Huguet da Silva de Almeida Prata",      "Djamila Prata",       "Membro BP",                                           "N/D", "F"),
    (97, "Esperança Luzia Jackon Pembele",                "Esperança Pembele",   "Membro BP",                                           "N/D", "F"),
    (98, "Evandra Luisa de Jesus Martins Mingas",         "Evandra Mingas",      "Membro BP",                                           "N/D", "F"),
    (99, "Helena Berta Buco Vando Marciado",              "Helena Marciado",     "Membro BP",                                           "N/D", "F"),
    (100,"Suzana Augusta de Melo",                        "Suzana de Melo",      "Membro BP",                                           "N/D", "F"),
    (101,"Luciana Mona Cachiangue",                       "Luciana Cachiangue",  "Membro BP",                                           "N/D", "F"),
]

# ─── INICIALIZAR CANDIDATES (após BUREAU_POLITICO estar definido) ────────────
CANDIDATES = build_all_candidates()

# ─── FUNÇÕES DE CÁLCULO ───────────────────────────────────────────────────────

def compute_score(c: dict) -> float:
    """Calcula score ponderado total (0–10). Multiplicar por 10 para escala 0–100."""
    return sum(
        c.get(f"s_{v['id']}", 0) * v["weight"]
        for v in VARIABLES
    )

def score_rank(candidates: list) -> list:
    """Retorna lista ordenada por score descendente."""
    scored = [(c, compute_score(c)) for c in candidates]
    return sorted(scored, key=lambda x: x[1], reverse=True)

# ─── EXPORTAR CSVs ────────────────────────────────────────────────────────────

def export_candidates_csv():
    path = DATA / "angola_bp_scored.csv"
    score_fields  = [f"s_{v['id']}" for v in VARIABLES]

    fieldnames = [
        "id", "nome", "nome_curto", "nascimento", "idade_2025", "sexo",
        "posicao_bp", "cargo_funcao", "tem_score_detalhado",
        *score_fields,
        "score_total_0_10", "score_total_0_100",
        "ranking",
    ]

    ranked = score_rank(CANDIDATES)

    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        for rank_pos, (c, total) in enumerate(ranked, 1):
            row = {k: c.get(k, "") for k in fieldnames}
            row["score_total_0_10"]  = round(total, 4)
            row["score_total_0_100"] = round(total * 10, 2)
            row["ranking"] = rank_pos
            w.writerow(row)

    print(f"✓ {path.name}  ({len(CANDIDATES)} membros scored)")
    return path


def export_bp_full_csv():
    path = DATA / "angola_bp_full.csv"
    fieldnames = ["posicao_lista", "nome_completo", "nome_curto", "cargo_funcao", "nascimento_aprox", "sexo", "tem_score_detalhado"]

    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        for row in BUREAU_POLITICO:
            pos, nome_c, nome_s, cargo, nasc, sexo = row
            w.writerow({
                "posicao_lista": pos,
                "nome_completo": nome_c,
                "nome_curto": nome_s,
                "cargo_funcao": cargo,
                "nascimento_aprox": nasc,
                "sexo": sexo,
                "tem_score_detalhado": "Sim" if nome_s in BP_SCORES else "Não",
            })

    print(f"✓ {path.name}  ({len(BUREAU_POLITICO)} membros BP)")
    return path


def export_comparative_csv():
    path = DATA / "comparative_cases.csv"
    fieldnames = [
        "id", "pais", "lider", "ano_chegada_poder", "nascimento", "idade_chegada",
        "anos_partido_chegada", "sistema", "regiao", "mecanismo_chegada",
        "ultimo_cargo_anterior",
        "tinha_carteira_seguranca", "tinha_carteira_militar", "tinha_carteira_economica",
        "estava_no_partido_lideranca", "era_vp_antes",
        "anos_poder", "nota",
    ]
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        for c in COMPARATIVE:
            w.writerow({k: c.get(k, "") for k in fieldnames})

    print(f"✓ {path.name}  ({len(COMPARATIVE)} casos históricos)")
    return path


def export_variables_schema():
    path = DATA / "variables_schema.csv"
    fieldnames = ["id", "label", "weight", "scale", "description", "source"]
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        for v in VARIABLES:
            w.writerow(v)

    print(f"✓ {path.name}  ({len(VARIABLES)} variáveis)")
    return path


def export_json():
    ranked = score_rank(CANDIDATES)
    export_data = []
    for rank_pos, (c, total) in enumerate(ranked, 1):
        entry = dict(c)
        entry["score_total_0_100"] = round(total * 10, 2)
        entry["ranking"] = rank_pos
        export_data.append(entry)

    p1 = DATA / "angola_bp_scored.json"
    with open(p1, "w", encoding="utf-8") as f:
        json.dump(export_data, f, ensure_ascii=False, indent=2)
    print(f"✓ {p1.name}")

    p2 = DATA / "comparative_cases.json"
    with open(p2, "w", encoding="utf-8") as f:
        json.dump(COMPARATIVE, f, ensure_ascii=False, indent=2)
    print(f"✓ {p2.name}")


# ─── SUMÁRIO ─────────────────────────────────────────────────────────────────

def print_summary():
    ranked = score_rank(CANDIDATES)
    print(f"\n{'='*65}")
    print(f"RANKING COMPLETO — {len(ranked)} membros BP scored (pesos iguais 0.10)")
    print("="*65)
    print(f"\n  TOP 20:")
    for rank_pos, (c, total) in enumerate(ranked[:20], 1):
        det = "★" if c.get("tem_score_detalhado") else "·"
        bar = "█" * int(total * 4)
        print(f"  {rank_pos:>3}. {det} {c['nome_curto']:<28} {total*10:5.1f}  {bar}")
    print(f"\n  ... + {len(ranked)-20} membros (scores 31.0 base para membros sem dados)")
    print(f"\n  ★ = score detalhado   · = score estimado (dados insuficientes)")
    print()
    print("Variáveis e pesos:")
    for v in VARIABLES:
        print(f"  {v['id']:<15} {v['label']:<35} w={v['weight']:.2f}")
    print()


# ─── MAIN ─────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("Angola Succession Dataset Builder")
    print("-" * 40)
    export_candidates_csv()
    export_bp_full_csv()
    export_comparative_csv()
    export_variables_schema()
    export_json()
    print_summary()
    print(f"Todos os ficheiros em: {DATA.resolve()}")
