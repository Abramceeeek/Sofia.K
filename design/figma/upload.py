"""Posts files to the Figma connector's upload URLs (from upload_assets), one per file, in order, and records
the node each became. usage: upload.py <urls.txt> <page-id> <manifest.json> <start> <results.json> [retry-failed]
manifest: [{"key", "path", "name", "type"}]. Names are the Figma layer names; a "/" in one cuts it short."""
import json, subprocess, sys, urllib.parse, os
urls_file, page, manifest, start, results = sys.argv[1:6]
only_failed = len(sys.argv) > 6
ids = [l.strip() for l in open(urls_file) if l.strip()]
items = json.load(open(manifest))[int(start):int(start) + len(ids)]
out = json.load(open(results)) if os.path.exists(results) else {}
for uid, it in zip(ids, items):
    if only_failed and isinstance(out.get(it["key"]), str):
        continue
    url = f"https://mcp.figma.com/mcp/upload/{uid}/submit?scaleMode=FILL&currentPageId={urllib.parse.quote(page)}"
    ext = os.path.splitext(it["path"])[1]
    name = it["name"].replace('"', "'") + ext
    r = subprocess.run(["curl", "-sS", "-F", f'file=@{it["path"]};type={it["type"]};filename="{name}"', url],
                       capture_output=True, text=True)
    try:
        j = json.loads(r.stdout)
    except Exception:
        j = {"error": r.stdout[:200] + r.stderr[:200]}
    out[it["key"]] = j.get("placedOnNodeId") or j
    print(it["key"], out[it["key"]])
json.dump(out, open(results, "w"), indent=1)
