#!/usr/bin/env python3
"""gitcleaner: find merged / stale / orphaned git branches and delete them safely."""
import argparse, subprocess, sys, time

__version__ = "0.1.0"
PROTECTED = {"main", "master", "develop", "dev", "trunk", "release"}


def git(*args, check=True):
    r = subprocess.run(["git", *args], capture_output=True, text=True)
    if check and r.returncode:
        raise SystemExit(f"gitcleaner: git {' '.join(args)}: {r.stderr.strip()}")
    return r.stdout


def default_branch():
    ref = git("symbolic-ref", "--quiet", "refs/remotes/origin/HEAD", check=False).strip()
    if ref:
        return ref.rsplit("/", 1)[1]
    for b in ("main", "master"):
        if git("rev-parse", "--verify", "--quiet", f"refs/heads/{b}", check=False).strip():
            return b
    return git("rev-parse", "--abbrev-ref", "HEAD").strip()


def branches(now=None):
    """Return list of dicts for local branches: name, days, merged, gone, current."""
    now = now or time.time()
    base = default_branch()
    merged = {l.strip().lstrip("* ") for l in git("branch", "--merged", base).splitlines()}
    current = git("rev-parse", "--abbrev-ref", "HEAD").strip()
    out = []
    fmt = "%(refname:short)\t%(committerdate:unix)\t%(upstream:track)"
    for line in git("for-each-ref", f"--format={fmt}", "refs/heads").splitlines():
        name, ts, track = line.split("\t")
        out.append({"name": name, "days": int((now - int(ts)) // 86400),
                    "merged": name in merged, "gone": "gone" in track,
                    "current": name == current, "base": base})
    return out


def classify(b, stale_days):
    """Return a reason string if the branch is safe to delete, else None."""
    if b["current"] or b["name"] == b["base"] or b["name"] in PROTECTED:
        return None
    if b["merged"]:
        return "merged"
    if b["gone"]:
        return "upstream gone"
    if stale_days and b["days"] >= stale_days:
        return f"stale ({b['days']}d)"
    return None


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--stale-days", type=int, default=0, metavar="N",
                   help="also treat unmerged branches untouched for N days as candidates (deleting them needs --force)")
    p.add_argument("--delete", action="store_true", help="delete candidates (merged ones with -d, others skipped unless --force)")
    p.add_argument("--force", action="store_true", help="with --delete, also delete unmerged candidates (-D)")
    p.add_argument("--yes", action="store_true", help="do not ask for confirmation")
    p.add_argument("--version", action="version", version=__version__)
    a = p.parse_args(argv)

    bs = branches()
    cands = [(b, r) for b in bs if (r := classify(b, a.stale_days))]
    keep = [b for b in bs if not classify(b, a.stale_days)]
    for b in keep:
        print(f"  keep    {b['name']}")
    for b, r in cands:
        print(f"  delete? {b['name']}  [{r}]")
    if not cands:
        print("nothing to clean")
        return 0
    if not a.delete:
        print(f"\n{len(cands)} candidate(s). Re-run with --delete to remove them.")
        return 0
    if not a.yes and input(f"\nDelete {len(cands)} branch(es)? [y/N] ").lower() != "y":
        print("aborted")
        return 1
    for b, r in cands:
        flag = "-d" if b["merged"] else "-D"
        if flag == "-D" and not a.force:
            print(f"  skip    {b['name']} (unmerged; use --force)")
            continue
        git("branch", flag, b["name"])
        print(f"  deleted {b['name']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
