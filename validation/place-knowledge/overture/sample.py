import duckdb, json, math, re
con=duckdb.connect()
f='validation/place-knowledge/overture/london_central.parquet'
STRATA = {
 "museum": ["museum","history_museum","art_museum","science_museum"],
 "gallery": ["art_gallery"],
 "park_garden": ["park","botanical_garden"],
 "restaurant": ["restaurant"],
 "cafe": ["cafe","coffee_shop"],
 "pub_bar": ["pub","bar"],
 "historic": ["historic_site","monument"],
 "market": ["farmers_market","market","public_market"],
 "shop": ["department_store","shopping_center"],
 "any": None,   # the whole file, to show what's in the long tail
}
rows=[]
for s, cats in STRATA.items():
    where = "true" if cats is None else "cat IN (" + ",".join(f"'{c}'" for c in cats) + ")"
    q=f"""select id,name,cat,hier,basic,confidence,coalesce(len(websites),0)>0 as web, coalesce(len(phones),0)>0 as phone,
          addr, postcode, lon, lat, datasets, licenses, operating_status
          from '{f}' where {where} order by hash(id || 'odys-batch9') limit 5"""
    for r in con.execute(q).fetchall():
        d=dict(zip(["id","name","cat","hier","basic","confidence","web","phone","addr","postcode","lon","lat","datasets","licenses","status"],r))
        d["stratum"]=s; rows.append(d)
# duplicates: other records within ~75 m sharing a name token set
def norm(n): return set(w for w in re.sub(r"[^a-z0-9 ]"," ",(n or "").lower()).split() if w not in {"the","of","and","london","ltd","&"})
for d in rows:
    dl=0.00068; dlon=dl/ math.cos(math.radians(d["lat"]))
    near=con.execute(f"select id,name,cat from '{f}' where lat between ? and ? and lon between ? and ? and id<>?",
                     [d["lat"]-dl,d["lat"]+dl,d["lon"]-dlon,d["lon"]+dlon,d["id"]]).fetchall()
    a=norm(d["name"])
    dup=[ (i,n,c) for i,n,c in near if a and len(a & norm(n))/max(1,len(a|norm(n)))>=0.6]
    d["near_75m"]=len(near); d["dupes"]=[{"name":n,"cat":c} for i,n,c in dup]
tot=con.execute(f"""select count(*), avg(confidence), avg((coalesce(len(websites),0)>0)::int), avg((coalesce(len(phones),0)>0)::int),
   avg((operating_status='permanently_closed')::int), avg((cat is null)::int) from '{f}'""").fetchone()
lic=con.execute(f"select l, count(*) from (select unnest(licenses) l from '{f}') group by 1 order by 2 desc").fetchall()
ds=con.execute(f"select l, count(*) from (select unnest(datasets) l from '{f}') group by 1 order by 2 desc").fetchall()
json.dump({"rows":rows,"totals":dict(zip(["n","conf","web","phone","closed","nocat"],tot)),"licenses":lic,"datasets":ds},
          open('validation/place-knowledge/overture/sample.json','w'),indent=1,default=str)
print(tot); print(lic); print(ds)
for d in rows: print(d["stratum"], "|", d["name"], "|", d["cat"], "|", round(d["confidence"],2), "| web" if d["web"] else "| -", "|", d["status"], "| dupes", len(d["dupes"]), "|", d["datasets"], "|", (d["addr"] or "")[:40])
