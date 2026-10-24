# autoprof.py SRCDIR: RAII fuel scope at the top of every function with a body > 12 lines (on top of ungate.py)
import re,glob,os,sys,json
d=sys.argv[1]; names=[]
pat=re.compile(r'^(\s*)(?:template\s*<[^>]*>\s*)?(?:static\s+|inline\s+|\[\[noreturn\]\]\s+|CHAMP_HOOK\s+)*[A-Za-z_][\w:<>,\*& ]*?[\s\*&]([a-z_]\w*)\s*\([^;{}]*\)\s*(?:const\s*)?(?:noexcept\s*)?\{\s*$')
skip={'dm_cost','dm_mark','fuel_okc','fuel_okc_at','fuel_ok','pp_point','dm_turn_end','dm_turn_start','note_error','attempt','X','Y','dist','main','run_game','is','pr_turn','prof_end'}
for f in sorted(glob.glob(d+'/*.cpp')+glob.glob(d+'/*.h')):
    L=open(f).read().split('\n'); out=[]; i=0
    while i<len(L):
        l=L[i]; out.append(l); m=pat.match(l)
        if m and m.group(2) not in skip and not l.strip().startswith(('if','for','while','switch','return','else')):
            depth=0; j=i
            for j in range(i,len(L)):
                depth+=L[j].count('{')-L[j].count('}')
                if depth<=0: break
            if j-i>12:
                names.append(os.path.basename(f)+':'+m.group(2)); out.append(m.group(1)+'    PROF_SCOPE(%d);'%(len(names)-1))
        i+=1
    open(f,'w').write('\n'.join(out))
json.dump(names,open(d+'/../profnames.json','w'))
print(len(names))
