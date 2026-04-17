import streamlit as st
import pandas as pd
import math
import random
import math as _m
from collections import defaultdict


# --- DIAGNOSTIC ---
def diagnose(participants, max_per_table, n_rounds, exclusion_groups, obligation_pairs):
    n_p = len(participants)
    n_t = math.ceil(n_p / max_per_table)
    table_size = n_p / n_t
    problems = []
    warnings = []

    # 1. Pas assez de participants
    if n_p < 2:
        problems.append("❌ Il faut au moins 2 participants.")
        return problems, warnings

    # 2. Anti-stagnation impossible (plus de rotations que de tables)
    if n_rounds >= n_t:
        problems.append(
            f"❌ Anti-stagnation impossible : {n_rounds} rotations pour seulement {n_t} table(s). "
            f"Une personne n'a que {n_t} tables disponibles et ne peut pas en changer à chaque rotation. "
            f"→ Réduisez à {n_t - 1} rotation(s) max, ou augmentez le nombre de tables."
        )

    # 3. Noms invalides dans les contraintes
    all_names = set(participants)
    for group in exclusion_groups:
        for name in group:
            if name and name not in all_names:
                problems.append(f"❌ '{name}' (exclusion) est introuvable dans la liste des participants.")
    for pair in obligation_pairs:
        for name in pair:
            if name and name not in all_names:
                problems.append(f"❌ '{name}' (obligation) est introuvable dans la liste des participants.")

    if problems:
        return problems, warnings

    # 4. Contradiction obligation + exclusion sur la même paire
    for pair in obligation_pairs:
        if len(pair) < 2:
            continue
        a, b = pair[0].strip(), pair[1].strip()
        for group in exclusion_groups:
            g = [x.strip() for x in group]
            if a in g and b in g:
                problems.append(
                    f"❌ Contradiction : {a} et {b} doivent se rencontrer (obligation) "
                    f"mais ne peuvent jamais se croiser (exclusion). "
                    f"→ Retirez l'un des deux."
                )

    # 5. Exclusion impossible : groupe trop grand pour être séparé
    for group in exclusion_groups:
        g = [x.strip() for x in group if x.strip() in all_names]
        if len(g) > n_t:
            problems.append(
                f"❌ Exclusion impossible : le groupe [{', '.join(g)}] contient {len(g)} personnes "
                f"qui ne peuvent jamais se croiser, mais il n'y a que {n_t} table(s). "
                f"Il faudrait au moins {len(g)} tables pour les séparer. "
                f"→ Augmentez le nombre de tables ou réduisez le groupe."
            )

    # 6. Doublons inévitables (pigeonhole)
    if table_size > n_t:
        min_d_per_pair = n_t * (
            math.comb(math.ceil(table_size / n_t), 2) * (n_p % n_t) +
            math.comb(math.floor(table_size / n_t), 2) * (n_t - n_p % n_t)
        )
        total_m = int(table_size * (table_size - 1) / 2 * n_t * n_rounds)
        total_p = n_p * (n_p - 1) // 2
        min_doublons = max(0, total_m - total_p)
        warnings.append(
            f"⚠️ Doublons inévitables : avec {n_t} table(s) de {table_size:.0f} personnes, "
            f"chaque nouvelle rotation doit forcément regrouper des personnes déjà croisées "
            f"(principe des tiroirs). Minimum {min_doublons} doublon(s) quoi qu'il arrive. "
            f"→ Pour 0 doublon : passez à {n_t + 1} tables (max {math.floor(n_p / (n_t + 1))} par table)."
        )
    else:
        total_m = int(table_size * (table_size - 1) / 2 * n_t * n_rounds)
        total_p = n_p * (n_p - 1) // 2
        if total_m > total_p:
            warnings.append(
                f"⚠️ Trop de rotations : {n_rounds} rotations génèrent {total_m} rencontres "
                f"pour seulement {total_p} paires possibles. "
                f"Des doublons sont inévitables à partir de la rotation {math.floor(total_p / (total_m / n_rounds)) + 1}. "
                f"→ Réduisez à {math.floor(total_p / (total_m / n_rounds))} rotation(s) pour 0 doublon."
            )

    return problems, warnings


