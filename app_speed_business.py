import streamlit as st
import pandas as pd
import math
import random

# --- 1. ALGORITHME (Recuit Simulé) ---
def solve_speed_business_optimized(participants, max_per_table, n_rounds, exclusion_groups, obligation_pairs):
    n_p = len(participants)
    n_t = math.ceil(n_p / max_per_table)

    # Index des exclusions et obligations
    excl_sets = [set(g) for g in exclusion_groups]
    obl_pairs = [tuple(sorted([participants.index(a), participants.index(b)]))
                 for a, b in obligation_pairs
                 if a in participants and b in participants]

    def make_random_plan():
        plan = []
        for r in range(n_rounds):
            perm = list(range(n_p))
            random.shuffle(perm)
            assignment = {}
            for i, p in enumerate(perm):
                assignment[p] = i % n_t
            plan.append(assignment)
        return plan

    def check_exclusions(plan):
        for r in range(n_rounds):
            for s in excl_sets:
                indices = [i for i, name in enumerate(participants) if name in s]
                tables_used = [plan[r][i] for i in indices]
                if len(tables_used) != len(set(tables_used)):
                    return False
        return True

    def count_doublons(plan):
        from collections import defaultdict
        meetings = defaultdict(int)
        for r in range(n_rounds):
            table_members = [[] for _ in range(n_t)]
            for p, t in plan[r].items():
                table_members[t].append(p)
            for members in table_members:
                for i in range(len(members)):
                    for j in range(i+1, len(members)):
                        pair = tuple(sorted([members[i], members[j]]))
                        meetings[pair] += 1
        doublons = sum(max(0, v - 1) for v in meetings.values())
        return doublons, meetings

    def check_obligations(meetings):
        for p1, p2 in obl_pairs:
            pair = tuple(sorted([p1, p2]))
            if meetings.get(pair, 0) == 0:
                return False
        return True

    def check_stagnation(plan):
        for r in range(n_rounds - 1):
            for p in range(n_p):
                if plan[r][p] == plan[r+1][p]:
                    return False
        return True

    def score(plan):
        d, meetings = count_doublons(plan)
        penalty = d * 1000
        if not check_obligations(meetings):
            penalty += 5000
        if not check_stagnation(plan):
            penalty += 500
        return penalty, d, meetings

    # Recherche locale
    best_plan = None
    best_score = float('inf')
    best_doublons = float('inf')

    for attempt in range(10):  # 10 tentatives depuis des points de départ différents
        # Génère un plan valide (respecte les exclusions)
        for _ in range(1000):
            plan = make_random_plan()
            if check_exclusions(plan):
                break
        else:
            continue

        current_score, _, _ = score(plan)

        # Recuit simulé
        for iteration in range(80000):
            # Choisit une rotation et échange deux participants de tables différentes
            r = random.randint(0, n_rounds - 1)
            p1, p2 = random.sample(range(n_p), 2)
            if plan[r][p1] == plan[r][p2]:
                continue

            # Applique l'échange
            plan[r][p1], plan[r][p2] = plan[r][p2], plan[r][p1]

            # Vérifie les exclusions
            if not check_exclusions(plan):
                plan[r][p1], plan[r][p2] = plan[r][p2], plan[r][p1]
                continue

            new_score, new_d, _ = score(plan)

            # Accepte si meilleur
            if new_score < current_score:
                current_score = new_score
            else:
                plan[r][p1], plan[r][p2] = plan[r][p2], plan[r][p1]

            if current_score == 0:
                break

        s, d, meetings = score(plan)
        if s < best_score:
            best_score = s
            best_doublons = d
            best_plan = [dict(p) for p in plan]

        if best_score == 0:
            break

    if best_plan is None:
        return None, 0

    # Construit le résultat
    res = []
    for r in range(n_rounds):
        round_data = []
        for p in range(n_p):
            round_data.append({
                "Participant": participants[p],
                "Table": best_plan[r][p] + 1,
                "Rotation": r + 1
            })
        res.append(pd.DataFrame(round_data))

    return res, best_doublons

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
    exclusion_groups = [[n.strip() for n in line.split(',')] for line in excl_input.split('\n') if ',' in line]
with col2:
    st.markdown("### 🔗 Obligations (Strictes)")
    obl_input = st.text_area("Ex: Jean,Marie (Un binôme par ligne)", key="obl")
    obligation_pairs = [[n.strip() for n in line.split(',')] for line in obl_input.split('\n') if ',' in line]

if st.button("🚀 Générer la solution"):
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
        with st.spinner("Optimisation en cours..."):
            solution, doublons = solve_speed_business_optimized(
                participants, max_per_table, n_rounds, exclusion_groups, obligation_pairs)

        if solution:
            score = max(0, min(100, 100 - (doublons * 2)))
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
