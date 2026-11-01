"""Posts files to the Figma connector's upload URLs (from upload_assets), one per file, in order, and records
the node each became. usage: upload.py <urls.txt> <page-id> <manifest.json> <start> <results.json> [retry-failed]
manifest: [{"key", "path", "name", "type"}]. Names are the Figma layer names; a "/" in one cuts it short.
Posts 8 at a time: an image can take ~25 s to place, and the URLs expire 10 minutes after they're issued."""
import json, subprocess, sys, urllib.parse, os
from concurrent.futures import ThreadPoolExecutor
urls_file, page, manifest, start, results = sys.argv[1:6]
only_failed = len(sys.argv) > 6
ids = [l.strip() for l in open(urls_file) if l.strip()]
items = json.load(open(manifest))[int(start):int(start) + len(ids)]
out = json.load(open(results)) if os.path.exists(results) else {}


def post(job):
    uid, it = job
    url = f"https://mcp.figma.com/mcp/upload/{uid}/submit?scaleMode=FILL&currentPageId={urllib.parse.quote(page)}"
    ext = os.path.splitext(it["path"])[1]
    name = it["name"].replace('"', "'") + ext
    r = subprocess.run(["curl", "-sS", "--max-time", "300", "-F", f'file=@{it["path"]};type={it["type"]};filename="{name}"', url],
                       capture_output=True, text=True)
    try:
        j = json.loads(r.stdout)
    except Exception:
        j = {"error": r.stdout[:200] + r.stderr[:200]}
    return it["key"], j.get("placedOnNodeId") or j


jobs = [(uid, it) for uid, it in zip(ids, items) if not (only_failed and isinstance(out.get(it["key"]), str))]
with ThreadPoolExecutor(8) as pool:
    for key, res in pool.map(post, jobs):
        out[key] = res
        print(key, res, flush=True)
json.dump(out, open(results, "w"), indent=1)
