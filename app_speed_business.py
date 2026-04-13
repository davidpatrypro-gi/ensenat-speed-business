import streamlit as st
from ortools.sat.python import cp_model
import pandas as pd
import math

# --- LOGIQUE DE RÉPARTITION OPTIMISÉE ---
def solve_speed_business_optimized(participants, max_per_table, n_rounds, exclusion_groups, obligation_pairs):
    model = cp_model.CpModel()
    n_p = len(participants)
    n_tables = math.ceil(n_p / max_per_table)
    
    # --- VARIABLES ---
    x = {}
    for r in range(n_rounds):
        for t in range(n_tables):
            for p in range(n_p):
                x[r, t, p] = model.NewBoolVar(f'x_r{r}_t{t}_p{p}')

    # --- CONTRAINTES STRICTES (HARD) ---
    for r in range(n_rounds):
        for p in range(n_p):
            model.Add(sum(x[r, t, p] for t in range(n_tables)) == 1)
        
        for t in range(n_tables):
            model.Add(sum(x[r, t, p] for p in range(n_p)) <= max_per_table)
            model.Add(sum(x[r, t, p] for p in range(n_p)) >= (n_p // n_tables))

    # EXCLUSIONS STRICTES
    for r in range(n_rounds):
        for t in range(n_tables):
            for group in exclusion_groups:
                indices = [i for i, name in enumerate(participants) if name in group]
                if len(indices) > 1:
                    model.Add(sum(x[r, t, i] for i in indices) <= 1)

    # --- LOGIQUE DE RENCONTRE (AVEC FORTE PÉNALITÉ) ---
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

            # OBLIGATIONS STRICTES
            if any({p1_n, p2_n}.issubset(set(pair)) for pair in obligation_pairs):
                model.Add(sum(pair_meetings) >= 1)

            # PÉNALITÉ DE DOUBLON (Poids de 100 pour forcer l'unicité)
            penalty = model.NewIntVar(0, n_rounds, f'pen_p{p1}_p{p2}')
            model.Add(penalty >= sum(pair_meetings) - 1)
            redundant_meetings.append(penalty * 100)

    # --- OBJECTIF ---
    model.Minimize(sum(redundant_meetings))

    # --- RÉSOLUTION ---
    solver = cp_model.CpSolver()
    solver.parameters.max_time_in_seconds = 30.0 # Temps de réflexion pro
    solver.parameters.num_search_workers = 4     # Utilisation de la puissance CPU
    
    status = solver.Solve(model)

    if status in [cp_model.FEASIBLE, cp_model.OPTIMAL]:
        results = []
        total_doublons = int(solver.ObjectiveValue() / 100)
        for r in range(n_rounds):
            round_data = []
            for p in range(n_p):
                for t in range(n_tables):
                    if solver.Value(x[r, t, p]) == 1:
                        round_data.append({"Participant": participants[p], "Table": t + 1, "Rotation": r + 1})
            results.append(pd.DataFrame(round_data))
        return results, total_doublons
    return None, 0

# --- INTERFACE UTILISATEUR ---
st.set_page_config(page_title="Ensenat Optimizer", layout="wide", page_icon="🤝")
st.title("🛡️ Speed Business Optimizer - Groupe Ensenat")

with st.sidebar:
    st.header("⚙️ Configuration")
    raw_names = st.text_area("Participants (un par ligne)", "P1\nP2\n...\n(Collez vos noms ici)")
    participants = [n.strip() for n in raw_names.split('\n') if n.strip()]
    n_p = len(participants)
    n_rounds = st.number_input("Nombre de rotations", 1, 10, 4)
    max_per_table = st.number_input("Max personnes par table", 2, 20, 8)
    st.info(f"Config : {n_p} participants / {math.ceil(n_p/max_per_table)} tables")

col1, col2 = st.columns(2)
with col1:
    excl_in = st.text_area("🚫 Groupes d'Exclusions (ex: Coach1,Coach2)")
    exclusion_groups = [line.split(',') for line in excl_in.split('\n') if ',' in line]
with col2:
    obl_in = st.text_area("🔗 Obligations (ex: Pierre,Sophie)")
    obligation_pairs = [line.split(',') for line in obl_in.split('\n') if ',' in line]

if st.button("🚀 Générer la meilleure solution"):
    if n_p < 2:
        st.error("Ajoutez des participants.")
    else:
        with st.spinner("Calcul de la solution optimale en cours (30s max)..."):
            solution, doublons = solve_speed_business_optimized(participants, max_per_table, n_rounds, exclusion_groups, obligation_pairs)
        
        if solution:
            if doublons == 0:
                st.success("✅ Solution Parfaite : Zéro doublon.")
            else:
                st.warning(f"⚠️ Solution Optimisée : {doublons} doublon(s) inévitable(s).")
            
            df_total = pd.concat(solution)
            csv = df_total.to_csv(index=False).encode('utf-8-sig')
            st.download_button("📥 Télécharger (CSV)", csv, "planning_ensenat.csv", "text/csv")
            
            tabs = st.tabs([f"Rotation {i+1}" for i in range(n_rounds)])
            for i, tab in enumerate(tabs):
                with tab:
                    st.table(solution[i].sort_values("Table"))
        else:
            st.error("❌ Impossible de trouver une solution avec vos exclusions strictes.")