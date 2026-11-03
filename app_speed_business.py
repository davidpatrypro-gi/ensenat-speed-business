import streamlit as st
import pandas as pd
import math
import random
import math as _m
import json as _json
from collections import defaultdict


# --- GÉNÉRATION PAGE WEB (3 blocs Webflow + page complète) ---
LOGO_URL   = "https://cdn.prod.website-files.com/6638a4188051fb2366951b27/6720e8e5e3c84be2401830de_logo.svg"
REVIEW_URL = "https://g.page/r/CYk5Jtzqw0HHEAE/review"


def _lookup_css():
    """Bloc 1 — CSS (Head Code Webflow). Ne change jamais."""
    return "\n".join([
        "*,*::before,*::after{box-sizing:border-box;margin:0;padding:0}",
        ":root{--bg:#0a0a0f;--surf:#13131a;--card:#1c1c26;--bord:#2a2a3a;--gold:#cb1d23;--goldd:#9e1519;--txt:#f0eee8;--mut:#7a7a8a;--r:16px}",
        "body{background:var(--bg);color:var(--txt);font-family:Georgia,'Times New Roman',serif;min-height:100vh;padding-bottom:60px}",
        ".hdr{background:linear-gradient(160deg,#13131a,#0d0d14);border-bottom:1px solid var(--bord);padding:36px 24px 28px;text-align:center;position:relative;overflow:hidden}",
        ".hdr::before{content:'';position:absolute;inset:0;background:radial-gradient(ellipse 80% 60% at 50% -10%,rgba(203,29,35,.13) 0%,transparent 70%);pointer-events:none}",
        ".eye{font-family:'Courier New',monospace;font-size:11px;letter-spacing:.25em;text-transform:uppercase;color:var(--gold);margin-bottom:10px}",
        ".ttl{font-size:clamp(26px,7vw,42px);font-weight:normal;letter-spacing:-.02em;line-height:1.1}",
        ".sub{margin-top:8px;font-size:14px;color:var(--mut);font-style:italic}",
        ".wrap{padding:28px 20px 16px;max-width:540px;margin:0 auto}",
        ".lbl-s{display:block;font-family:'Courier New',monospace;font-size:10px;letter-spacing:.2em;text-transform:uppercase;color:var(--gold);margin-bottom:10px}",
        ".row{display:flex;gap:10px}",
        "#inp{flex:1;padding:15px 16px;background:var(--surf);border:1px solid var(--bord);border-radius:var(--r);color:var(--txt);font-family:Georgia,serif;font-size:17px;outline:none;-webkit-appearance:none;min-width:0}",
        "#inp:focus{border-color:var(--goldd);box-shadow:0 0 0 3px rgba(201,168,76,.12)}",
        "#inp::placeholder{color:var(--mut)}",
        "#btn{flex-shrink:0;background:var(--gold);border:none;border-radius:var(--r);color:#ffffff;font-family:'Courier New',monospace;font-size:13px;font-weight:bold;letter-spacing:.06em;padding:0 20px;cursor:pointer}",
        "#btn:active{opacity:.75}",
        "#res,#det{max-width:540px;margin:10px auto 0;padding:0 20px}",
        "#det{display:none}",
        ".hint,.no-result{text-align:center;color:var(--mut);font-style:italic;padding:20px 0;font-size:14px}",
        ".result-item{display:flex;align-items:center;justify-content:space-between;padding:14px 18px;background:var(--surf);border:1px solid var(--bord);border-radius:10px;margin-bottom:8px;cursor:pointer}",
        ".result-item:hover{border-color:var(--goldd);background:var(--card)}",
        ".arr{color:var(--gold);font-size:18px}",
        ".dh{display:flex;align-items:center;gap:12px;margin-bottom:20px}",
        ".back{background:var(--surf);border:1px solid var(--bord);border-radius:8px;color:var(--gold);font-size:18px;padding:6px 12px;cursor:pointer;line-height:1}",
        ".dname{font-size:clamp(20px,5vw,26px);font-weight:normal;flex:1}",
        ".cards{display:grid;gap:14px}",
        ".card{background:var(--card);border:1px solid var(--bord);border-radius:var(--r);padding:20px 24px;display:flex;align-items:center;justify-content:space-between;position:relative;overflow:hidden}",
        ".card::before{content:'';position:absolute;left:0;top:0;bottom:0;width:3px;background:var(--gold)}",
        ".cl{flex:1}",
        ".lbl{display:block;font-family:'Courier New',monospace;font-size:10px;letter-spacing:.18em;text-transform:uppercase;color:var(--mut)}",
        ".gold{color:var(--gold)!important}",
        ".rnum{font-size:18px}",
        ".ct{text-align:right}",
        ".tnum{display:block;font-size:clamp(38px,10vw,54px);font-weight:normal;line-height:1;color:var(--gold);letter-spacing:-.03em}",
        ".foot{text-align:center;padding:40px 20px 0;color:var(--mut);font-size:12px;font-style:italic}",
    ])


