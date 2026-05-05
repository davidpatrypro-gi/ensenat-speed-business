import streamlit as st
import pandas as pd
import math
import random
import math as _m
import json
from collections import defaultdict


# --- GÉNÉRATION PAGE WEB QR CODE ---
def generate_lookup_html(solution, participants, n_rounds, event_name="Speed Business"):
    data = {}
    for name in participants:
        tables = []
        for r in range(n_rounds):
            df = solution[r]
            row = df[df["Participant"] == name]
            tables.append(int(row["Table"].values[0]) if len(row) > 0 else "?")
        data[name] = tables

    data_json = json.dumps(data, ensure_ascii=False)
    rounds_json = json.dumps(list(range(1, n_rounds + 1)))

    return f"""<!DOCTYPE html>
<html lang="fr">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0">
<title>{event_name} — Mes tables</title>
<style>
  *, *::before, *::after {{ box-sizing: border-box; margin: 0; padding: 0; }}
  :root {{
    --bg: #0a0a0f; --surface: #13131a; --card: #1c1c26; --border: #2a2a3a;
    --gold: #c9a84c; --gold-dim: #8a6e2f; --text: #f0eee8; --muted: #7a7a8a;
    --radius: 16px; --radius-sm: 10px;
  }}
  html {{ scroll-behavior: smooth; }}
  body {{ background: var(--bg); color: var(--text); font-family: 'Georgia','Times New Roman',serif; min-height: 100vh; padding-bottom: 60px; }}
  .header {{ background: linear-gradient(160deg,#13131a 0%,#0d0d14 100%); border-bottom: 1px solid var(--border); padding: 36px 24px 28px; text-align: center; position: relative; overflow: hidden; }}
  .header::before {{ content:''; position:absolute; inset:0; background:radial-gradient(ellipse 80% 60% at 50% -10%,rgba(201,168,76,.12) 0%,transparent 70%); pointer-events:none; }}
  .header-eyebrow {{ font-family:'Courier New',monospace; font-size:11px; letter-spacing:.25em; text-transform:uppercase; color:var(--gold); margin-bottom:10px; }}
  .header-title {{ font-size:clamp(26px,7vw,42px); font-weight:normal; letter-spacing:-.02em; line-height:1.1; }}
  .header-sub {{ margin-top:8px; font-size:14px; color:var(--muted); font-style:italic; }}
  .search-wrap {{ padding:28px 20px 16px; max-width:540px; margin:0 auto; }}
  .search-label {{ display:block; font-family:'Courier New',monospace; font-size:10px; letter-spacing:.2em; text-transform:uppercase; color:var(--gold); margin-bottom:10px; }}
  .search-box {{ position:relative; }}
  .search-icon {{ position:absolute; left:16px; top:50%; transform:translateY(-50%); color:var(--muted); font-size:18px; pointer-events:none; }}
  #searchInput {{ width:100%; padding:16px 16px 16px 46px; background:var(--surface); border:1px solid var(--border); border-radius:var(--radius); color:var(--text); font-family:'Georgia',serif; font-size:17px; outline:none; transition:border-color .2s,box-shadow .2s; -webkit-appearance:none; }}
  #searchInput::placeholder {{ color:var(--muted); }}
  #searchInput:focus {{ border-color:var(--gold-dim); box-shadow:0 0 0 3px rgba(201,168,76,.12); }}
  .results {{ max-width:540px; margin:0 auto; padding:0 20px; }}
  .result-item {{ display:flex; align-items:center; justify-content:space-between; padding:14px 18px; background:var(--surface); border:1px solid var(--border); border-radius:var(--radius-sm); margin-bottom:8px; cursor:pointer; transition:border-color .15s,background .15s; -webkit-tap-highlight-color:transparent; }}
  .result-item:hover,.result-item:active {{ border-color:var(--gold-dim); background:var(--card); }}
  .result-name {{ font-size:16px; }}
  .result-arrow {{ color:var(--gold); font-size:18px; }}
  .no-result {{ text-align:center; color:var(--muted); font-style:italic; padding:24px 0; font-size:15px; }}
  .hint {{ text-align:center; color:var(--muted); font-size:13px; padding:16px 0 0; font-style:italic; }}
  .detail {{ display:none; max-width:540px; margin:0 auto; padding:0 20px; animation:fadeUp .25s ease; }}
  .detail.visible {{ display:block; }}
  @keyframes fadeUp {{ from {{ opacity:0; transform:translateY(12px); }} to {{ opacity:1; transform:translateY(0); }} }}
  .detail-header {{ display:flex; align-items:center; gap:12px; margin-bottom:20px; }}
  .back-btn {{ background:var(--surface); border:1px solid var(--border); border-radius:8px; color:var(--gold); font-size:18px; padding:6px 12px; cursor:pointer; line-height:1; -webkit-tap-highlight-color:transparent; }}
  .detail-name {{ font-size:clamp(20px,5vw,26px); font-weight:normal; flex:1; }}
  .rotation-cards {{ display:grid; gap:14px; }}
  .rotation-card {{ background:var(--card); border:1px solid var(--border); border-radius:var(--radius); padding:20px 24px; display:flex; align-items:center; justify-content:space-between; position:relative; overflow:hidden; animation:fadeUp .3s ease both; }}
  .rotation-card:nth-child(1){{animation-delay:.03s}}.rotation-card:nth-child(2){{animation-delay:.08s}}.rotation-card:nth-child(3){{animation-delay:.13s}}.rotation-card:nth-child(4){{animation-delay:.18s}}.rotation-card:nth-child(5){{animation-delay:.23s}}.rotation-card:nth-child(6){{animation-delay:.28s}}
  .rotation-card::before {{ content:''; position:absolute; left:0; top:0; bottom:0; width:3px; background:var(--gold); opacity:.6; }}
  .card-left {{ display:flex; flex-direction:column; gap:2px; }}
  .card-rotation-label,.card-table-label {{ font-family:'Courier New',monospace; font-size:10px; letter-spacing:.18em; text-transform:uppercase; color:var(--muted); }}
  .card-table-label {{ color:var(--gold); display:block; margin-bottom:2px; }}
  .card-rotation-num {{ font-size:18px; }}
  .card-table {{ text-align:right; }}
  .card-table-num {{ font-size:clamp(36px,10vw,52px); font-weight:normal; line-height:1; color:var(--gold); letter-spacing:-.03em; }}
  .footer {{ text-align:center; padding:40px 20px 20px; color:var(--muted); font-size:12px; font-style:italic; }}
</style>
</head>
<body>
<header class="header">
  <p class="header-eyebrow">Planning de tables</p>
  <h1 class="header-title">{event_name}</h1>
  <p class="header-sub">{n_rounds} rotations &nbsp;&middot;&nbsp; Trouvez votre nom</p>
</header>
<div class="search-wrap">
  <label class="search-label" for="searchInput">Recherchez votre nom</label>
  <div class="search-box">
    <span class="search-icon">&#128269;</span>
    <input type="text" id="searchInput" placeholder="Ex : Marie Dupont&hellip;"
           autocomplete="off" autocorrect="off" autocapitalize="words" spellcheck="false">
  </div>
</div>
<div class="results" id="resultsList"></div>
<div class="detail" id="detail"></div>
<footer class="footer">Speed Business Optimizer</footer>
<script>
const DATA={data_json};
const ROUNDS={rounds_json};
const names=Object.keys(DATA);
const input=document.getElementById('searchInput');
const resList=document.getElementById('resultsList');
const detail=document.getElementById('detail');
function renderList(query){{
  detail.classList.remove('visible');
  const q=query.trim().toLowerCase();
  if(!q){{resList.innerHTML='<p class="hint">Tapez les premi&egrave;res lettres de votre nom ou pr&eacute;nom</p>';return;}}
  const matched=names.filter(n=>n.toLowerCase().includes(q));
  if(!matched.length){{resList.innerHTML='<p class="no-result">Aucun participant trouv&eacute;</p>';return;}}
  if(matched.length===1){{showDetail(matched[0]);return;}}
  resList.innerHTML=matched.map(name=>'<div class="result-item" onclick="showDetail(\''+name.replace(/\\/g,'\\\\').replace(/'/g,"\\'")+'\')">'+'<span class="result-name">'+name+'</span><span class="result-arrow">&rsaquo;</span></div>').join('');
}}
function showDetail(name){{
  resList.innerHTML='';
  const tables=DATA[name];
  const cards=ROUNDS.map((r,i)=>'<div class="rotation-card"><div class="card-left"><span class="card-rotation-label">Rotation</span><span class="card-rotation-num">'+r+'</span></div><div class="card-table"><span class="card-table-label">Table</span><span class="card-table-num">'+tables[i]+'</span></div></div>').join('');
  detail.innerHTML='<div class="detail-header"><button class="back-btn" onclick="backToSearch()">&larr;</button><h2 class="detail-name">'+name+'</h2></div><div class="rotation-cards">'+cards+'</div>';
  detail.classList.add('visible');
  detail.scrollIntoView({{behavior:'smooth',block:'start'}});
}}
function backToSearch(){{
  detail.classList.remove('visible');
  resList.innerHTML='';
  input.value='';
  input.focus();
}}
input.addEventListener('input', () => renderList(input.value));
input.addEventListener('keyup', (e) => {{
  if (e.key === 'Enter') {{
    const matched = names.filter(n => n.toLowerCase().includes(input.value.trim().toLowerCase()));
    if (matched.length === 1) showDetail(matched[0]);
  }}
}});
resList.innerHTML='<p class="hint">Tapez les premi&egrave;res lettres de votre nom ou pr&eacute;nom</p>';
</script>
</body>
</html>"""


