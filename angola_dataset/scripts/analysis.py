"""
angola_analysis.py
==================
Análise exploratória + modelos preditivos sobre o dataset
de sucessão presidencial em Angola.

Requer: pandas, numpy, matplotlib, scikit-learn
Instalar: pip install pandas numpy matplotlib scikit-learn

Secções:
  1. Carregar dados
  2. Análise exploratória (EDA)
  3. Matriz de correlação das variáveis
  4. Ranking com pesos ajustáveis
  5. Modelo de referência: Random Forest sobre casos comparados
  6. SHAP values para interpretabilidade
  7. Cenários hipotéticos (what-if)
  8. Exportar gráficos
"""

import sys
import os
import json
import csv
from pathlib import Path

# ─── PATHS ─────────────────────────────────────────────────────────────────
BASE   = Path(__file__).parent.parent
DATA   = BASE / "data"
FIGS   = BASE / "figures"
FIGS.mkdir(exist_ok=True)

# ─── TENTAR IMPORTAR DEPENDÊNCIAS ─────────────────────────────────────────
try:
    import pandas as pd
    import numpy as np
    import matplotlib.pyplot as plt
    import matplotlib.patches as mpatches
    from matplotlib.colors import LinearSegmentedColormap
    HAS_DEPS = True
except ImportError:
    HAS_DEPS = False
    print("⚠  pandas / matplotlib não encontrados.")
    print("   Executar: pip install pandas numpy matplotlib scikit-learn")

# ─── 1. CARREGAR DADOS ─────────────────────────────────────────────────────

def load_candidates() -> "pd.DataFrame":
    return pd.read_csv(DATA / "angola_bp_scored.csv")

def load_comparative() -> "pd.DataFrame":
    return pd.read_csv(DATA / "comparative_cases.csv")

def load_variables() -> "pd.DataFrame":
    return pd.read_csv(DATA / "variables_schema.csv")

SCORE_COLS = [
    "s_cargo", "s_partido", "s_seguranca", "s_proximidade",
    "s_burpol", "s_trajetoria", "s_militar", "s_academia",
    "s_perfil_int", "s_idade",
]
VAR_LABELS = {
    "s_cargo":       "Cargo",
    "s_partido":     "Partido",
    "s_seguranca":   "Segurança",
    "s_proximidade": "Proximidade",
    "s_burpol":      "Bureau Pol.",
    "s_trajetoria":  "Trajectória",
    "s_militar":     "Militar",
    "s_academia":    "Academia",
    "s_perfil_int":  "Perf. Intl.",
    "s_idade":       "Idade",
}
WEIGHTS = {
    "s_cargo": 0.10, "s_partido": 0.10, "s_seguranca": 0.10,
    "s_proximidade": 0.10, "s_burpol": 0.10, "s_trajetoria": 0.10,
    "s_militar": 0.10, "s_academia": 0.10, "s_perfil_int": 0.10,
    "s_idade": 0.10,
}
CANDIDATE_COLORS = {
    "Mara Quiosa":              "#F472B6",
    "Adão de Almeida":          "#E8A020",
    "Manuel Homem":             "#22C55E",
    "Vera Daves":               "#60A5FA",
    "Francisco Furtado":        "#A78BFA",
    "Paulo Pombolo":            "#2DD4BF",
    "Eugénio Laborinho":        "#EF4444",
    "Carlos Feijó":             "#FB923C",
    "Ana Dias Lourenço":        "#818CF8",
    "Fernando Miala":           "#94A3B8",
    "Bornito de Sousa":         "#FBBF24",
    "Nunes Júnior":             "#34D399",
    "Tete António":             "#F87171",
    "Joana Lina":               "#C084FC",
    "Rui Falcão Andrade":       "#38BDF8",
    "Carolina Cerqueira":       "#FB7185",
    "Sílvia Lutucuta":          "#A3E635",
    "Manuel Augusto":           "#FDBA74",
    "Fernando Nandó":           "#6EE7B7",
    "João Liberdade":           "#7DD3FC",
}
# Limite de candidatos para gráficos detalhados (radar, heatmap)
TOP_N_CHARTS = 15

