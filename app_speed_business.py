import streamlit as st
from ortools.sat.python import cp_model
import pandas as pd
import math

def solve_speed_business_pro(participants, max_per_table, n_rounds, exclusion_groups, obligation_pairs):
    model = cp_model.CpModel()
    n_p = len(participants)
    n_tables = math.ceil(n_p / max_per_table)
    
    # --- VARIABLES ---
    x = {}
    for r in range(n_rounds):
        for t in range(n_tables):
            for p in range(n_p):
                x[r, t, p] = model.NewBoolVar(f'x_r{r}_t{t}_p{p}')

    # --- 1. SYMMETRY BREAKING (ACCÉLÉRATEUR) ---
    # On fige la rotation 1 : les gens s'assoient dans l'ordre d'arrivée
    # Cela évite au solveur de chercher des millions de variantes identiques
    for p in range(n_p):
        target_table = p // max_per_table
        if target_table < n_tables:
            model.Add(x[0, target_table, p] == 1)

    # --- 2. CONTRAINTES STRICTES (HARD) ---
    for r in range(n_rounds):
        for p in range(n_p):
            model.Add(sum(x[r, t, p] for t in range(n_tables)) == 1)
        
        for t in range(n_tables):
            model.Add(sum(x[r, t, p] for p in range(n_p)) <= max_per_table)
            model.Add(sum(x[r, t, p] for p in range(n_p)) >= (n_p // n_tables))

    # --- 3. ANTI-STAGNATION (NOUVEAU) ---
    # Interdiction d'être à la même table r et r+1
    for r in range(n_rounds - 1):
        for p in range(n_p):
            for t in range(n_tables):
                model.Add(x[r, t, p] + x[r+1, t, p] <= 1)

    # EXCLUSIONS STRICTES
    for r in range(n_rounds):
        for t in range(n_tables):
            for group in exclusion_groups:
                indices = [i for i, name in enumerate(participants) if name in group]
                if len(indices) > 1:
                    model.Add(sum(x[r, t, i] for i in indices) <= 1)

    # --- 4. LOGIQUE DE RENCONTRE & DOUBLONS ---
    redundant_meetings = []
    for p1 in range(n_p):
        for p2 in range(p1 + 1, n_p):
            p1_n, p2_n = participants[p1], participants[p2]
            pair_meetings = []
            for r in range(n_rounds):
                met_r = model.NewBoolVar(f'meet_p{p1}_p{p2}_r{r}')
                for t in range(n_tables):
                    together_t = model.NewBoolVar(f'tog_p{p1}_p{p2}_r{r}_t{t}')
                    model.Add(x[r, t, p1] + x[r, t, p2] == 2).OnlyEnforceIf(together_t)
                    model.Add(x[r, t, p1] + x[r, t, p2] < 2).OnlyEnforceIf(together_t.Not())
                    model.Add(met_r == 1).OnlyEnforceIf(together_t)
                pair_meetings.append(met_r)

            if any({p1_n, p2_n}.issubset(set(pair)) for pair in obligation_pairs):
                model.Add(sum(pair_meetings) >= 1)

            # Pénalité TRÈS forte pour les doublons
            penalty = model.NewIntVar(0, n_rounds, f'pen_p{p1}_p{p2}')
            model.Add(penalty >= sum(pair_meetings) - 1)
            redundant_meetings.append(penalty * 1000)

    model.Minimize(sum(redundant_meetings))

    # --- RÉSOLUTION ---
    solver = cp_model.CpSolver()
    solver.parameters.max_time_in_seconds = 45.0 # Temps optimal
    solver.parameters.num_search_workers = 8
    status = solver.Solve(model)

    if status in [cp_model.FEASIBLE, cp_model.OPTIMAL]:
        results = []
        total_doublons = int(solver.ObjectiveValue() / 1000)
        for r in range(n_rounds):
            round_data = []
            for p in range(n_p):
                for t in range(n_tables):
                    if solver.Value(x[r, t, p]) == 1:
                        round_data.append({"Participant": participants[p], "Table": t + 1, "Rotation": r + 1})
            results.append(pd.DataFrame(round_data))
        return results, total_doublons
    return None, 0

# --- INTERFACE ---
st.set_page_config(page_title="Ensenat Pro Optimizer", layout="wide")
st.title("🚀 Optimizer Business Pro - Groupe Ensenat")

with st.sidebar:
    st.header("⚙️ Configuration")
    raw_names = st.text_area("Participants (un par ligne)", "Jean\nMarie\nPierre...")
    participants = [n.strip() for n in raw_names.split('\n') if n.strip()]
    n_p = len(participants)
    n_rounds = st.number_input("Nombre de rotations", 1, 10, 4)
    max_per_table = st.number_input("Max personnes par table", 2, 20, 8)

col1, col2 = st.columns(2)
with col1:
    excl_groups = [line.split(',') for line in st.text_area("🚫 Exclusions").split('\n') if ',' in line]
with col2:
    obl_pairs = [line.split(',') for line in st.text_area("🔗 Obligations").split('\n') if ',' in line]

if st.button("🚀 Lancer l'Optimisation"):
    with st.spinner("Recherche de la solution parfaite..."):
        solution, doublons = solve_speed_business_pro(participants, max_per_table, n_rounds, excl_groups, obl_pairs)
    
    if solution:
        # Calcul du score de qualité
        total_possible_meets = (n_p * (n_p - 1)) / 2
        score = max(0, 100 - (doublons * 2))
        
        st.metric("Score de Qualité", f"{score}%", help="100% signifie zéro doublon et respect strict de toutes les règles.")
        
        if doublons == 0:
            st.success("🎯 Solution Parfaite trouvée !")
        else:
            st.warning(f"⚠️ Solution optimisée avec seulement {doublons} doublon(s).")

        csv = pd.concat(solution).to_csv(index=False).encode('utf-8-sig')
        st.download_button("📥 Télécharger le planning CSV", csv, "planning_pro.csv", "text/csv")
        
        tabs = st.tabs([f"Rotation {i+1}" for i in range(n_rounds)])
        for i, tab in enumerate(tabs):
            with tab:
                st.table(solution[i].sort_values("Table"))
