import streamlit as st
import pandas as pd
import math
import random
from collections import defaultdict

def solve_speed_business_optimized(participants, max_per_table, n_rounds, exclusion_groups, obligation_pairs):
    n_p = len(participants)
    n_t = math.ceil(n_p / max_per_table)

    # Préparation des exclusions par index
    excl_sets = []
    for group in exclusion_groups:
        idx = frozenset(i for i, name in enumerate(participants) if name in group)
        if len(idx) >= 2:
            excl_sets.append(idx)

    excl_for = defaultdict(list)
    for s in excl_sets:
        for p in s:
            excl_for[p].append(s)

    # Préparation des obligations par index
    obl_pairs_idx = []
    for pair in obligation_pairs:
        if len(pair) >= 2:
            a, b = pair[0].strip(), pair[1].strip()
            if a in participants and b in participants:
                obl_pairs_idx.append((participants.index(a), participants.index(b)))

    def make_valid_plan():
        shuffled = list(range(n_p))
        random.shuffle(shuffled)
        groups = [shuffled[i::n_t] for i in range(n_t)]
        plan = []
        for r in range(n_rounds):
            assignment = [0] * n_p
            for g_idx, group in enumerate(groups):
                table = (g_idx + r) % n_t
                for p in group:
                    assignment[p] = table
            plan.append(assignment)
        return plan

    def check_all_hard(plan):
        for r in range(n_rounds):
            for s in excl_sets:
                tables = [plan[r][p] for p in s]
                if len(tables) != len(set(tables)):
                    return False
        for r in range(n_rounds - 1):
            for p in range(n_p):
                if plan[r][p] == plan[r + 1][p]:
                    return False
        return True

    def check_exclusion_at(plan, r, p, new_table):
        for s in excl_for[p]:
            for other in s:
                if other != p and plan[r][other] == new_table:
                    return False
        return True

    def check_stagnation_at(plan, r, p, new_table):
        if r > 0 and plan[r - 1][p] == new_table:
            return False
        if r < n_rounds - 1 and plan[r + 1][p] == new_table:
            return False
        return True

    def build_meetings(plan):
        meetings = [[0] * n_p for _ in range(n_p)]
        for r in range(n_rounds):
            by_table = defaultdict(list)
            for p in range(n_p):
                by_table[plan[r][p]].append(p)
            for members in by_table.values():
                for i in range(len(members)):
                    for j in range(i + 1, len(members)):
                        meetings[members[i]][members[j]] += 1
                        meetings[members[j]][members[i]] += 1
        return meetings

    def count_doublons(meetings):
        return sum(
            meetings[p1][p2] - 1
            for p1 in range(n_p)
            for p2 in range(p1 + 1, n_p)
            if meetings[p1][p2] > 1
        )

    def obligations_ok(meetings):
        return all(meetings[p1][p2] > 0 for p1, p2 in obl_pairs_idx)

    def full_score(doublons, meetings):
        return doublons * 1000 + (0 if obligations_ok(meetings) else 5000)

    best_plan, best_score, best_doublons = None, float('inf'), float('inf')

    for attempt in range(20):
        # Cherche un plan de départ valide (hard constraints respectées)
        plan = None
        for _ in range(3000):
            candidate = make_valid_plan()
            if check_all_hard(candidate):
                plan = candidate
                break
        if plan is None:
            continue

        meetings = build_meetings(plan)
        doublons = count_doublons(meetings)
        cur_score = full_score(doublons, meetings)
        no_improve = 0

        for _ in range(200000):
            r = random.randint(0, n_rounds - 1)
            p1, p2 = random.sample(range(n_p), 2)
            t1, t2 = plan[r][p1], plan[r][p2]
            if t1 == t2:
                continue

            # Applique l'échange
            plan[r][p1] = t2
            plan[r][p2] = t1

            # Vérifie les contraintes dures (exclusions + anti-stagnation)
            hard_ok = (
                check_exclusion_at(plan, r, p1, t2) and
                check_exclusion_at(plan, r, p2, t1) and
                check_stagnation_at(plan, r, p1, t2) and
                check_stagnation_at(plan, r, p2, t1)
            )
            if not hard_ok:
                plan[r][p1] = t1
                plan[r][p2] = t2
                continue

            # Mise à jour incrémentale des meetings (O(n) au lieu de O(n²))
            at_t1 = [p for p in range(n_p) if p not in (p1, p2) and plan[r][p] == t1]
            at_t2 = [p for p in range(n_p) if p not in (p1, p2) and plan[r][p] == t2]

            delta_d = 0
            for p3 in at_t1:
                if meetings[p1][p3] > 1: delta_d -= 1
                if meetings[p1][p3] - 1 > 1: delta_d += 1  # après -1
                if meetings[p2][p3] + 1 > 1: delta_d += 1  # après +1
                if meetings[p2][p3] > 1: delta_d -= 1
            for p3 in at_t2:
                if meetings[p1][p3] + 1 > 1: delta_d += 1
                if meetings[p1][p3] > 1: delta_d -= 1
                if meetings[p2][p3] > 1: delta_d -= 1
                if meetings[p2][p3] - 1 > 1: delta_d += 1

            for p3 in at_t1:
                meetings[p1][p3] -= 1; meetings[p3][p1] -= 1
                meetings[p2][p3] += 1; meetings[p3][p2] += 1
            for p3 in at_t2:
                meetings[p1][p3] += 1; meetings[p3][p1] += 1
                meetings[p2][p3] -= 1; meetings[p3][p2] -= 1

            new_doublons = doublons + delta_d
            new_score = full_score(new_doublons, meetings)

            if new_score <= cur_score:
                doublons = new_doublons
                cur_score = new_score
                no_improve = 0
            else:
                # Annule l'échange
                plan[r][p1] = t1; plan[r][p2] = t2
                for p3 in at_t1:
                    meetings[p1][p3] += 1; meetings[p3][p1] += 1
                    meetings[p2][p3] -= 1; meetings[p3][p2] -= 1
                for p3 in at_t2:
                    meetings[p1][p3] -= 1; meetings[p3][p1] -= 1
                    meetings[p2][p3] += 1; meetings[p3][p2] += 1
                no_improve += 1

            if cur_score == 0:
                break

            # Secousse aléatoire si bloqué
            if no_improve > 10000:
                for _ in range(500):
                    ra = random.randint(0, n_rounds - 1)
                    pa, pb = random.sample(range(n_p), 2)
                    ta, tb = plan[ra][pa], plan[ra][pb]
                    if ta == tb: continue
                    plan[ra][pa] = tb; plan[ra][pb] = ta
                    if check_all_hard(plan): break
                    plan[ra][pa] = ta; plan[ra][pb] = tb
                meetings = build_meetings(plan)
                doublons = count_doublons(meetings)
                cur_score = full_score(doublons, meetings)
                no_improve = 0

        if cur_score < best_score:
            best_score = cur_score
            best_doublons = doublons
            best_plan = [list(r) for r in plan]

        if best_score == 0:
            break

    if best_plan is None:
        return None, 0

    res = []
    for r in range(n_rounds):
        round_data = [{"Participant": participants[p], "Table": best_plan[r][p] + 1, "Rotation": r + 1}
                      for p in range(n_p)]
        res.append(pd.DataFrame(round_data))
    return res, best_doublons


# --- INTERFACE ---
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
                errors.append(f"'{name}' (exclusion) introuvable dans la liste.")
    for pair in obligation_pairs:
        for name in pair:
            if name and name not in all_names:
                errors.append(f"'{name}' (obligation) introuvable dans la liste.")

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

            tabs = st.tabs([f"Rotation {i + 1}" for i in range(n_rounds)])
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
