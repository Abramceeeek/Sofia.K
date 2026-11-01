"""Writes the use_figma script that lays out the real screens in Figma: each screen's iPhone and Android pictures side
by side under one label, grouped by journey (build_shots.py's GROUPS), in auto-layout. It finds the uploaded pictures
by layer name ("iphone-<screen>", "android-<screen>", as upload.py names them from shots_manifest), so no node ids are
needed, and it removes any duplicate a retried upload left. Safe to run again.

Run: python3 design/figma/shots_layout.py <unzipped-screenshots-dir> <out.js> [manifest.json]
With a manifest path it also writes the upload list for upload.py (every picture, named for its layer).
"""
import json
import sys
import types
from pathlib import Path

sys.modules.setdefault("PIL", types.ModuleType("PIL")).Image = None   # build_shots needs Pillow only for JPEGs
sys.path.insert(0, str(Path(__file__).parent))
import build_shots as bs  # noqa: E402

JS = r'''const page = await figma.getNodeByIdAsync("1:2");
await figma.setCurrentPageAsync(page);
const GROUPS = __GROUPS__;
const WRAP = "Real screens · 1 Nov";
for (const old of page.children.filter(n => n.name === WRAP)) {   // a re-run: pictures back on the page first
  for (const f of old.findAll(n => n.type === "FRAME" && /^(iphone|android)-/.test(n.name))) page.appendChild(f);
  old.remove();
}
const byName = {}; let dupes = 0;
for (const n of page.children.filter(n => n.type === "FRAME" && /^(iphone|android)-/.test(n.name))) {
  if (byName[n.name]) { n.remove(); dupes++; } else byName[n.name] = n;
}
const SERIF = { family: "Newsreader", style: "Regular" }, SANS = { family: "Inter", style: "Regular" }, SEMI = { family: "Inter", style: "Semi Bold" };
await Promise.all([SERIF, SANS, SEMI].map(f => figma.loadFontAsync(f)));
const INK = { r: 30 / 255, g: 35 / 255, b: 38 / 255 }, SOFT = { r: 59 / 255, g: 64 / 255, b: 68 / 255 }, MUTED = { r: 91 / 255, g: 96 / 255, b: 100 / 255 };
function text(s, font, size, color, width) {
  const t = figma.createText(); t.fontName = font; t.characters = s; t.fontSize = size; t.fills = [{ type: "SOLID", color }];
  if (width) { t.textAutoResize = "HEIGHT"; t.resize(width, t.height); }
  return t;
}
const wrap = figma.createAutoLayout("VERTICAL", { name: WRAP, itemSpacing: 140 });
wrap.fills = []; page.appendChild(wrap); wrap.x = 72; wrap.y = 72;
const intro = figma.createAutoLayout("VERTICAL", { name: "About this page", itemSpacing: 18 }); intro.fills = [];
intro.appendChild(text("ODYS · every screen a person sees", SERIF, 72, INK));
intro.appendChild(text(__INTRO__, SANS, 22, SOFT, 1700));
wrap.appendChild(intro);
let pairs = 0, placed = 0, holes = 0;
const lost = [];
for (const [title, items] of GROUPS) {
  const sec = figma.createAutoLayout("VERTICAL", { name: title, itemSpacing: 44 }); sec.fills = [];
  sec.appendChild(text(title, SERIF, 56, INK));
  const grid = figma.createAutoLayout("HORIZONTAL", { name: title + " · screens", itemSpacing: 80 }); grid.fills = [];
  grid.layoutWrap = "WRAP"; grid.counterAxisSpacing = 96;
  grid.resize(6 * 819 + 5 * 80, 100); grid.primaryAxisSizingMode = "FIXED"; grid.counterAxisSizingMode = "AUTO";
  sec.appendChild(grid);
  for (const [label, ik, ak, note] of items) {
    const pair = figma.createAutoLayout("VERTICAL", { name: label, itemSpacing: 14 }); pair.fills = [];
    pair.appendChild(text(label, SERIF, 28, INK, 819));
    const row = figma.createAutoLayout("HORIZONTAL", { name: "iPhone and Android", itemSpacing: 24 }); row.fills = [];
    for (const [plat, key, w, h] of [["iPhone", ik, 402, 874], ["Android", ak, 393, 852]]) {
      const col = figma.createAutoLayout("VERTICAL", { name: plat, itemSpacing: 8 }); col.fills = [];
      const cap = text(plat.toUpperCase(), SEMI, 14, MUTED); cap.letterSpacing = { unit: "PIXELS", value: 1.2 }; col.appendChild(cap);
      const node = key ? byName[key] : null;
      if (node) {
        node.resize(w, h); node.name = plat + " · " + label;
        const fl = node.fills; if (Array.isArray(fl) && fl.length && fl[0].type === "IMAGE" && fl[0].scaleMode !== "FILL") node.fills = [{ ...fl[0], scaleMode: "FILL" }];
        col.appendChild(node); placed++;
      } else {
        if (key) lost.push(key);
        const box = figma.createAutoLayout("VERTICAL", { name: plat + " · not on this phone", paddingLeft: 40, paddingRight: 40 });
        box.primaryAxisAlignItems = "CENTER"; box.counterAxisAlignItems = "CENTER";
        box.resize(w, h); box.primaryAxisSizingMode = "FIXED"; box.counterAxisSizingMode = "FIXED";
        box.fills = []; box.strokes = [{ type: "SOLID", color: { r: 167 / 255, g: 161 / 255, b: 150 / 255 } }]; box.strokeWeight = 1.5; box.dashPattern = [8, 6];
        const t = text(key ? "Picture not uploaded yet." : note, SANS, 18, MUTED, w - 80); t.textAlignHorizontal = "CENTER"; box.appendChild(t);
        col.appendChild(box); holes++;
      }
      row.appendChild(col);
    }
    pair.appendChild(row); grid.appendChild(pair); pairs++;
  }
  wrap.appendChild(sec);
}
const loose = page.children.filter(n => n.type === "FRAME" && /^(iphone|android)-/.test(n.name)).map(n => n.name);
return { wrapperId: wrap.id, pairs, placed, holes, dupes, lost, loose, bounds: [wrap.x, wrap.y, wrap.width, wrap.height] };'''

