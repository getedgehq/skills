import re, json, random
lines = open("etiquette.txt", encoding="utf-8").read().split("\n")
end = next(i for i,l in enumerate(lines) if "END OF THE PROJECT" in l)
chap_idx = [i for i,l in enumerate(lines[:end]) if re.match(r"^CHAPTER [IVXL]+\s*$", l)]
out = []
random.seed(7)
for ci, start in enumerate(chap_idx):
    stop = chap_idx[ci+1] if ci+1 < len(chap_idx) else end
    paras, cur = [], []
    for l in lines[start:stop]:
        if l.strip() == "":
            if cur: paras.append(cur); cur = []
        else:
            cur.append(l)
    if cur: paras.append(cur)
    good = []
    for p in paras:
        if any(l.startswith("  ") for l in p): continue          # indented letters/tables/quotes
        t = " ".join(l.strip() for l in p)
        if "[Illustration" in t or t.isupper() or "_" in t[:3]: continue
        t = re.sub(r"_([^_]+)_", r"\1", t)                       # italics markers
        t = re.sub(r"\[\d+\]", "", t)
        n = len(t.split())
        if 70 <= n <= 230 and t[-1] in '.!?"' and not t.startswith(("CHAPTER","(")): good.append(t)
    pick = random.sample(good, min(7, len(good)))
    for j,t in enumerate(pick):
        out.append({"id": f"c{ci+1:02d}p{j}", "group": f"chapter-{ci+1:02d}", "answer": t})
json.dump(out, open("passages.json","w"), indent=1)
print(len(out), "passages from", len(set(o["group"] for o in out)), "chapters")