def _lookup_body(event_name, n_rounds):
    """Bloc 2 — HTML (Embed Webflow). Ne change jamais : le titre et le nombre
    de rotations sont mis à jour par le JS (ids ev-ttl / ev-sub)."""
    return "\n".join([
        "<header class='hdr'>",
        "  <img src='" + LOGO_URL + "'",
        "       alt='Ensenat Coaching' style='height:56px;margin-bottom:20px;display:block;margin-left:auto;margin-right:auto'>",
        "  <p class='eye'>Planning de tables</p>",
        "  <h1 class='ttl' id='ev-ttl'>" + event_name + "</h1>",
        "  <p class='sub' id='ev-sub'>" + str(n_rounds) + " rotations &middot; Trouvez votre nom</p>",
        "</header>",
        "<div class='wrap'>",
        "  <label class='lbl-s' for='inp'>Recherchez votre nom</label>",
        "  <div class='row'>",
        "    <input type='text' id='inp' placeholder='Ex : Marie ou Dupont…' autocomplete='off' spellcheck='false'>",
        "    <button id='btn' onclick='doSearch()'>Rechercher</button>",
        "  </div>",
        "</div>",
        "<div id='res'></div>",
        "<div id='det'></div>",
        "<p class='foot' style='font-size:15px;'><a href='" + REVIEW_URL + "' target='_blank' style='color:var(--mut);text-decoration:underline;'>Laissez nous un avis</a></p>",
    ])


def _lookup_js(solution, participants, n_rounds, event_name):
    """Bloc 3 — JS + données (Before </body> Webflow). Change à chaque événement."""
    data = {}
    for name in participants:
        tables = []
        for r in range(n_rounds):
            df = solution[r]
            row = df[df["Participant"] == name]
            tables.append(int(row["Table"].values[0]) if len(row) > 0 else 0)
        data[name] = tables

    data_js   = _json.dumps(data, ensure_ascii=True, separators=(',', ':'))
    rounds_js = _json.dumps(list(range(1, n_rounds + 1)), separators=(',', ':'))
    event_js  = _json.dumps(event_name, ensure_ascii=True)

    js_lines = [
        "var EVENT=" + event_js + ";",
        "var DATA=" + data_js + ";",
        "var ROUNDS=" + rounds_js + ";",
        "var names=Object.keys(DATA);",
        "(function(){",
        "  var t=document.getElementById('ev-ttl');if(t)t.textContent=EVENT;",
        "  var s=document.getElementById('ev-sub');if(s)s.textContent=ROUNDS.length+' rotations · Trouvez votre nom';",
        "})();",
        "function doSearch(){",
        "  var q=document.getElementById('inp').value.trim().toLowerCase();",
        "  var res=document.getElementById('res');",
        "  var det=document.getElementById('det');",
        "  det.style.display='none';",
        "  if(!q){res.innerHTML='<p class=\"hint\">Tapez votre prénom ou votre nom</p>';return;}",
        "  var found=[];",
        "  for(var i=0;i<names.length;i++){",
        "    var words=q.split(' ');",
        "    for(var w=0;w<words.length;w++){",
        "      if(words[w]&&names[i].toLowerCase().indexOf(words[w])>=0){found.push(names[i]);break;}",
        "    }",
        "  }",
        "  if(!found.length){res.innerHTML='<p class=\"no-result\">Aucun résultat &mdash; vérifiez l’orthographe</p>';return;}",
        "  if(found.length===1){showDetail(found[0]);return;}",
        "  var html='';",
        "  for(var j=0;j<found.length;j++){",
        "    var safe=found[j].replace(/&/g,'&amp;').replace(/\"/g,'&quot;');",
        "    html+='<div class=\"result-item\" data-n=\"'+safe+'\" onclick=\"showDetail(this.dataset.n)\">'",
        "         +'<span>'+found[j]+'</span><span class=\"arr\">&rsaquo;</span></div>';",
        "  }",
        "  res.innerHTML=html;",
        "}",
        "function showDetail(name){",
        "  document.getElementById('res').innerHTML='';",
        "  var tables=DATA[name];if(!tables)return;",
        "  var cards='';",
        "  for(var i=0;i<ROUNDS.length;i++){",
        "    cards+='<div class=\"card\"><div class=\"cl\"><span class=\"lbl\">Rotation</span>'",
        "          +'<span class=\"rnum\">'+ROUNDS[i]+'</span></div>'",
        "          +'<div class=\"ct\"><span class=\"lbl gold\">Table</span>'",
        "          +'<span class=\"tnum\">'+tables[i]+'</span></div></div>';",
        "  }",
        "  var det=document.getElementById('det');",
        "  det.innerHTML='<div class=\"dh\"><button class=\"back\" onclick=\"goBack()\">&larr;</button>'",
        "               +'<h2 class=\"dname\">'+name+'</h2></div><div class=\"cards\">'+cards+'</div>';",
        "  det.style.display='block';window.scrollTo(0,0);",
        "}",
        "function goBack(){",
        "  document.getElementById('det').style.display='none';",
        "  document.getElementById('res').innerHTML='';",
        "  document.getElementById('inp').value='';",
        "  document.getElementById('inp').focus();",
        "}",
        "document.getElementById('inp').addEventListener('input',function(){doSearch();});",
        "document.getElementById('inp').addEventListener('keyup',function(e){if(e.key==='Enter')doSearch();});",
        "document.getElementById('res').innerHTML='<p class=\"hint\">Tapez votre prénom ou votre nom</p>';",
    ]
    return "\n".join(js_lines)


