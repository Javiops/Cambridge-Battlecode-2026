import pandas as pd, numpy as np, sys
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import GroupKFold, cross_val_predict
from sklearn.metrics import roc_auc_score
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import make_pipeline
E=pd.concat([pd.read_csv('/tmp/fe/o52/episodes.csv'),pd.read_csv('/tmp/fe/otop/episodes.csv')])
E['bad']=(E.out=='L').astype(int); E['lpr']=np.log(E.power_ratio.clip(0.02,50)); E['lhr']=np.log(E.hp_ratio6.clip(0.02,50))
E['first_them']=(E['first']=='them').astype(int); E['first_us']=(E['first']=='us').astype(int)
us=E[E.tag=='us_v52']
def tab(col,bins,df=us):
    c=pd.cut(df[col],bins)
    t=df.groupby(c,observed=True).agg(n=('bad','size'),lost=('bad','mean'),died=('died','mean'),won=('out',lambda s:(s=='W').mean()))
    print('\n##',col); print(t.round(2))
tab('power_ratio',[0,0.25,0.5,0.8,1.25,2,4,100])
tab('hp_frac',[0,.3,.45,.6,.8,1.01])
tab('n_ally3',[-1,0,1,5])
tab('num_diff',[-6,-2,-1,0,1,2,6])
for c in ['first','ready_me','melee']:
    print('\n##',c); print(us.groupby(c).agg(n=('bad','size'),lost=('bad','mean'),won=('out',lambda s:(s=='W').mean())).round(2))
print('\n## same table for top (mite+uni)'); top=E[E.tag.isin(['mite','uni'])]
tab('power_ratio',[0,0.25,0.5,0.8,1.25,2,4,100],top)
print(top.groupby('first').agg(n=('bad','size'),lost=('bad','mean'),won=('out',lambda s:(s=='W').mean())).round(2))
# predictability
X=['lpr','lhr','hp_frac','maxhp','n_ally2','n_ally3','n_ally6','n_en4','n_en6','num_diff','ready_me','ally_ready','en_ready','melee','dist','gems','team_alive','opp_alive']
for tag,df in [('us',us),('top',top),('all',E)]:
    m=make_pipeline(StandardScaler(),LogisticRegression(max_iter=2000))
    p=cross_val_predict(m,df[X],df.bad,groups=df.match,cv=GroupKFold(5),method='predict_proba')[:,1]
    print(tag,'AUC lost-at-first-contact',round(roc_auc_score(df.bad,p),3),'n',len(df))
    df=df.assign(p=p)
    if tag=='us':
        for th in [0.3,0.4,0.5]:
            s=df[df.p>=th]; print(f' p>={th}: {len(s)} episodes ({len(s)/len(df):.0%}), lost {s.bad.mean():.0%}, covers {s.bad.sum()/df.bad.sum():.0%} of lost; engaged share {s.engage_share.mean():.2f} retreat {s.retreat_share.mean():.2f}')
        lo=df[df.p<0.15]; print(f' p<0.15: {len(lo)} lost {lo.bad.mean():.0%}')
    if tag=='all':
        m.fit(E[X],E.bad); co=m[-1].coef_[0]
        print(sorted(zip(X,co.round(2)),key=lambda z:-abs(z[1])))