INTRO = ("iPhone and Android side by side, by journey (1 Nov). 86 iPhone screens from the screenshot run of the code "
         "on main (commit 94f31d4) and 86 Android screens drawn by its tests, both from the same sample data with no "
         "server. Night unless the label says day or golden hour. These are pictures to comment on; the editable "
         "versions are on the first page. The 25 Oct set is further right, kept so its comments stay.")


def main(shots_dir, out_js, manifest=None):
    d = Path(shots_dir)
    ios = {p.stem for p in (d / "iphone").glob("*.jpg")}
    android = {p.stem for p in (d / "android").glob("*.jpg")}
    groups = []
    for title, names in bs.GROUPS:
        items = []
        for n in names:
            i = "iphone-" + n if n in ios else None
            a = "android-" + n if n in android else None
            if not (i or a):
                continue
            words, light = bs.label(n)
            only = bs.ONLY.get(n.partition("-")[0])
            items.append([f"{words} · {light}", i, a, only[1] if only else "Not drawn for this phone yet."])
        groups.append([title, items])
    js = JS.replace("__GROUPS__", json.dumps(groups, ensure_ascii=False)).replace("__INTRO__", json.dumps(INTRO))
    Path(out_js).write_text(js)
    print(f"wrote {out_js}: {sum(len(g[1]) for g in groups)} screens, {len(js)} characters")
    if manifest:
        items = [{"key": f"{p}/{n}", "path": str(d / p / f"{n}.jpg"), "name": f"{p}-{n}", "type": "image/jpeg"}
                 for p, names in (("iphone", ios), ("android", android)) for n in sorted(names)]
        Path(manifest).write_text(json.dumps(items, indent=0))
        print(f"wrote {manifest}: {len(items)} pictures")


if __name__ == "__main__":
    main(*sys.argv[1:4])