def generate_webflow_blocks(solution, participants, n_rounds, event_name="Speed Business"):
    """Les 3 blocs prêts à coller dans Webflow (Paramètres de la page → Custom code)."""
    return {
        "head":   "<style>\n" + _lookup_css() + "\n</style>",
        "embed":  _lookup_body(event_name, n_rounds),
        "footer": "<script>\n" + _lookup_js(solution, participants, n_rounds, event_name) + "\n</script>",
    }


def generate_lookup_html(solution, participants, n_rounds, event_name="Speed Business"):
    """Page complète autonome (index.html) = les 3 blocs assemblés."""
    b = generate_webflow_blocks(solution, participants, n_rounds, event_name)
    parts = [
        "<!DOCTYPE html>",
        "<html lang='fr'>",
        "<head>",
        "<meta charset='UTF-8'>",
        "<meta name='viewport' content='width=device-width,initial-scale=1.0,maximum-scale=1.0'>",
        "<title>" + event_name + " — Mes tables</title>",
        b["head"],
        "</head>",
        "<body>",
        b["embed"],
        b["footer"],
        "</body>",
        "</html>",
    ]
    return "\n".join(parts)



# --- DÉDUPLICATION DES HOMONYMES ---
def deduplicate_names(names):
    """
    Détecte les noms en double et ajoute un suffixe (2), (3)...
    Retourne (liste_dédupliquée, dict_des_renommages).
    """
    from collections import Counter
    count = Counter(names)
    duplicates = {n for n, c in count.items() if c > 1}
    if not duplicates:
        return list(names), {}

    renamed = {}   # ancien_nom_occurrence → nouveau_nom
    seen = {}      # nom → compteur
    result = []
    for n in names:
        if n in duplicates:
            seen[n] = seen.get(n, 0) + 1
            if seen[n] == 1:
                result.append(n)           # premier : on garde l'original
            else:
                new_name = f"{n} ({seen[n]})"
                result.append(new_name)
                renamed[f"{n}__occ{seen[n]}"] = new_name
        else:
            result.append(n)
    return result, renamed

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
    obl_idx = list(set(obl_idx))
    obl_set = set(obl_idx)

    # ── Utilitaires ──────────────────────────────────────────────────────────

    def build_m(plan):
        m = [[0] * n_p for _ in range(n_p)]
        for rnd in plan:
            by_t = defaultdict(list)
            for p in range(n_p): by_t[rnd[p]].append(p)
            for members in by_t.values():
                for i in range(len(members)):
                    for j in range(i + 1, len(members)):
                        m[members[i]][members[j]] += 1
                        m[members[j]][members[i]] += 1
        return m

    def count_d(m):
        return sum(max(0, m[i][j] - 1) for i in range(n_p) for j in range(i + 1, n_p))

    def count_obl_miss(m):
        return sum(1 for a, b in obl_idx if m[a][b] == 0)

    def count_excl_viol(plan):
        """Nombre de paires exclusion qui se retrouvent à la même table."""
        total = 0
        for rnd in plan:
            by_t = defaultdict(list)
            for p in range(n_p): by_t[rnd[p]].append(p)
            for members in by_t.values():
                mset = set(members)
                for s in excl_sets:
                    overlap = s & mset
                    if len(overlap) >= 2:
                        # nombre de paires en violation dans cette table
                        total += len(overlap) * (len(overlap) - 1) // 2
        return total

    def in_same_excl(p, q):
        for s in excl_for[p]:
            if q in s: return True
        return False

    def stag_ok(plan, r, p, t):
        if r > 0 and plan[r - 1][p] == t: return False
        if r < n_rounds - 1 and plan[r + 1][p] == t: return False
        return True

    def excl_ok(asgn, p, t):
        for s in excl_for[p]:
            for other in s:
                if other != p and asgn[other] == t: return False
        return True

    # ── Greedy orientée obligations (exclusions = best effort) ───────────────
    def make_greedy():
        meet = [[0] * n_p for _ in range(n_p)]
        plan = []
        for r in range(n_rounds):
            tc = [0] * n_t
            asgn = [-1] * n_p
            prev = plan[r - 1] if r > 0 else None
            unmet_count = {p: 0 for p in range(n_p)}
            for a, b in obl_idx:
                if meet[a][b] == 0:
                    unmet_count[a] += 1; unmet_count[b] += 1
            order = sorted(range(n_p), key=lambda p: (-unmet_count[p], random.random()))
            for p in order:
                # Priorité 1 : anti-stag + exclusion respectées
                valid = [t for t in range(n_t) if tc[t] < target[t]
                         and (prev is None or t != prev[p]) and excl_ok(asgn, p, t)]
                # Priorité 2 : relâcher anti-stagnation
                if not valid:
                    valid = [t for t in range(n_t) if tc[t] < target[t]
                             and excl_ok(asgn, p, t)]
                # Priorité 3 : relâcher exclusion (JAMAIS les doublons)
                if not valid:
                    valid = [t for t in range(n_t) if tc[t] < target[t]
                             and (prev is None or t != prev[p])]
                # Priorité 4 : relâcher tout sauf capacité
                if not valid:
                    valid = [t for t in range(n_t) if tc[t] < target[t]]
                if not valid: return None

                def tbl_cost(t):
                    cost = sum(meet[p][q] * 2 for q in range(n_p) if asgn[q] == t)
                    for q in range(n_p):
                        if asgn[q] == t and (min(p, q), max(p, q)) in obl_set and meet[p][q] == 0:
                            cost -= 20
                    return cost

                asgn[p] = min(valid, key=tbl_cost)
                tc[asgn[p]] += 1
            by_t = defaultdict(list)
            for p in range(n_p): by_t[asgn[p]].append(p)
            for members in by_t.values():
                for i in range(len(members)):
                    for j in range(i + 1, len(members)):
                        meet[members[i]][members[j]] += 1
                        meet[members[j]][members[i]] += 1
            plan.append(asgn)
        return plan

    # ── Recuit simulé — Hiérarchie : doublons >> exclusions > obligations ────
    #
    # Poids du score :
    #   1 doublon          = 100 000 pts  (priorité absolue)
    #   1 viol. exclusion  =     500 pts  (best effort)
    #   1 oblig. manquée   =   2 000 pts  (best effort)
    #
    # → l'algo préférera toujours violer une exclusion plutôt qu'accepter
    #   un seul doublon, quelles que soient les contraintes.

    W_DUP  = 100_000
    W_EXCL =     500
    W_OBL  =   2_000

    best_plan, best_score = None, float('inf')

    for attempt in range(30):
        plan = make_greedy()
        if not plan: continue

        m = build_m(plan)
        d        = count_d(m)
        obl_miss = count_obl_miss(m)
        excl_v   = count_excl_viol(plan)
        score    = d * W_DUP + excl_v * W_EXCL + obl_miss * W_OBL

        T = 5.0; T_min = 5e-4; n_steps = 200_000
        cooling = (T_min / T) ** (1.0 / n_steps)
        no_improve = 0
        best_local = score
        best_local_plan = [list(rr) for rr in plan]

        for step in range(n_steps):
            T *= cooling
            if no_improve >= 20_000:
                T = min(T * 8, 3.0); no_improve = 0
            if step % 20_000 == 0:
                d        = count_d(m)
                obl_miss = count_obl_miss(m)
                excl_v   = count_excl_viol(plan)
                score    = d * W_DUP + excl_v * W_EXCL + obl_miss * W_OBL

            r = random.randint(0, n_rounds - 1)

            if random.random() < 0.85:
                # ── 2-swap ───────────────────────────────────────────────────
                p1, p2 = random.sample(range(n_p), 2)
                t1, t2 = plan[r][p1], plan[r][p2]
                if t1 == t2: continue
                plan[r][p1] = t2; plan[r][p2] = t1

                # Anti-stagnation : hard (inchangé)
                if not (stag_ok(plan, r, p1, t2) and stag_ok(plan, r, p2, t1)):
                    plan[r][p1] = t1; plan[r][p2] = t2; continue

                at1 = [q for q in range(n_p) if q not in (p1, p2) and plan[r][q] == t1]
                at2 = [q for q in range(n_p) if q not in (p1, p2) and plan[r][q] == t2]

                # Delta doublons
                delta_d = 0
                for p3 in at1:
                    if m[p1][p3] >= 2: delta_d -= 1
                    if m[p2][p3] >= 1: delta_d += 1
                for p3 in at2:
                    if m[p1][p3] >= 1: delta_d += 1
                    if m[p2][p3] >= 2: delta_d -= 1

                # Delta obligations
                delta_obl = 0
                for p3 in at1:
                    if (min(p1,p3),max(p1,p3)) in obl_set and m[p1][p3]==1: delta_obl+=1
                    if (min(p2,p3),max(p2,p3)) in obl_set and m[p2][p3]==0: delta_obl-=1
                for p3 in at2:
                    if (min(p1,p3),max(p1,p3)) in obl_set and m[p1][p3]==0: delta_obl-=1
                    if (min(p2,p3),max(p2,p3)) in obl_set and m[p2][p3]==1: delta_obl+=1

                # Delta exclusions (NOUVEAU — soft constraint)
                delta_excl = 0
                for p3 in at1:
                    if in_same_excl(p1, p3): delta_excl -= 1  # p1 quitte t1
                    if in_same_excl(p2, p3): delta_excl += 1  # p2 rejoint t1
                for p3 in at2:
                    if in_same_excl(p1, p3): delta_excl += 1  # p1 rejoint t2
                    if in_same_excl(p2, p3): delta_excl -= 1  # p2 quitte t2

                delta_score = delta_d * W_DUP + delta_excl * W_EXCL + delta_obl * W_OBL

                if delta_score <= 0 or random.random() < _m.exp(-delta_score / max(T * W_DUP, 1e-9)):
                    for p3 in at1:
                        m[p1][p3]-=1; m[p3][p1]-=1; m[p2][p3]+=1; m[p3][p2]+=1
                    for p3 in at2:
                        m[p1][p3]+=1; m[p3][p1]+=1; m[p2][p3]-=1; m[p3][p2]-=1
                    d+=delta_d; obl_miss+=delta_obl; excl_v+=delta_excl
                    score = d*W_DUP + excl_v*W_EXCL + obl_miss*W_OBL
                    if score < best_local:
                        best_local=score; best_local_plan=[list(rr) for rr in plan]; no_improve=0
                    else: no_improve+=1
                else:
                    plan[r][p1]=t1; plan[r][p2]=t2; no_improve+=1

            else:
                # ── Or-opt ───────────────────────────────────────────────────
                tc_r = [0]*n_t
                for q in range(n_p): tc_r[plan[r][q]]+=1
                p1=random.randint(0,n_p-1); t1=plan[r][p1]
                dests=[t for t in range(n_t) if t!=t1 and tc_r[t]<target[t]]
                if not dests: continue
                t2=random.choice(dests); plan[r][p1]=t2
                if not stag_ok(plan,r,p1,t2): plan[r][p1]=t1; continue
                at1=[q for q in range(n_p) if q!=p1 and plan[r][q]==t1]
                at2=[q for q in range(n_p) if q!=p1 and plan[r][q]==t2]
                delta_d=0
                for p3 in at1:
                    if m[p1][p3]>=2: delta_d-=1
                for p3 in at2:
                    if m[p1][p3]>=1: delta_d+=1
                delta_obl=0
                for p3 in at1:
                    if (min(p1,p3),max(p1,p3)) in obl_set and m[p1][p3]==1: delta_obl+=1
                for p3 in at2:
                    if (min(p1,p3),max(p1,p3)) in obl_set and m[p1][p3]==0: delta_obl-=1
                delta_excl=0
                for p3 in at1:
                    if in_same_excl(p1,p3): delta_excl-=1
                for p3 in at2:
                    if in_same_excl(p1,p3): delta_excl+=1
                delta_score=delta_d*W_DUP+delta_excl*W_EXCL+delta_obl*W_OBL
                if delta_score<=0 or random.random()<_m.exp(-delta_score/max(T*W_DUP,1e-9)):
                    for p3 in at1: m[p1][p3]-=1; m[p3][p1]-=1
                    for p3 in at2: m[p1][p3]+=1; m[p3][p1]+=1
                    d+=delta_d; obl_miss+=delta_obl; excl_v+=delta_excl
                    score=d*W_DUP+excl_v*W_EXCL+obl_miss*W_OBL
                    if score<best_local:
                        best_local=score; best_local_plan=[list(rr) for rr in plan]; no_improve=0
                    else: no_improve+=1
                else:
                    plan[r][p1]=t1; no_improve+=1

            if d==0 and excl_v==0 and obl_miss==0: break

        if best_local < best_score:
            best_score=best_local; best_plan=best_local_plan
        if best_score==0: break

    if best_plan is None: return None, 0, 0, 0
    m_final = build_m(best_plan)
    res = [pd.DataFrame([
        {"Participant": participants[p], "Table": best_plan[r][p]+1, "Rotation": r+1}
        for p in range(n_p)]) for r in range(n_rounds)]
    return res, count_d(m_final), count_excl_viol(best_plan), count_obl_miss(m_final)


