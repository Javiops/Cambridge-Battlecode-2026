"""Behaviour cloning of the top teams' fight decisions.

usage: bc.py TURNS_CSV OUT_DIR
Fits (1) engage-vs-retreat (binary) and (2) engage/hold/retreat (3-class) on Mite + Univardisty
turns, grouped 5-fold CV by match. Models: majority, best single hp threshold, logistic
regression, tiny MLP. Writes metrics.json, coefs.csv, model_lr.json (weights to embed).
"""
import sys, os, json
import numpy as np, pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.neural_network import MLPClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import make_pipeline
from sklearn.model_selection import GroupKFold
from sklearn.inspection import permutation_importance
from sklearn.metrics import accuracy_score, log_loss, balanced_accuracy_score

TURNS, OUT = sys.argv[1], sys.argv[2]
os.makedirs(OUT, exist_ok=True)

FEATS = ['hp_frac', 'hp', 'maxhp', 'melee', 'gems', 'd_altar', 'd_spawn', 'own_casts_last8',
         'dmg_taken_last1', 'dmg_taken_last3', 'n_ally8', 'n_ally4', 'ally_hp8', 'ally_lowfrac8',
         'n_en8', 'n_en4', 'n_en3', 'n_en1', 'en_hp8', 'near_en_dist', 'near_en_hpfrac', 'near_en_melee',
         'min_en_hpfrac', 'en_gems8', 'en_casts_last8', 'en_ranged8', 'log_hp_ratio8', 'en_dmg_last1', 'round']


def prep(d):
    d = d.copy()
    d['log_hp_ratio8'] = np.log(np.clip(d.hp_ratio8, 0.05, 20))
    for c in ['gems', 'en_gems8', 'dmg_taken_last1', 'dmg_taken_last3', 'en_dmg_last1']:
        d[c] = np.log1p(d[c].clip(lower=0))
    return d


def cv(model_fn, X, y, groups, k=5):
    pred = np.zeros((len(y), len(np.unique(y))))
    for tr, te in GroupKFold(k).split(X, y, groups):
        m = model_fn(); m.fit(X[tr], y[tr]); pred[te] = m.predict_proba(X[te])
    return pred


def evaluate(name, d, label, classes):
    y = d[label].map({c: i for i, c in enumerate(classes)}).values
    X = d[FEATS].values.astype(float); g = d.match.values
    res = {'n': int(len(y)), 'class_share': {c: round(float((y == i).mean()), 4) for i, c in enumerate(classes)}}
    maj = np.bincount(y).argmax()
    res['majority_acc'] = round(float((y == maj).mean()), 4)
    # best single threshold on hp_frac (our bot's current logic is mostly an hp threshold)
    if len(classes) == 2:
        best = (0, None)
        for t in np.arange(0.1, 0.9, 0.02):
            acc = ((d.hp_frac.values < t).astype(int) == y).mean()  # 1 = retreat
            best = max(best, (acc, round(float(t), 2)))
        res['hp_threshold_acc'] = round(float(best[0]), 4); res['hp_threshold'] = best[1]
    lr = lambda: make_pipeline(StandardScaler(), LogisticRegression(max_iter=2000, C=1.0))
    mlp = lambda: make_pipeline(StandardScaler(), MLPClassifier((16,), alpha=1e-3, max_iter=300, early_stopping=True, random_state=0))
    for mname, fn in (('logreg', lr), ('mlp16', mlp)):
        p = cv(fn, X, y, g)
        res[mname] = dict(acc=round(float(accuracy_score(y, p.argmax(1))), 4),
                          bal_acc=round(float(balanced_accuracy_score(y, p.argmax(1))), 4),
                          logloss=round(float(log_loss(y, p)), 4))
    # full fit for coefficients + permutation importance
    m = lr(); m.fit(X, y)
    sub = np.random.RandomState(0).choice(len(y), min(20000, len(y)), replace=False)
    pi = permutation_importance(m, X[sub], y[sub], n_repeats=5, random_state=0, scoring='accuracy')
    return res, m, pi


def main():
    d = prep(pd.read_csv(TURNS))
    top = d[d.team_tag.isin(['mite', 'uni'])]
    out = {}; coefs = []
    er = top[top.action3.isin(['engage', 'retreat'])].copy()
    er['er'] = er.action3
    r2, m2, pi2 = evaluate('engage_vs_retreat', er, 'er', ['engage', 'retreat'])
    out['engage_vs_retreat'] = r2
    r3, m3, pi3 = evaluate('action3', top, 'action3', ['engage', 'hold', 'retreat'])
    out['action3'] = r3
    sc = m2[0]; lrm = m2[1]
    for f, c, imp in zip(FEATS, lrm.coef_[0], pi2.importances_mean):
        coefs.append(dict(feature=f, coef_std=round(float(c), 4), perm_importance=round(float(imp), 4)))
    pd.DataFrame(coefs).sort_values('perm_importance', ascending=False).to_csv(os.path.join(OUT, 'coefs_engage_vs_retreat.csv'), index=False)
    # transfer: how well does the top-team model predict other teams (and per team)?
    for tag in ['mite', 'uni', 'opp']:
        s = d[(d.team_tag == tag) & d.action3.isin(['engage', 'retreat'])]
        y = (s.action3 == 'retreat').astype(int).values
        out.setdefault('by_team_fit_on_top', {})[tag] = dict(n=int(len(s)), acc=round(float((m2.predict(s[FEATS].values) == y).mean()), 4),
                                                              retreat_share=round(float(y.mean()), 4))
    json.dump(out, open(os.path.join(OUT, 'metrics.json'), 'w'), indent=1)
    model = dict(kind='logistic', label='P(retreat | engage-or-retreat turn)', classes=['engage', 'retreat'],
                 features=FEATS, transforms={'log_hp_ratio8': 'ln(clip(hp_ratio8,0.05,20))',
                                             'log1p': ['gems', 'en_gems8', 'dmg_taken_last1', 'dmg_taken_last3', 'en_dmg_last1']},
                 mean=sc.mean_.round(6).tolist(), scale=sc.scale_.round(6).tolist(),
                 coef=lrm.coef_[0].round(6).tolist(), intercept=float(round(lrm.intercept_[0], 6)))
    json.dump(model, open(os.path.join(OUT, 'model_lr_engage_retreat.json'), 'w'), indent=1)
    print(json.dumps(out, indent=1))
    print(pd.DataFrame(coefs).sort_values('perm_importance', ascending=False).head(15).to_string())


main()
