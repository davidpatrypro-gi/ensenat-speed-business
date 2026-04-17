import streamlit as st
from ortools.sat.python import cp_model
import pandas as pd
import math

# --- 1. FONCTION DE CALCUL ---
def solve_speed_business_ensenat_final(participants, max_per_table, n_rounds, exclusion_groups, obligation_pairs):
    model = cp_model.CpModel()
    n_p = len(participants)
    n_t = math.ceil(n_p / max_per_table)
    
    # x[r, t, p] : Le participant p est à la table t à la rotation r
    x = {}
    for r in range(n_rounds):
        for t in range(n_t):
            for p in range(n_p):
                x[r, t, p] = model.NewBoolVar(f'x_r{r}_t{t}_p{p}')

    # CONTRAINTES DE BASE (PRÉSENCE ET CAPACITÉ)
    for r in range(n_rounds):
        for p in range(n_p):
            model.Add(sum(x[r, t, p] for t in range(n_t)) == 1)
        for t in range(n_t):
            model.Add(sum(x[r, t, p] for p in range(n_p)) <= max_per_table)
            model.Add(sum(x[r, t, p] for p in range(n_p)) >= math.floor(n_p / n_t))  # CORRIGÉ

    # EXCLUSIONS STRICTES
    for r in range(n_rounds):
        for t in range(n_t):
            for group in exclusion_groups:
                indices = [i for i, name in enumerate(participants) if name in group]
                if len(indices) > 1:
                    model.Add(sum(x[r, t, i] for i in indices) <= 1)

    # UNICITÉ ET OBLIGATIONS (OPTIMISATION)
    penalties = []
    for p1 in range(n_p):
        for p2 in range(p1 + 1, n_p):
            p1_n, p2_n = participants[p1], participants[p2]
            meetings = []
            for r in range(n_rounds):
                together_r = model.NewBoolVar(f'm_{p1}_{p2}_{r}')
                t_list = []
                for t in range(n_t):
                    pair_t = model.NewBoolVar(f'p_{p1}_{p2}_{r}_{t}')
                    model.Add(x[r, t, p1] + x[r, t, p2] == 2).OnlyEnforceIf(pair_t)
                    model.Add(x[r, t, p1] + x[r, t, p2] < 2).OnlyEnforceIf(pair_t.Not())
                    t_list.append(pair_t)
                model.Add(together_r == sum(t_list))
                meetings.append(together_r)

            if any({p1_n, p2_n}.issubset(set(pair)) for pair in obligation_pairs):
                model.Add(sum(meetings) >= 1)

            dup = model.NewIntVar(0, n_rounds, f'd_{p1}_{p2}')
            model.Add(dup >= sum(meetings) - 1)
            penalties.append(dup * 10000)

    # ANTI-STAGNATION
    for r in range(n_rounds - 1):
        for p in range(n_p):
            for t in range(n_t):
                model.Add(x[r, t, p] + x[r+1, t, p] <= 1)

    model.Minimize(sum(penalties))
    solver = cp_model.CpSolver()
    solver.parameters.max_time_in_seconds = 30.0
    status = solver.Solve(model)

    if status in [cp_model.FEASIBLE, cp_model.OPTIMAL]:
        res = []
        doublons = int(solver.ObjectiveValue() / 10000)
        for r in range(n_rounds):
            round_data = []
            for p in range(n_p):
                for t in range(n_t):
                    if solver.Value(x[r, t, p]) == 1:
                        round_data.append({"Participant": participants[p], "Table": t + 1, "Rotation": r + 1})
            res.append(pd.DataFrame(round_data))
        return res, doublons
    return None, 0

# --- 2. INTERFACE UTILISATEUR ---
st.set_page_config(page_title="Ensenat Master Optimizer", layout="wide")
st.title("🛡️ Speed Business Optimizer - Version Master")

with st.sidebar:
    st.header("⚙️ Configuration")
    raw_names = st.text_area("Participants (un par ligne)", "Jean\nMarie\nPierre\nSophie\nLuc\nJulie\nAntoine\nClara")
    participants = [n.strip() for n in raw_names.split('\n') if n.strip()]
    n_p = len(participants)
    n_rounds = st.number_input("Nombre de rotations", 1, 10, 4)
    max_per_table = st.number_input("Max personnes par table", 2, 20, 8)
    n_t_calc = math.ceil(n_p / max_per_table)
    st.info(f"Résumé : {n_p} participants | {n_t_calc} tables")

col1, col2 = st.columns(2)
with col1:
    st.markdown("### 🚫 Exclusions (Strictes)")
    excl_input = st.text_area("Ex: Coach1,Coach2 (Un groupe par ligne)", key="excl")
    exclusion_groups = [[n.strip() for n in line.split(',')] for line in excl_input.split('\n') if ',' in line]  # CORRIGÉ
with col2:
    st.markdown("### 🔗 Obligations (Strictes)")
    obl_input = st.text_area("Ex: Jean,Marie (Un binôme par ligne)", key="obl")
    obligation_pairs = [[n.strip() for n in line.split(',')] for line in obl_input.split('\n') if ',' in line]  # CORRIGÉ

if st.button("🚀 Générer la solution"):
    # VALIDATION
    errors = []
    all_names = set(participants)
    if n_p < 2:
        errors.append("Il faut au moins 2 participants.")
    for group in exclusion_groups:
        for name in group:
            if name and name not in all_names:
                errors.append(f"'{name}' (exclusion) introuvable dans la liste de participants.")
    for pair in obligation_pairs:
        for name in pair:
            if name and name not in all_names:
                errors.append(f"'{name}' (obligation) introuvable dans la liste de participants.")

    if errors:
        for e in errors:
            st.error(e)
    else:
        with st.spinner("Optimisation en cours (max 300s)..."):
            solution, doublons = solve_speed_business_ensenat_final(
                participants, max_per_table, n_rounds, exclusion_groups, obligation_pairs)

        if solution:
            score = max(0, min(100, 100 - (doublons * 2)))  # CORRIGÉ
            st.metric("Score de Mixage", f"{score}%")
            if doublons > 0:
                st.warning(f"⚠️ {doublons} doublon(s) détecté(s). Essayez d'augmenter le nombre de rotations.")
            else:
                st.success("✅ Solution optimale — aucun doublon !")

            df_total = pd.concat(solution)
            csv = df_total.to_csv(index=False).encode('utf-8-sig')
            st.download_button("📥 Télécharger CSV", csv, "planning.csv", "text/csv")

            tabs = st.tabs([f"Rotation {i+1}" for i in range(n_rounds)])
            for i, tab in enumerate(tabs):
                with tab:
                    df_round = solution[i].sort_values("Table")
                    st.table(df_round)
                    st.markdown("**Vue par table :**")
                    for table_num in sorted(df_round["Table"].unique()):
                        membres = df_round[df_round["Table"] == table_num]["Participant"].tolist()
                        st.write(f"🪑 Table {table_num} : {' • '.join(membres)}")
        else:
            st.error("❌ Impossible de trouver une solution avec ces contraintes.")