# --- DIAGNOSTIC ---
def diagnose(participants, max_per_table, n_rounds, exclusion_groups, obligation_pairs):
    n_p = len(participants)
    n_t = math.ceil(n_p / max_per_table)
    table_size = n_p / n_t
    problems = []
    warnings = []

    if n_p < 2:
        problems.append("❌ Il faut au moins 2 participants.")
        return problems, warnings

    if n_rounds >= n_t:
        problems.append(
            f"❌ Anti-stagnation impossible : {n_rounds} rotations pour seulement {n_t} table(s). "
            f"→ Réduisez à {n_t - 1} rotation(s) max, ou augmentez le nombre de tables."
        )

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

    for pair in obligation_pairs:
        if len(pair) < 2:
            continue
        a, b = pair[0].strip(), pair[1].strip()
        for group in exclusion_groups:
            g = [x.strip() for x in group]
            if a in g and b in g:
                problems.append(
                    f"❌ Contradiction : {a} et {b} doivent se rencontrer (obligation) "
                    f"mais ne peuvent jamais se croiser (exclusion)."
                )

    for group in exclusion_groups:
        g = [x.strip() for x in group if x.strip() in all_names]
        if len(g) > n_t:
            problems.append(
                f"❌ Exclusion impossible : le groupe [{', '.join(g)}] contient {len(g)} personnes "
                f"mais il n'y a que {n_t} table(s). "
                f"→ Augmentez le nombre de tables ou réduisez le groupe."
            )

    if table_size > n_t:
        total_m = int(table_size * (table_size - 1) / 2 * n_t * n_rounds)
        total_p = n_p * (n_p - 1) // 2
        min_doublons = max(0, total_m - total_p)
        warnings.append(
            f"⚠️ Doublons inévitables : avec {n_t} table(s) de {table_size:.0f} personnes, "
            f"minimum {min_doublons} doublon(s) quoi qu'il arrive. "
            f"→ Pour 0 doublon : passez à {n_t + 1} tables."
        )
    else:
        total_m = int(table_size * (table_size - 1) / 2 * n_t * n_rounds)
        total_p = n_p * (n_p - 1) // 2
        if total_m > total_p:
            warnings.append(
                f"⚠️ Trop de rotations : {n_rounds} rotations génèrent {total_m} rencontres "
                f"pour seulement {total_p} paires possibles. "
                f"→ Réduisez à {math.floor(total_p / (total_m / n_rounds))} rotation(s) pour 0 doublon."
            )

    return problems, warnings