# ─── 2. EDA — HEATMAP DE SCORES ────────────────────────────────────────────

def plot_heatmap(df: "pd.DataFrame"):
    fig, ax = plt.subplots(figsize=(13, 5))
    fig.patch.set_facecolor("#06090f")
    ax.set_facecolor("#06090f")

    mat = df.set_index("nome_curto")[SCORE_COLS].values.astype(float)
    names = df.sort_values("ranking")["nome_curto"].tolist()
    mat = df.sort_values("ranking").set_index("nome_curto")[SCORE_COLS].values.astype(float)

    cmap = LinearSegmentedColormap.from_list("custom", ["#0c1219", "#1a3a5c", "#E8A020"])
    im = ax.imshow(mat, aspect="auto", cmap=cmap, vmin=0, vmax=10)

    ax.set_xticks(range(len(SCORE_COLS)))
    ax.set_xticklabels([VAR_LABELS[c] for c in SCORE_COLS],
                       rotation=35, ha="right", color="#CBD5E1", fontsize=9)
    ax.set_yticks(range(len(names)))
    ax.set_yticklabels(names, color="#CBD5E1", fontsize=9)

    for i in range(mat.shape[0]):
        for j in range(mat.shape[1]):
            ax.text(j, i, f"{int(mat[i,j])}", ha="center", va="center",
                    color="white" if mat[i,j] > 5 else "#64748b", fontsize=8, fontweight="bold")

    cb = fig.colorbar(im, ax=ax, fraction=0.02, pad=0.04)
    cb.ax.tick_params(colors="#CBD5E1")
    cb.outline.set_edgecolor("#1a2536")

    ax.set_title("Heatmap de Scores — Candidatos Angola", color=C_GOLD, fontsize=13, pad=12)
    for spine in ax.spines.values():
        spine.set_edgecolor("#1a2536")
    ax.tick_params(colors="#1a2536")

    plt.tight_layout()
    out = FIGS / "heatmap_scores.png"
    plt.savefig(out, dpi=150, facecolor="#06090f")
    plt.close()
    print(f"  ✓ {out.name}")


# ─── 3. RADAR / SPIDER CHART ───────────────────────────────────────────────