# --- ALGORITHME ---
def solve_speed_business(participants, max_per_table, n_rounds, exclusion_groups, obligation_pairs):
    n_p = len(participants)
    n_t = math.ceil(n_p / max_per_table)
    target = [n_p // n_t + (1 if t < n_p % n_t else 0) for t in range(n_t)]

    excl_sets = [frozenset(i for i, name in enumerate(participants) if name in g)
                 for g in exclusion_groups if sum(1 for p in participants if p in g) >= 2]
    excl_for = defaultdict(list)
    for s in excl_sets:
        for p in s: excl_for[p].append(s)
    obl_idx = [(participants.index(a.strip()), participants.index(b.strip()))
               for a, b in obligation_pairs
               if a.strip() in participants and b.strip() in participants]

    def build_m(plan):
        m = [[0] * n_p for _ in range(n_p)]
        for r in range(len(plan)):
            by_t = defaultdict(list)
            for p in range(n_p): by_t[plan[r][p]].append(p)
            for members in by_t.values():
                for i in range(len(members)):
                    for j in range(i + 1, len(members)):
                        m[members[i]][members[j]] += 1
                        m[members[j]][members[i]] += 1
        return m

    def count_d(m):
        return sum(m[p1][p2] - 1 for p1 in range(n_p) for p2 in range(p1 + 1, n_p) if m[p1][p2] > 1)

    def obl_ok(m):
        return all(m[p1][p2] > 0 for p1, p2 in obl_idx)

    def check_excl(asgn, p, t):
        for s in excl_for[p]:
            for other in s:
                if other != p and asgn[other] == t: return False
        return True

    def check_stag(plan, r, p, t):
        if r > 0 and plan[r - 1][p] == t: return False
        if r < n_rounds - 1 and plan[r + 1][p] == t: return False
        return True

    def make_greedy():
        meetings = [[0] * n_p for _ in range(n_p)]
        plan = []
        for r in range(n_rounds):
            tc = [0] * n_t
            asgn = [-1] * n_p
            prev = plan[r - 1] if r > 0 else None
            people = list(range(n_p))
            random.shuffle(people)
            for p in people:
                valid = [t for t in range(n_t)
                         if tc[t] < target[t]
                         and (prev is None or t != prev[p])
                         and check_excl(asgn, p, t)]
                if not valid:
                    valid = [t for t in range(n_t)
                             if tc[t] < target[t] and check_excl(asgn, p, t)]
                if not valid:
                    return None
                best_t = min(valid, key=lambda t: sum(
                    meetings[p][q] for q in range(n_p) if asgn[q] == t))
                asgn[p] = best_t
                tc[best_t] += 1
            by_t = defaultdict(list)
            for p in range(n_p): by_t[asgn[p]].append(p)
            for members in by_t.values():
                for i in range(len(members)):
                    for j in range(i + 1, len(members)):
                        meetings[members[i]][members[j]] += 1
                        meetings[members[j]][members[i]] += 1
            plan.append(asgn)
        return plan

    best_plan, best_d = None, float('inf')

    for attempt in range(30):
        plan = make_greedy()
        if not plan: continue
        m = build_m(plan)
        d = count_d(m)
        score = d * 1000 + (0 if obl_ok(m) else 5000)

        T = 3.0
        cooling = (0.001 / T) ** (1 / 150000)

        for _ in range(150000):
            T *= cooling
            r = random.randint(0, n_rounds - 1)
            p1, p2 = random.sample(range(n_p), 2)
            t1, t2 = plan[r][p1], plan[r][p2]
            if t1 == t2: continue
            plan[r][p1] = t2
            plan[r][p2] = t1
            if not (check_stag(plan, r, p1, t2) and check_stag(plan, r, p2, t1)
                    and check_excl(plan[r], p1, t2) and check_excl(plan[r], p2, t1)):
                plan[r][p1] = t1
                plan[r][p2] = t2
                continue
            at1 = [p for p in range(n_p) if p not in (p1, p2) and plan[r][p] == t1]
            at2 = [p for p in range(n_p) if p not in (p1, p2) and plan[r][p] == t2]
            delta = 0
            for p3 in at1:
                if m[p1][p3] > 1: delta -= 1
                if m[p1][p3] - 1 > 1: delta += 1
                if m[p2][p3] + 1 > 1: delta += 1
                if m[p2][p3] > 1: delta -= 1
            for p3 in at2:
                if m[p1][p3] + 1 > 1: delta += 1
                if m[p1][p3] > 1: delta -= 1
                if m[p2][p3] > 1: delta -= 1
                if m[p2][p3] - 1 > 1: delta += 1
            if delta <= 0 or random.random() < _m.exp(-delta / max(T, 1e-9)):
                for p3 in at1:
                    m[p1][p3] -= 1; m[p3][p1] -= 1
                    m[p2][p3] += 1; m[p3][p2] += 1
                for p3 in at2:
                    m[p1][p3] += 1; m[p3][p1] += 1
                    m[p2][p3] -= 1; m[p3][p2] -= 1
                d = count_d(m)
                new_score = d * 1000 + (0 if obl_ok(m) else 5000)
                if new_score < score:
                    score = new_score
                    if d < best_d:
                        best_d = d
                        best_plan = [list(rr) for rr in plan]
            else:
                plan[r][p1] = t1
                plan[r][p2] = t2
            if d == 0 and obl_ok(m): break
        if best_d == 0 and best_plan and obl_ok(build_m(best_plan)): break

    if best_plan is None: return None, 0
    res = []
    for r in range(n_rounds):
        res.append(pd.DataFrame([
            {"Participant": participants[p], "Table": best_plan[r][p] + 1, "Rotation": r + 1}
            for p in range(n_p)]))
    return res, best_d


# --- INTERFACE ---
st.set_page_config(page_title="Speed Business Optimizer", layout="wide")
st.title("🛡️ Speed Business Optimizer")

with st.sidebar:
    st.header("⚙️ Configuration")
    raw_names = st.text_area("Participants (un par ligne)",
                             "Jean\nMarie\nPierre\nSophie\nLuc\nJulie\nAntoine\nClara\nEmma\nPaul")
    participants = [n.strip() for n in raw_names.split('\n') if n.strip()]
    n_p = len(participants)
    n_rounds = st.number_input("Nombre de rotations", 1, 10, 4)
    max_per_table = st.number_input("Max personnes par table", 2, 20, 5)
    n_t = math.ceil(n_p / max_per_table)
    table_size = n_p / n_t
    st.info(f"**{n_p} participants | {n_t} tables de {table_size:.0f}**")

col1, col2 = st.columns(2)
with col1:
    st.markdown("### 🚫 Exclusions")
    excl_input = st.text_area("Ex: Coach1,Coach2 (un groupe par ligne)", key="excl")
    exclusion_groups = [[n.strip() for n in line.split(',')]
                        for line in excl_input.split('\n') if ',' in line]
with col2:
    st.markdown("### 🔗 Obligations")
    obl_input = st.text_area("Ex: Jean,Marie (un binôme par ligne)", key="obl")
    obligation_pairs = [[n.strip() for n in line.split(',')]
                        for line in obl_input.split('\n') if ',' in line]

# Diagnostic en temps réel (avant le bouton)
problems, warnings = diagnose(
    participants, max_per_table, n_rounds, exclusion_groups, obligation_pairs)

if problems:
    st.markdown("---")
    st.markdown("### 🔍 Diagnostic")
    for p in problems:
        st.error(p)
elif warnings:
    st.markdown("---")
    st.markdown("### 🔍 Diagnostic")
    for w in warnings:
        st.warning(w)
else:
    total_m = int(table_size * (table_size - 1) / 2 * n_t * n_rounds)
    total_p = n_p * (n_p - 1) // 2
    st.markdown("---")
    st.markdown("### 🔍 Diagnostic")
    st.success(
        f"✅ Scénario valide — 0 doublon mathématiquement atteignable. "
        f"({total_m} rencontres pour {total_p} paires possibles)"
    )

# Bouton désactivé si problèmes bloquants
if not problems:
    if st.button("🚀 Générer la solution"):
        with st.spinner("Optimisation en cours..."):
            solution, doublons = solve_speed_business(
                participants, max_per_table, n_rounds, exclusion_groups, obligation_pairs)

        if solution:
            col_a, col_b, col_c = st.columns(3)
            with col_a:
                st.metric("Doublons", doublons)
            with col_b:
                total_m = int(table_size * (table_size - 1) / 2 * n_t * n_rounds)
                total_p = n_p * (n_p - 1) // 2
                pct = min(100, round(total_m / total_p * 100))
                st.metric("Couverture théorique max", f"{pct}%")
            with col_c:
                score = max(0, min(100, 100 - doublons * 2))
                st.metric("Score de mixage", f"{score}%")

            # Vérifie quelles obligations ont été respectées
df_total_check = pd.concat(solution)
obl_non_respectees = []
for pair in obligation_pairs:
    if len(pair) < 2: continue
    a, b = pair[0].strip(), pair[1].strip()
    met = False
    for r in range(1, n_rounds + 1):
        df_r = df_total_check[df_total_check["Rotation"] == r]
        if len(df_r[df_r["Participant"] == a]) == 0: continue
        if len(df_r[df_r["Participant"] == b]) == 0: continue
        ta = df_r[df_r["Participant"] == a]["Table"].values[0]
        tb = df_r[df_r["Participant"] == b]["Table"].values[0]
        if ta == tb:
            met = True
            break
    if not met:
        obl_non_respectees.append(f"{a} & {b}")

if doublons == 0:
    st.success("✅ Solution optimale — aucun doublon !")
else:
    zero_possible = table_size <= n_t
    st.warning(
        f"⚠️ {doublons} doublon(s). "
        f"{'Inévitables pour ce scénario.' if not zero_possible else 'Essayez de relancer.'}"
    )

if obl_non_respectees:
    st.warning(
        f"⚠️ Obligation(s) non respectée(s) faute de place : "
        f"{', '.join(obl_non_respectees)}. "
        f"L'algo a privilégié 0 doublon. "
        f"Relancez pour tenter une autre combinaison."
    )
elif obligation_pairs:
    st.success("✅ Toutes les obligations sont respectées.")

            df_total = pd.concat(solution)
            csv = df_total.to_csv(index=False).encode('utf-8-sig')
            st.download_button("📥 Télécharger CSV", csv, "planning.csv", "text/csv")

            tabs = st.tabs([f"Rotation {i + 1}" for i in range(n_rounds)])
            for i, tab in enumerate(tabs):
                with tab:
                    df_round = solution[i].sort_values("Table")
                    for table_num in sorted(df_round["Table"].unique()):
                        membres = df_round[df_round["Table"] == table_num]["Participant"].tolist()
                        st.write(f"🪑 **Table {table_num}** : {' • '.join(membres)}")
        else:
            st.error("❌ Impossible de trouver une solution. Vérifiez vos contraintes d'exclusion.")
else:
    st.button("🚀 Générer la solution", disabled=True)