# --- ALGORITHME AMÉLIORÉ ---
def solve_speed_business(participants, max_per_table, n_rounds, exclusion_groups, obligation_pairs):
    n_p = len(participants)
    n_t = math.ceil(n_p / max_per_table)
    target = [n_p // n_t + (1 if t < n_p % n_t else 0) for t in range(n_t)]

    # ── Précomputation des contraintes ──────────────────────────────────────
    excl_sets = [frozenset(i for i, name in enumerate(participants) if name in g)
                 for g in exclusion_groups if sum(1 for p in participants if p in g) >= 2]
    excl_for = defaultdict(list)
    for s in excl_sets:
        for p in s:
            excl_for[p].append(s)

    obl_idx = []
    for pair in obligation_pairs:
        if len(pair) < 2:
            continue
        a, b = pair[0].strip(), pair[1].strip()
        if a in participants and b in participants:
            ia, ib = participants.index(a), participants.index(b)
            obl_idx.append((min(ia, ib), max(ia, ib)))
    # Déduplique et indexe pour lookup O(1)
    obl_idx = list(set(obl_idx))
    obl_set = set(obl_idx)

    # ── Fonctions utilitaires ────────────────────────────────────────────────
    def build_m(plan):
        m = [[0] * n_p for _ in range(n_p)]
        for rnd in plan:
            by_t = defaultdict(list)
            for p in range(n_p):
                by_t[rnd[p]].append(p)
            for members in by_t.values():
                for i in range(len(members)):
                    for j in range(i + 1, len(members)):
                        m[members[i]][members[j]] += 1
                        m[members[j]][members[i]] += 1
        return m

    def count_d(m):
        # Total des rencontres en excès (doublons = rencontres au-delà de 1)
        return sum(max(0, m[i][j] - 1) for i in range(n_p) for j in range(i + 1, n_p))

    def count_obl_miss(m):
        # Nombre d'obligations non satisfaites
        return sum(1 for a, b in obl_idx if m[a][b] == 0)

    def excl_ok(asgn, p, t):
        for s in excl_for[p]:
            for other in s:
                if other != p and asgn[other] == t:
                    return False
        return True

    def stag_ok(plan, r, p, t):
        # Anti-stagnation : pas la même table deux rotations de suite
        if r > 0 and plan[r - 1][p] == t:
            return False
        if r < n_rounds - 1 and plan[r + 1][p] == t:
            return False
        return True

    # ── Greedy orientée obligations ──────────────────────────────────────────
    # Amélioration : les participants avec des obligations non satisfaites
    # sont placés en priorité, et un bonus attire leurs partenaires obligatoires.
    def make_greedy():
        meet = [[0] * n_p for _ in range(n_p)]
        plan = []

        for r in range(n_rounds):
            tc = [0] * n_t
            asgn = [-1] * n_p
            prev = plan[r - 1] if r > 0 else None

            # Priorité aux participants avec le plus d'obligations non satisfaites
            unmet_count = {p: 0 for p in range(n_p)}
            for a, b in obl_idx:
                if meet[a][b] == 0:
                    unmet_count[a] += 1
                    unmet_count[b] += 1

            order = sorted(range(n_p), key=lambda p: (-unmet_count[p], random.random()))

            for p in order:
                valid = [t for t in range(n_t)
                         if tc[t] < target[t]
                         and (prev is None or t != prev[p])
                         and excl_ok(asgn, p, t)]
                if not valid:
                    # Relâcher anti-stagnation en dernier recours
                    valid = [t for t in range(n_t)
                             if tc[t] < target[t] and excl_ok(asgn, p, t)]
                if not valid:
                    return None

                def tbl_cost(t):
                    # Pénalité : rencontres déjà vues
                    cost = sum(meet[p][q] * 2 for q in range(n_p) if asgn[q] == t)
                    # Bonus : réunir des paires obligatoires jamais encore ensemble
                    for q in range(n_p):
                        if asgn[q] == t and (min(p, q), max(p, q)) in obl_set and meet[p][q] == 0:
                            cost -= 20
                    return cost

                asgn[p] = min(valid, key=tbl_cost)
                tc[asgn[p]] += 1

            by_t = defaultdict(list)
            for p in range(n_p):
                by_t[asgn[p]].append(p)
            for members in by_t.values():
                for i in range(len(members)):
                    for j in range(i + 1, len(members)):
                        meet[members[i]][members[j]] += 1
                        meet[members[j]][members[i]] += 1
            plan.append(asgn)
        return plan

    # ── Recuit simulé (SA) amélioré ──────────────────────────────────────────
    #
    # Améliorations vs version originale :
    # 1. Bug corrigé : delta doublons correct pour m >= 3
    #    (original : delta=0 au lieu de -1 pour m=3)
    # 2. Delta obligations incrémental dans le SA
    #    (original : obligations seulement vérifiées globalement à la fin)
    # 3. Pénalité proportionnelle : obl_miss * 5000 (original : 0 ou 5000 binaire)
    # 4. Reheat adaptatif si bloqué dans un minimum local
    # 5. Or-opt : déplacer une seule personne (utile pour tables de tailles inégales)
    # 6. Correction de dérive périodique des compteurs incrémentaux

    best_plan, best_score = None, float('inf')

    for attempt in range(30):
        plan = make_greedy()
        if not plan:
            continue

        m = build_m(plan)
        d = count_d(m)
        obl_miss = count_obl_miss(m)
        score = d * 1000 + obl_miss * 5000

        T = 5.0       # Température initiale (unités : équivalents-doublons)
        T_min = 5e-4
        n_steps = 200_000
        cooling = (T_min / T) ** (1.0 / n_steps)

        no_improve = 0
        best_local = score
        best_local_plan = [list(rr) for rr in plan]

        for step in range(n_steps):
            T *= cooling

            # ── Reheat adaptatif ─────────────────────────────────────────────
            # Si aucune amélioration depuis 20 000 étapes, on réchauffe
            if no_improve >= 20_000:
                T = min(T * 8, 3.0)
                no_improve = 0

            # ── Correction de dérive périodique ──────────────────────────────
            # Recalcul exact tous les 20 000 pas pour éviter accumulation d'erreurs
            if step % 20_000 == 0:
                d = count_d(m)
                obl_miss = count_obl_miss(m)
                score = d * 1000 + obl_miss * 5000

            r = random.randint(0, n_rounds - 1)

            # ── Choix du type de mouvement ───────────────────────────────────
            if random.random() < 0.85:
                # ── Mouvement 1 : 2-swap ──────────────────────────────────────
                p1, p2 = random.sample(range(n_p), 2)
                t1, t2 = plan[r][p1], plan[r][p2]
                if t1 == t2:
                    continue

                plan[r][p1] = t2
                plan[r][p2] = t1

                if not (stag_ok(plan, r, p1, t2) and stag_ok(plan, r, p2, t1)
                        and excl_ok(plan[r], p1, t2) and excl_ok(plan[r], p2, t1)):
                    plan[r][p1] = t1
                    plan[r][p2] = t2
                    continue

                at1 = [q for q in range(n_p) if q not in (p1, p2) and plan[r][q] == t1]
                at2 = [q for q in range(n_p) if q not in (p1, p2) and plan[r][q] == t2]

                # ── Delta doublons (CORRIGÉ) ──────────────────────────────────
                # Règle : perte d'une rencontre réduit l'excès si m >= 2
                #          gain d'une rencontre augmente l'excès si m >= 1
                # Bug original : pour m=3, donnait delta=0 au lieu de -1
                delta_d = 0
                for p3 in at1:
                    if m[p1][p3] >= 2: delta_d -= 1   # p1 quitte t1 → perte de doublon
                    if m[p2][p3] >= 1: delta_d += 1   # p2 rejoint t1 → nouveau doublon potentiel
                for p3 in at2:
                    if m[p1][p3] >= 1: delta_d += 1   # p1 rejoint t2 → nouveau doublon potentiel
                    if m[p2][p3] >= 2: delta_d -= 1   # p2 quitte t2 → perte de doublon

                # ── Delta obligations (NOUVEAU) ───────────────────────────────
                # p1 quitte t1 (perd la rencontre avec les membres de at1 dans ce round)
                # p1 rejoint t2 (gagne la rencontre avec les membres de at2 dans ce round)
                # p2 fait le chemin inverse
                delta_obl = 0
                for p3 in at1:
                    # p1 perd une rencontre avec p3
                    if (min(p1, p3), max(p1, p3)) in obl_set and m[p1][p3] == 1:
                        delta_obl += 1   # obligation perdue (seule rencontre disparaît)
                    # p2 gagne une rencontre avec p3
                    if (min(p2, p3), max(p2, p3)) in obl_set and m[p2][p3] == 0:
                        delta_obl -= 1   # obligation nouvellement satisfaite
                for p3 in at2:
                    # p1 gagne une rencontre avec p3
                    if (min(p1, p3), max(p1, p3)) in obl_set and m[p1][p3] == 0:
                        delta_obl -= 1   # obligation nouvellement satisfaite
                    # p2 perd une rencontre avec p3
                    if (min(p2, p3), max(p2, p3)) in obl_set and m[p2][p3] == 1:
                        delta_obl += 1   # obligation perdue

                delta_score = delta_d * 1000 + delta_obl * 5000

                if delta_score <= 0 or random.random() < _m.exp(-delta_score / max(T * 1000, 1e-9)):
                    # Accepter : mise à jour incrémentale de la matrice
                    for p3 in at1:
                        m[p1][p3] -= 1; m[p3][p1] -= 1
                        m[p2][p3] += 1; m[p3][p2] += 1
                    for p3 in at2:
                        m[p1][p3] += 1; m[p3][p1] += 1
                        m[p2][p3] -= 1; m[p3][p2] -= 1
                    d += delta_d
                    obl_miss += delta_obl
                    score = d * 1000 + obl_miss * 5000
                    if score < best_local:
                        best_local = score
                        best_local_plan = [list(rr) for rr in plan]
                        no_improve = 0
                    else:
                        no_improve += 1
                else:
                    plan[r][p1] = t1
                    plan[r][p2] = t2
                    no_improve += 1

            else:
                # ── Mouvement 2 : or-opt (NOUVEAU) ───────────────────────────
                # Déplace une seule personne vers une table moins remplie.
                # Utile quand les tables ont des tailles inégales.
                tc_r = [0] * n_t
                for q in range(n_p):
                    tc_r[plan[r][q]] += 1

                p1 = random.randint(0, n_p - 1)
                t1 = plan[r][p1]
                # Table de destination : doit avoir de la place (selon target)
                dests = [t for t in range(n_t) if t != t1 and tc_r[t] < target[t]]
                if not dests:
                    continue
                t2 = random.choice(dests)

                plan[r][p1] = t2
                if not (stag_ok(plan, r, p1, t2) and excl_ok(plan[r], p1, t2)):
                    plan[r][p1] = t1
                    continue

                # at1 : membres restant en t1 ; at2 : membres déjà en t2
                at1 = [q for q in range(n_p) if q != p1 and plan[r][q] == t1]
                at2 = [q for q in range(n_p) if q != p1 and plan[r][q] == t2]

                delta_d = 0
                for p3 in at1:
                    if m[p1][p3] >= 2: delta_d -= 1
                for p3 in at2:
                    if m[p1][p3] >= 1: delta_d += 1

                delta_obl = 0
                for p3 in at1:
                    if (min(p1, p3), max(p1, p3)) in obl_set and m[p1][p3] == 1:
                        delta_obl += 1
                for p3 in at2:
                    if (min(p1, p3), max(p1, p3)) in obl_set and m[p1][p3] == 0:
                        delta_obl -= 1

                delta_score = delta_d * 1000 + delta_obl * 5000

                if delta_score <= 0 or random.random() < _m.exp(-delta_score / max(T * 1000, 1e-9)):
                    for p3 in at1:
                        m[p1][p3] -= 1; m[p3][p1] -= 1
                    for p3 in at2:
                        m[p1][p3] += 1; m[p3][p1] += 1
                    d += delta_d
                    obl_miss += delta_obl
                    score = d * 1000 + obl_miss * 5000
                    if score < best_local:
                        best_local = score
                        best_local_plan = [list(rr) for rr in plan]
                        no_improve = 0
                    else:
                        no_improve += 1
                else:
                    plan[r][p1] = t1
                    no_improve += 1

            if d == 0 and obl_miss == 0:
                break

        if best_local < best_score:
            best_score = best_local
            best_plan = best_local_plan

        if best_score == 0:
            break

    if best_plan is None:
        return None, 0

    m_final = build_m(best_plan)
    res = [pd.DataFrame([
        {"Participant": participants[p], "Table": best_plan[r][p] + 1, "Rotation": r + 1}
        for p in range(n_p)]) for r in range(n_rounds)]
    return res, count_d(m_final)


# --- INTERFACE ---
st.set_page_config(page_title="Speed Business Optimizer", layout="wide")
st.title("🛡️ Speed Business Optimizer")

with st.sidebar:
    st.header("⚙️ Configuration")
    event_name = st.text_input("Nom de l'événement", "Speed Business")
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

if not problems:
    if st.button("🚀 Générer la solution"):
        with st.spinner("Optimisation en cours..."):
            solution, doublons = solve_speed_business(
                participants, max_per_table, n_rounds, exclusion_groups, obligation_pairs)
        if solution:
            st.session_state['solution']      = solution
            st.session_state['doublons']      = doublons
            st.session_state['snap_parts']    = list(participants)
            st.session_state['snap_rounds']   = int(n_rounds)
            st.session_state['snap_mpt']      = int(max_per_table)
            st.session_state['snap_event']    = event_name
            st.session_state['snap_obl_pairs']= list(obligation_pairs)
        else:
            st.session_state.pop('solution', None)

    if st.session_state.get('solution'):
        solution      = st.session_state['solution']
        doublons      = st.session_state['doublons']
        participants  = st.session_state['snap_parts']
        n_rounds      = st.session_state['snap_rounds']
        max_per_table = st.session_state['snap_mpt']
        event_name    = st.session_state['snap_event']
        obligation_pairs = st.session_state['snap_obl_pairs']
        n_t           = math.ceil(len(participants) / max_per_table)
        table_size    = len(participants) / n_t

        if True:
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

            df_total_check = pd.concat(solution)
            obl_non_respectees = []
            for pair in obligation_pairs:
                if len(pair) < 2:
                    continue
                a, b = pair[0].strip(), pair[1].strip()
                met = False
                for r in range(1, n_rounds + 1):
                    df_r = df_total_check[df_total_check["Rotation"] == r]
                    if len(df_r[df_r["Participant"] == a]) == 0:
                        continue
                    if len(df_r[df_r["Participant"] == b]) == 0:
                        continue
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
                    f"Relancez pour tenter une autre combinaison."
                )
            elif obligation_pairs:
                st.success("✅ Toutes les obligations sont respectées.")

            df_total = pd.concat(solution)
            csv = df_total.to_csv(index=False).encode('utf-8-sig')
            st.markdown("---")
            st.markdown("### 📤 Exports")
            col_dl1, col_dl2 = st.columns(2)
            with col_dl1:
                df_total = pd.concat(solution)
                csv = df_total.to_csv(index=False).encode('utf-8-sig')
                st.download_button("📥 Télécharger CSV", csv, "planning.csv", "text/csv", use_container_width=True)
            with col_dl2:
                html_content = generate_lookup_html(solution, participants, n_rounds, event_name)
                st.download_button("🌐 Page web (QR code)", html_content.encode("utf-8"), "index.html", "text/html", use_container_width=True)
            st.info(
                "💡 **Comment utiliser la page web ?**  \n"
                "1. Téléchargez `planning.html`  \n"
                "2. Glissez-déposez sur **netlify.com/drop** (gratuit, 10 sec)  \n"
                "3. Copiez l\'URL → QR code sur **qrcode-monkey.com**  \n"
                "4. Affichez le QR code à l\'entrée ✅"
            )
            st.markdown("---")
            tabs = st.tabs([f"Rotation {i + 1}" for i in range(n_rounds)])
            for i, tab in enumerate(tabs):
                with tab:
                    df_round = solution[i].sort_values("Table")
                    for table_num in sorted(df_round["Table"].unique()):
                        membres = df_round[df_round["Table"] == table_num]["Participant"].tolist()
                        st.write(f"🪑 **Table {table_num}** : {' • '.join(membres)}")
        else:
            if not st.session_state.get('solution'):
                st.error("❌ Impossible de trouver une solution. Vérifiez vos contraintes d'exclusion.")
else:
    st.button("🚀 Générer la solution", disabled=True)
