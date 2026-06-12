# peek.py -- look at the PoeTree dump before parsing, to confirm its layout.
# Run:  python peek.py            (looks in data/poetree_en/)
#       python peek.py SOME/DIR   (look somewhere else)

import json
import os
import sys

import config

DUMP_DIR = sys.argv[1] if len(sys.argv) > 1 else os.path.join(config.DATA_DIR, "poetree_en")
TALLY = 3000   # how many json files to scan for the tally


def shape(value, depth=0, max_depth=3):
    """A short, human-readable sketch of a JSON value's structure."""
    pad = "  " * depth
    if isinstance(value, dict):
        if depth >= max_depth:
            return "{ ... }"
        inner = "\n".join(f"{pad}  {k}: {shape(v, depth + 1, max_depth)}"
                          for k, v in value.items())
        return "{\n" + inner + f"\n{pad}}}"
    if isinstance(value, list):
        if not value:
            return "[] (empty)"
        return f"[{len(value)} items] e.g. " + shape(value[0], depth + 1, max_depth)
    if isinstance(value, str):
        one_line = value.replace("\n", " ")
        return '"' + one_line[:50] + ('..."' if len(one_line) > 50 else '"')
    return repr(value)


def is_poem(rec):
    return isinstance(rec, dict) and "body" in rec and isinstance(rec.get("author"), dict)


def main():
    if not os.path.isdir(DUMP_DIR):
        print("PoeTree dump not found. To set it up:")
        print("  1) download en.zip from https://zenodo.org/records/10907309")
        print(f"  2) unzip it so the json files sit in: {DUMP_DIR}")
        print("  3) run  python peek.py  again")
        return

    paths = []
    for root, _, files in os.walk(DUMP_DIR):
        for fn in files:
            if fn.endswith(".json"):
                paths.append(os.path.join(root, fn))

    print(f"found {len(paths)} json files under {DUMP_DIR}\n")
    if not paths:
        print("no .json files -- did the unzip put them somewhere else?")
        return

    print("first few files:")
    for p in paths[:12]:
        print("  " + os.path.relpath(p, DUMP_DIR))
    print()

    # show one poem record in full so you can see the structure
    for p in paths[:TALLY]:
        try:
            with open(p, encoding="utf-8") as f:
                obj = json.load(f)
        except Exception:
            continue
        rec = obj[0] if isinstance(obj, list) and obj else obj
        if is_poem(rec):
            print("a POEM record looks like:\n" + shape(rec) + "\n")
            break

    # tally what the first TALLY files contain
    poems = dups = undated = other = 0
    for p in paths[:TALLY]:
        try:
            with open(p, encoding="utf-8") as f:
                obj = json.load(f)
        except Exception:
            continue
        for rec in (obj if isinstance(obj, list) else [obj]):
            if is_poem(rec):
                poems += 1
                if rec.get("duplicate"):
                    dups += 1
                elif not (rec.get("year_created") or rec["author"].get("born")):
                    undated += 1
            else:
                other += 1

    scanned = min(len(paths), TALLY)
    print(f"in the first {scanned} files: {poems} poems "
          f"({dups} duplicates, {undated} undated), {other} other.\n")

    if poems:
        print("Looks good -- fetch.py will parse this. Run:  python fetch.py")
    else:
        print("No poem records recognized. Paste one record (above) and I can")
        print("adjust the parser to match.")


if __name__ == "__main__":
    main()
