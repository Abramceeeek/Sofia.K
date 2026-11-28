import duckdb, json, sys
con = duckdb.connect()
con.execute("INSTALL azure; LOAD azure; SET azure_transport_option_type='curl';")
REL = "2026-11-18.0"
src = f"az://overturemapswestus2.blob.core.windows.net/release/{REL}/theme=places/type=place/*"
q = f"""
COPY (
SELECT id, names.primary AS name, taxonomy.primary AS cat, taxonomy.hierarchy AS hier, basic_category AS basic, confidence,
       websites, socials, phones, addresses[1].freeform AS addr, addresses[1].postcode AS postcode,
       ST_X(geometry) AS lon, ST_Y(geometry) AS lat, [s.dataset for s in sources] AS datasets, [s.license for s in sources] AS licenses,
       operating_status
FROM read_parquet('{src}', hive_partitioning=1)
WHERE bbox.xmin BETWEEN -0.25 AND 0.05 AND bbox.ymin BETWEEN 51.45 AND 51.57
) TO 'validation/place-knowledge/overture/london_central.parquet' (FORMAT parquet)
"""
try:
    con.execute("INSTALL spatial; LOAD spatial;")
    con.execute(q)
except Exception as e:
    print("ERR", type(e).__name__, str(e)[:500]); sys.exit(1)
print(con.execute("SELECT count(*) FROM 'validation/place-knowledge/overture/london_central.parquet'").fetchone())