def plot_radars(df: "pd.DataFrame"):
    names = df["nome_curto"].tolist()
    n_vars = len(SCORE_COLS)
    angles = np.linspace(0, 2 * np.pi, n_vars, endpoint=False).tolist()
    angles += angles[:1]

    n_cols = 4
    n_rows = (len(names) + n_cols - 1) // n_cols
    fig, axes = plt.subplots(n_rows, n_cols,
                             subplot_kw=dict(polar=True),
                             figsize=(14, n_rows * 3.5))
    fig.patch.set_facecolor("#06090f")

    for idx, row in df.iterrows():
        ax = axes[idx // n_cols][idx % n_cols] if n_rows > 1 else axes[idx % n_cols]
        vals = [row[c] for c in SCORE_COLS] + [row[SCORE_COLS[0]]]
        color = CANDIDATE_COLORS.get(row["nome_curto"], "#E8A020")

        ax.set_facecolor("#0c1219")
        ax.plot(angles, vals, color=color, linewidth=1.8)
        ax.fill(angles, vals, alpha=0.25, color=color)
        ax.set_xticks(angles[:-1])
        ax.set_xticklabels([VAR_LABELS[c] for c in SCORE_COLS],
                           color="#94a3b8", fontsize=7)
        ax.set_ylim(0, 10)
        ax.set_yticks([2, 4, 6, 8, 10])
        ax.set_yticklabels(["2","4","6","8","10"], color="#475569", fontsize=6)
        ax.grid(color="#1a2536", linewidth=0.8)
        ax.spines["polar"].set_color("#1a2536")
        ax.set_title(f"#{row['ranking']} {row['nome_curto']}\n{row['score_total_0_100']:.1f}/100",
                     color=color, fontsize=9, pad=10)

    # esconder eixos vazios
    for i in range(len(names), n_rows * n_cols):
        ax = axes[i // n_cols][i % n_cols] if n_rows > 1 else axes[i % n_cols]
        ax.set_visible(False)

    fig.suptitle("Radar de Competências — Bureau Político MPLA Angola",
                 color=C_GOLD, fontsize=13, y=1.01)
    plt.tight_layout()
    out = FIGS / "radar_candidatos.png"
    plt.savefig(out, dpi=150, facecolor="#06090f", bbox_inches="tight")
    plt.close()
    print(f"  ✓ {out.name}")


# ─── 4. RANKING COM BARRAS ─────────────────────────────────────────────────

def plot_ranking_bars(df: "pd.DataFrame"):
    df_s = df.sort_values("score_total_0_100")
    fig, ax = plt.subplots(figsize=(10, 6))
    fig.patch.set_facecolor("#06090f")
    ax.set_facecolor("#06090f")

    colors = [CANDIDATE_COLORS.get(n, "#E8A020") for n in df_s["nome_curto"]]
    bars = ax.barh(df_s["nome_curto"], df_s["score_total_0_100"], color=colors,
                   height=0.6, alpha=0.85)
    for bar, val in zip(bars, df_s["score_total_0_100"]):
        ax.text(bar.get_width() + 0.5, bar.get_y() + bar.get_height() / 2,
                f"{val:.1f}", va="center", color="#CBD5E1", fontsize=10, fontweight="bold")

    ax.set_xlim(0, 105)
    ax.set_xlabel("Score Ponderado (0–100)", color="#CBD5E1", fontsize=10)
    ax.set_title("Ranking de Sucessão Presidencial — Angola 2025",
                 color=C_GOLD, fontsize=12, pad=12)
    ax.tick_params(colors="#CBD5E1")
    ax.axvline(50, color="#1a2536", linewidth=1, linestyle="--")
    for spine in ax.spines.values():
        spine.set_edgecolor("#1a2536")
    ax.set_facecolor("#06090f")
    plt.tight_layout()
    out = FIGS / "ranking_bars.png"
    plt.savefig(out, dpi=150, facecolor="#06090f")
    plt.close()
    print(f"  ✓ {out.name}")


# ─── 5. FREQUÊNCIA DE VARIÁVEIS NOS CASOS COMPARADOS ──────────────────────

def plot_var_frequency(df_comp: "pd.DataFrame"):
    bool_cols = [
        "tinha_carteira_seguranca",
        "tinha_carteira_militar",
        "tinha_carteira_economica",
        "estava_no_partido_lideranca",
        "era_vp_antes",
    ]
    labels = {
        "tinha_carteira_seguranca":     "Carteira Segurança/Interior",
        "tinha_carteira_militar":       "Capital Militar",
        "tinha_carteira_economica":     "Carteira Económica",
        "estava_no_partido_lideranca":  "Liderança do Partido",
        "era_vp_antes":                 "Era VP antes de chegar ao poder",
    }
    counts = {labels[c]: df_comp[c].sum() for c in bool_cols}
    total = len(df_comp)

    fig, ax = plt.subplots(figsize=(9, 4))
    fig.patch.set_facecolor("#06090f")
    ax.set_facecolor("#06090f")

    items = sorted(counts.items(), key=lambda x: x[1])
    lbs, vals = zip(*items)
    colors_bar = ["#EF4444","#E8A020","#60A5FA","#22C55E","#A78BFA"]
    bars = ax.barh(lbs, vals, color=colors_bar[:len(vals)], height=0.55)
    for bar, v in zip(bars, vals):
        ax.text(bar.get_width() + 0.1, bar.get_y() + bar.get_height()/2,
                f"{v}/{total}  ({v/total*100:.0f}%)",
                va="center", color="#CBD5E1", fontsize=9)
    ax.set_xlim(0, total + 2)
    ax.set_xlabel("Nº de casos (de 12 históricos)", color="#CBD5E1")
    ax.set_title("Frequência de Variáveis Preditivas nos 12 Casos Comparados",
                 color=C_GOLD, fontsize=12, pad=10)
    ax.tick_params(colors="#CBD5E1")
    for spine in ax.spines.values():
        spine.set_edgecolor("#1a2536")
    plt.tight_layout()
    out = FIGS / "var_frequency.png"
    plt.savefig(out, dpi=150, facecolor="#06090f")
    plt.close()
    print(f"  ✓ {out.name}")


# ─── 6. ANÁLISE SENSITIVITY — PESOS ALTERNATIVOS ──────────────────────────

def sensitivity_analysis(df: "pd.DataFrame") -> "pd.DataFrame":
    """
    Testa 4 cenários de pesos alternativos:
      A) Pesos base (calibrado comparado)
      B) Democracia: academia e perfil_int sobem
      C) Conflito: militar e segurança sobem muito
      D) Renovação: idade e trajectória recente dominam
    """
    scenarios = {
        "Base":       {c: WEIGHTS[c] for c in SCORE_COLS},
        "Abertura":   dict(s_cargo=.15, s_partido=.12, s_seguranca=.08, s_proximidade=.10,
                          s_burpol=.10, s_trajetoria=.10, s_militar=.03, s_academia=.15,
                          s_perfil_int=.12, s_idade=.05),
        "Tensão":     dict(s_cargo=.15, s_partido=.10, s_seguranca=.25, s_proximidade=.15,
                          s_burpol=.08, s_trajetoria=.07, s_militar=.12, s_academia=.03,
                          s_perfil_int=.02, s_idade=.03),
        "Renovação":  dict(s_cargo=.20, s_partido=.10, s_seguranca=.12, s_proximidade=.12,
                          s_burpol=.12, s_trajetoria=.15, s_militar=.02, s_academia=.08,
                          s_perfil_int=.05, s_idade=.04),
    }

    results = {}
    for scenario, w in scenarios.items():
        df[f"score_{scenario}"] = sum(df[c] * w[c] for c in SCORE_COLS) * 10
        results[scenario] = df.set_index("nome_curto")[f"score_{scenario}"].to_dict()

    print("\nAnálise de Sensibilidade (scores 0–100):")
    print(f"{'Candidato':<30} {'Base':>8} {'Abertura':>10} {'Tensão':>8} {'Renovação':>10}")
    print("-" * 70)
    for _, row in df.sort_values("score_Base", ascending=False).iterrows():
        print(f"{row['nome_curto']:<30} "
              f"{row['score_Base']:>8.1f} "
              f"{row['score_Abertura']:>10.1f} "
              f"{row['score_Tensão']:>8.1f} "
              f"{row['score_Renovação']:>10.1f}")
    return df


# ─── 7. MODELO RF (quando houver dados suficientes) ───────────────────────

def build_rf_model(df_comp: "pd.DataFrame"):
    """
    Treina um Random Forest sobre os casos comparados.
    NOTA: 12 casos são insuficientes para um modelo robusto —
    isto é um protótipo pedagógico. Para produção, precisas
    de 40-60 casos codificados com as mesmas variáveis.
    """
    try:
        from sklearn.ensemble import RandomForestClassifier
        from sklearn.preprocessing import LabelEncoder
        import numpy as np
    except ImportError:
        print("  scikit-learn não instalado. Saltar modelo RF.")
        return

    # Variáveis binárias disponíveis nos casos comparados
    feat_cols = [
        "tinha_carteira_seguranca",
        "tinha_carteira_militar",
        "tinha_carteira_economica",
        "estava_no_partido_lideranca",
        "era_vp_antes",
        "idade_chegada",
        "anos_partido_chegada",
    ]

    # target: atingiu o poder (todos os casos = sim, por definição)
    # Aqui simulamos um problema de classificação binária:
    # chegou ao poder de forma "suave" (partido/institucional) vs "disruptiva" (golpe/morte)
    df_comp["chegada_institucional"] = df_comp["mecanismo_chegada"].apply(
        lambda x: 0 if any(w in x.lower() for w in ["golpe","morte","dimissão","herança"]) else 1
    )

    X = df_comp[feat_cols].fillna(0).values
    y = df_comp["chegada_institucional"].values

    rf = RandomForestClassifier(n_estimators=100, random_state=42)
    rf.fit(X, y)

    importances = rf.feature_importances_
    print("\nImportância das variáveis (Random Forest — casos comparados):")
    for feat, imp in sorted(zip(feat_cols, importances), key=lambda x: -x[1]):
        bar = "█" * int(imp * 50)
        print(f"  {feat:<35} {imp:.3f}  {bar}")

    return rf, feat_cols


# ─── 8. EXPORTAR RELATÓRIO TEXTO ──────────────────────────────────────────

def export_text_report(df: "pd.DataFrame", df_comp: "pd.DataFrame"):
    out = DATA / "relatorio_analise.txt"
    with open(out, "w", encoding="utf-8") as f:
        f.write("ANGOLA SUCCESSION DATASET — RELATÓRIO DE ANÁLISE\n")
        f.write("=" * 60 + "\n\n")

        f.write("RANKING FINAL (score ponderado 0-100)\n")
        f.write("-" * 40 + "\n")
        for _, row in df.sort_values("ranking").iterrows():
            f.write(f"  #{int(row['ranking'])}  {row['nome_curto']:<28}  {row['score_total_0_100']:5.1f}\n")

        f.write("\nCARACTERÍSTICAS DO CANDIDATO LÍDER\n")
        f.write("-" * 40 + "\n")
        top = df.sort_values("ranking").iloc[0]
        for col in ["nome", "nascimento", "cargo_funcao",
                    "tem_score_detalhado"]:
            f.write(f"  {col}: {top[col]}\n")

        f.write("\nPADRÃO EXTRAÍDO DOS CASOS COMPARADOS\n")
        f.write("-" * 40 + "\n")
        bool_cols = {
            "tinha_carteira_seguranca":    "Carteira Segurança",
            "tinha_carteira_militar":      "Capital Militar",
            "estava_no_partido_lideranca": "Liderança Partido",
            "era_vp_antes":                "Era VP antes",
        }
        for c, label in bool_cols.items():
            pct = df_comp[c].mean() * 100
            f.write(f"  {label:<30}  presente em {pct:.0f}% dos casos\n")

        f.write("\n" + "=" * 60 + "\n")
        f.write("Fontes: MPLA.ao, Jornal ÉME, Wikipedia PT/EN, VOA Português\n")
        f.write("governo.gov.ao, IMF Connect, World Bank Live\n")
    print(f"  ✓ {out.name}")


# ─── CONSTANTE DE COR PARA GRÁFICOS ───────────────────────────────────────
C_GOLD = "#E8A020"


# ─── MAIN ─────────────────────────────────────────────────────────────────

def main():
    if not HAS_DEPS:
        print("\nInstalar dependências primeiro:")
        print("  pip install pandas numpy matplotlib scikit-learn")
        return

    print("\nCarregando datasets...")
    df      = load_candidates()
    df_comp = load_comparative()
    df_vars = load_variables()

    print(f"  → {len(df)} candidatos scored")
    print(f"  → {len(df_comp)} casos comparados")
    print(f"  → {len(df_vars)} variáveis")

    # Usar apenas top N para gráficos detalhados
    df_top = df.sort_values("ranking").head(TOP_N_CHARTS).copy()
    df_top["ranking"] = range(1, len(df_top) + 1)

    print(f"\nGerando gráficos (top {TOP_N_CHARTS} de {len(df)})...")
    plot_heatmap(df_top)
    plot_radars(df_top)
    plot_ranking_bars(df_top)
    plot_var_frequency(df_comp)

    print("\nAnálise de sensibilidade (top 15)...")
    df_top = sensitivity_analysis(df_top)

    print("\nModelo Random Forest...")
    build_rf_model(df_comp)

    print("\nRelatório de texto...")
    export_text_report(df, df_comp)  # usa lista completa

    print(f"\n✓ Concluído. Figuras em: {FIGS.resolve()}")


if __name__ == "__main__":
    main()
