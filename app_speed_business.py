import streamlit as st
from ortools.sat.python import cp_model
import pandas as pd
import math

def solve_speed_business_ensenat_final(participants, max_per_table, n_rounds, exclusion_groups, obligation_pairs):
    model = cp_model.CpModel()
    n_p = len(participants)
    n_t = math.ceil(n_p / max_per_table)
    
    # --- VARIABLES ---
    # x[r, t, p] : Le participant p est à la table t à la rotation r
    x = {}
    for r in range(n_rounds):
        for t in range(n_t):
            for p in range(n_p):
                x[r, t, p] = model.NewBoolVar(f'x_r{r}_t{t}_p{p}')

    # --- 1. CONTRAINTES DE PRÉSENCE ET CAPACITÉ ---
    for r in range(n_rounds):
        for p in range(n_p):
            model.Add(sum(x[r, t, p] for t in range(n_t)) == 1)
        
        for t in range(n_t):
            model.Add(sum(x[r, t, p] for p in range(n_p)) <= max_per_table)
            model.Add(sum(x[r, t, p] for p in range(n_p)) >= (n_p // n_t))

    # --- 2. EXCLUSIONS STRICTES (HARD) ---
    for r in range(n_rounds):
        for t in range(n_t):
            for group in exclusion_groups:
                indices = [i for i, name in enumerate(participants) if name in group]
                if len(indices) > 1:
                    model.Add(sum(x[r, t, i] for i in indices) <= 1)

    # --- 3. LOGIQUE D'UNICITÉ DES RENCONTRES (LE CŒUR DU PROBLÈME) ---
    # On veut minimiser le fait de se voir plus d'une fois.
    meeting_penalties = []

    for p1 in range(n_p):
        for p2 in range(p1 + 1, n_p):
            p1_n, p2_n = participants[p1], participants[p2]
            
            # Pour chaque rotation, sont-ils ensemble ?
            together_rounds = []
            for r in range(n_rounds):
                together_r = model.NewBoolVar(f'meet_p{p1}_p{p2}_r{r}')
                
                # Ils sont ensemble au round r s'ils partagent la même table t
                table_indicators = []
                for t in range(n_t):
                    pair_at_t = model.NewBoolVar(f'pair_p{p1}_p{p2}_r{r}_t{t}')
                    # pair_at_t est vrai si les deux sont à la table t
                    model.Add(x[r, t, p1] + x[r, t, p2] == 2).OnlyEnforceIf(pair_at_t)
                    model.Add(x[r, t, p1] + x[r, t, p2] < 2).OnlyEnforceIf(pair_at_t.Not())
                    table_indicators.append(pair_at_t)
                
                # meet_p1_p2_r est vrai si l'un des pair_at_t est vrai
                model.Add(together_r == sum(table_indicators))
                together_rounds.append(together_r)

            # OBLIGATIONS STRICTES
            if any({p1_n, p2_n}.issubset(set(pair)) for pair in obligation_pairs):
                model.Add(sum(together_rounds) >= 1)

            # PÉNALITÉ POUR DOUBLON (Très forte : 10 000)
            # Cette règle force le renouvellement du voisinage : 
            # Si un participant reste à sa table, ses voisins ne peuvent pas rester.
            duplicate_penalty = model.NewIntVar(0, n_rounds, f'dup_p{p1}_p{p2}')
            model.Add(duplicate_penalty >= sum(together_rounds) - 1)
            meeting_penalties.append(duplicate_penalty * 10000)

    # --- 4. OPTIMISATION ---
    model.Minimize(sum(meeting_penalties))

    # --- 5. RÉSOLUTION ---
    solver = cp_model.CpSolver()
    solver.parameters.max_time_in_seconds = 60.0 # On laisse 1 minute pour éliminer les doublons
    solver.parameters.num_search_workers = 8
    status = solver.Solve(model)

    if status in [cp_model.FEASIBLE, cp_model.OPTIMAL]:
        results = []
        doublons = int(solver.ObjectiveValue() / 10000)
        for r in range(n_rounds):
            round_data = []
            for p in range(n_p):
                for t in range(n_t):
                    if solver.Value(x[r, t, p]) == 1:
                        round_data.append({"Participant": participants[p], "Table": t + 1, "Rotation": r + 1})
            results.append(pd.DataFrame(round_data))
        return results, doublons
    return None, 0

# --- INTERFACE ---
st.set_page_config(page_title="Ensenat Optimizer Final", layout="wide")
st.title("🤝 Speed Business Optimizer - Règle d'Unicité")

with st.sidebar:
    st.header("Configuration")
    raw_names = st.text_area("Participants", "Jean\nMarie\nPierre...")
    participants = [n.strip() for n in raw_names.split('\n') if n.strip()]
    n_p = len(participants)
    n_rounds = st.number_input("Rotations", 1, 10, 4)
    max_per_table = st.number_input("Max/Table", 2, 20, 8)

if st.button("🚀 Générer le planning"):
    with st.spinner("Optimisation du voisinage en cours..."):
        solution, doublons = solve_speed_business_ensenat_final(participants, max_per_table, n_rounds, [], [])
    
    if solution:
        score = max(0, 100 - (doublons * 5))
        st.metric("Qualité du Mixage (0 doublon souhaité)", f"{score}%")
        
        if doublons == 0:
            st.success("🎯 Parfait : Personne ne se croise deux fois !")
        else:
            st.warning(f"⚠️ {doublons} rencontre(s) répétée(s) inévitable(s).")

        df_total = pd.concat(solution)
        st.download_button("📥 Télécharger CSV", df_total.to_csv(index=False).encode('utf-8-sig'), "planning.csv")
        
        tabs = st.tabs([f"Rotation {i+1}" for i in range(n_rounds)])
        for i, tab in enumerate(tabs):
            with tab:
                st.table(solution[i].sort_values("Table"))