# --- INTERFACE ---
st.set_page_config(page_title="Speed Business Optimizer", layout="wide")
st.title("🛡️ Speed Business Optimizer")

with st.sidebar:
    st.header("⚙️ Configuration")
    event_name = st.text_input("Nom de l'événement", "Speed Business")
    raw_names = st.text_area("Participants (un par ligne)",
                             "Jean\nMarie\nPierre\nSophie\nLuc\nJulie\nAntoine\nClara\nEmma\nPaul")
    participants_raw = [n.strip() for n in raw_names.split('\n') if n.strip()]
    participants, homonymes = deduplicate_names(participants_raw)
    n_p = len(participants)
    n_rounds = st.number_input("Nombre de rotations", 1, 10, 4)
    max_per_table = st.number_input("Max personnes par table", 2, 20, 5)
    n_t = math.ceil(n_p / max_per_table)
    table_size = n_p / n_t
    st.info(f"**{n_p} participants | {n_t} tables de {table_size:.0f}**")

if homonymes:
    renamed_display = ", ".join(
        f"**{v}**" for v in sorted(set(homonymes.values()))
    )
    st.warning(
        f"⚠️ Homonymes détectés et renommés automatiquement : {renamed_display}. "
        f"Communiquez leur suffixe aux personnes concernées."
    )

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
            solution, doublons, excl_violations, obl_violations = solve_speed_business(
                participants, max_per_table, n_rounds, exclusion_groups, obligation_pairs)
        if solution:
            st.session_state['solution']       = solution
            st.session_state['doublons']       = doublons
            st.session_state['excl_violations']= excl_violations
            st.session_state['obl_violations'] = obl_violations
            st.session_state['snap_parts']     = list(participants)
            st.session_state['snap_rounds']    = int(n_rounds)
            st.session_state['snap_mpt']       = int(max_per_table)
            st.session_state['snap_event']     = event_name
            st.session_state['snap_obl_pairs'] = list(obligation_pairs)
        else:
            st.session_state.pop('solution', None)

    if st.session_state.get('solution'):
        solution         = st.session_state['solution']
        doublons         = st.session_state['doublons']
        excl_violations  = st.session_state.get('excl_violations', 0)
        obl_violations   = st.session_state.get('obl_violations', 0)
        participants     = st.session_state['snap_parts']
        n_rounds         = st.session_state['snap_rounds']
        max_per_table    = st.session_state['snap_mpt']
        event_name       = st.session_state['snap_event']
        obligation_pairs = st.session_state['snap_obl_pairs']
        n_t              = math.ceil(len(participants) / max_per_table)
        table_size       = len(participants) / n_t

        if True:
            col_a, col_b, col_c, col_d = st.columns(4)
            with col_a:
                st.metric("Doublons", doublons, delta="✅ Optimal" if doublons==0 else None)
            with col_b:
                st.metric("Violations exclusion", excl_violations,
                          delta="✅" if excl_violations==0 else f"⚠️ {excl_violations}")
            with col_c:
                total_m = int(table_size * (table_size - 1) / 2 * n_t * n_rounds)
                n_p_s = len(participants)
                total_p = n_p_s * (n_p_s - 1) // 2
                pct = min(100, round(total_m / total_p * 100))
                st.metric("Couverture max", f"{pct}%")
            with col_d:
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
                st.success("✅ 0 doublon — priorité absolue respectée.")
            else:
                zero_possible = table_size <= n_t
                st.error(
                    f"❌ {doublons} doublon(s). "
                    f"{'Inévitables mathématiquement pour ce scénario.' if not zero_possible else 'Relancez pour tenter mieux.'}"
                )
            if excl_violations > 0:
                st.warning(
                    f"⚠️ {excl_violations} violation(s) d'exclusion : l'algo a préféré respecter "
                    f"la règle des 0 doublons. Relancez pour tenter de réduire ce chiffre."
                )
            elif exclusion_groups:
                st.success("✅ Toutes les exclusions sont respectées.")

            if obl_non_respectees:
                st.warning(
                    f"⚠️ Obligation(s) non respectée(s) faute de place : "
                    f"{', '.join(obl_non_respectees)}. "
                    f"Relancez pour tenter une autre combinaison."
                )
            elif obligation_pairs:
                st.success("✅ Toutes les obligations sont respectées.")

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
            st.caption(
                "💡 `index.html` = aperçu local (double-clic pour l'ouvrir dans le navigateur). "
                "Pour la mise en ligne, utilisez les blocs Webflow ci-dessous."
            )

            # ── Intégration Webflow : 3 blocs prêts à coller ──────────────────
            st.markdown("---")
            st.markdown("### 🔷 Intégration Webflow")
            blocks = generate_webflow_blocks(solution, participants, n_rounds, event_name)
            st.caption(
                "Webflow → page **speed-business** → ⚙️ Paramètres de la page → *Custom code*. "
                "Les blocs **1** et **2** sont à coller **une seule fois** (ils ne changent jamais). "
                "Le bloc **3** est **à remplacer à chaque événement**, puis **Publier**. "
                "Survolez un bloc → icône 📋 en haut à droite pour tout copier."
            )

            def _code(txt, lang):
                try:
                    st.code(txt, language=lang, wrap_lines=True)
                except TypeError:  # anciennes versions de Streamlit
                    st.code(txt, language=lang)

            with st.expander(f"1️⃣ Head Code — CSS · {len(blocks['head']):,} car. · une seule fois"):
                _code(blocks["head"], "html")
            with st.expander(f"2️⃣ Embed — HTML · {len(blocks['embed']):,} car. · une seule fois"):
                _code(blocks["embed"], "html")
            with st.expander(
                f"3️⃣ Before `</body>` — JS + données · {len(blocks['footer']):,} car. · À CHAQUE ÉVÉNEMENT",
                expanded=True,
            ):
                if len(blocks["footer"]) > 50_000:
                    st.error(
                        f"❌ {len(blocks['footer']):,} caractères : au-delà de la limite Webflow (50 000). "
                        "Réduisez le nombre de participants ou raccourcissez les noms."
                    )
                _code(blocks["footer"], "html")

            webflow_txt = "\n\n".join([
                "===== 1) HEAD CODE (CSS) — une seule fois =====",
                blocks["head"],
                "===== 2) EMBED (HTML) — une seule fois =====",
                blocks["embed"],
                "===== 3) BEFORE </body> (JS + données) — à chaque événement =====",
                blocks["footer"],
            ])
            st.download_button(
                "📄 Télécharger les 3 blocs Webflow (.txt)",
                webflow_txt.encode("utf-8"),
                "webflow_blocs.txt", "text/plain",
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
