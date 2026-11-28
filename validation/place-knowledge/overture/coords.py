import duckdb, json, math, re, yaml, glob
con=duckdb.connect(); f='validation/place-knowledge/overture/london_central.parquet'
STOP={"the","of","and","london","a","in","at","to","on","by","from","walk","into","up","through","its","your"}
def norm(n): return set(w for w in re.sub(r"[^a-z0-9 ]"," ",(n or "").lower()).split() if w not in STOP and len(w)>2)
def dist(a,b,c,d):
    R=6371000; p1,p2=math.radians(a),math.radians(c); dp=p2-p1; dl=math.radians(d-b)
    h=math.sin(dp/2)**2+math.cos(p1)*math.cos(p2)*math.sin(dl/2)**2; return 2*R*math.asin(math.sqrt(h))
out=[]
for p in sorted(glob.glob('brain/data/moments/*.yaml')):
    txt=open(p).read(); d=yaml.safe_load(txt)
    if not isinstance(d,dict) or d.get('status')!='ready': continue
    pl=d.get('place') or {}; lat,lon,name=pl.get('lat'),pl.get('lon'),pl.get('name')
    if lat is None: continue
    coord_line=[l for l in txt.splitlines() if l.startswith('# Coordinates')]
    if any('Overture' in l for l in coord_line): continue   # its coordinates came from Overture: circular
    key=norm(name.split(':')[0].split(',')[0])
    if not key: continue
    dl=0.009; dlon=dl/math.cos(math.radians(lat))
    near=con.execute(f"select name,cat,lat,lon,confidence from '{f}' where lat between ? and ? and lon between ? and ?",[lat-dl,lat+dl,lon-dlon,lon+dlon]).fetchall()
    best=None
    for n,c,a,b,conf in near:
        k=norm(n)
        if not k: continue
        j=len(key&k)/len(key|k)
        if j>=0.5:
            dd=dist(lat,lon,a,b)
            if best is None or dd<best[0]: best=(dd,n,c,conf,j)
    out.append({"card":d['id'],"name":name,"src":(coord_line[0][:90] if coord_line else "card"),
                "match":None if best is None else {"m":round(best[0]),"name":best[1],"cat":best[2],"conf":round(best[3],2)}})
json.dump(out,open('validation/place-knowledge/overture/coords.json','w'),indent=1)
ms=[o["match"]["m"] for o in out if o["match"]]
print(len(out),"cards with their own coordinates;",len(ms),"matched by name within 1 km")
import statistics
print("median m",statistics.median(ms),"<=50m",sum(m<=50 for m in ms),"<=150m",sum(m<=150 for m in ms),">300m",sum(m>300 for m in ms))
for o in out:
    if o["match"] and o["match"]["m"]>150: print(o["card"],o["name"],"->",o["match"])
print("unmatched:",[o["card"] for o in out if not o["match"]])
w=con.execute(f"select name,cat,lat,lon,addr from '{f}' where name ilike 'Windsor Castle%' or name ilike 'Highland Coffee%' or name ilike 'Mcbeuvb%'").fetchall(); print(w)
