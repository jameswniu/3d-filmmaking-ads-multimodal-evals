#!/usr/bin/env python3
"""What a stranger can check without my vendor accounts or a light-field panel.

Deliberately narrow. These are not unit tests of the measurements: the numbers
are pinned by evals/labels.csv and checked by evals/derive.py, which this suite
runs. What is tested here is the property the repo kept getting wrong, which is
that a thing can announce failure and still report success.

    python3 -m pytest tests/ -v
    python3 tests/test_suite.py          # same checks, no pytest needed
"""
import ast
import json
import os
import re
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROBES = os.path.join(ROOT, "probes")


def probe_files():
    return sorted(f for f in os.listdir(PROBES) if f.endswith(".py"))


def run(args, timeout=90):
    return subprocess.run([sys.executable] + args, cwd=ROOT, capture_output=True,
                          text=True, timeout=timeout)


# --- the suite compiles ------------------------------------------------------

def test_every_probe_parses():
    """A probe that does not compile cannot be a gate, however good its docstring."""
    for name in probe_files():
        path = os.path.join(PROBES, name)
        with open(path) as fh:
            ast.parse(fh.read(), filename=path)


# --- no entrypoint may crash instead of explaining itself --------------------

def test_no_probe_tracebacks_on_bare_invocation():
    """README claims probes explain themselves with no arguments.

    Four of them used to raise IndexError instead. A traceback is not an
    explanation, so this asserts the absence of one rather than the presence of
    any particular wording.
    """
    broken = []
    for name in probe_files():
        r = run([os.path.join("probes", name)])
        blob = r.stdout + r.stderr
        if "Traceback (most recent call last)" in blob:
            broken.append(f"{name}: traceback on no args")
    assert not broken, "probes crash instead of printing usage: " + "; ".join(broken)


def test_bare_invocation_never_claims_success_while_failing():
    """The failure this repo keeps rediscovering: printing an error, exiting 0.

    A probe with no input has not measured anything. If it exits 0 a shell
    caller reads that as a pass, which is exactly how a missing file becomes a
    silent approval.
    """
    liars = []
    for name in probe_files():
        r = run([os.path.join("probes", name)])
        said_usage = re.search(r"usage[: ]", (r.stdout + r.stderr), re.I)
        if said_usage and r.returncode == 0:
            liars.append(f"{name}: printed usage but exited 0")
    assert not liars, "; ".join(liars)


# --- the derivation is the product ------------------------------------------

def test_derive_runs_clean():
    r = run([os.path.join("evals", "derive.py")])
    assert r.returncode == 0, (
        f"evals/derive.py exited {r.returncode}\n{r.stdout}\n{r.stderr}")


def derive_json():
    r = run([os.path.join("evals", "derive.py"), "--json"])
    return json.loads(r.stdout)


def test_derive_json_shape():
    data = derive_json()
    for key in ("gates", "reproduced", "derived", "authored", "refuted", "n_gating"):
        assert key in data, f"derive --json missing {key}"
    assert data["refuted"] == 0, (
        f"{data['refuted']} threshold(s) sit outside their own labelled interval")
    assert data["derived"] > 0, "no threshold is backed by a labelled pass/reject pair"
    assert data["reproduced"], "no labelled row ships pixels, so nothing is reproducible"
    for row in data["reproduced"]:
        assert row.get("ok"), f"{row['item']} did not reproduce"


WORDS = {1: "one", 2: "two", 3: "three", 4: "four", 5: "five", 6: "six", 7: "seven",
         8: "eight", 9: "nine", 10: "ten", 11: "eleven", 12: "twelve", 13: "thirteen",
         14: "fourteen", 15: "fifteen", 16: "sixteen", 17: "seventeen", 18: "eighteen"}


def test_documented_counts_match_the_tool():
    """EVERY stated count in the docs must equal what derive.py prints.

    An earlier version of this test named six exact strings. That was not enough,
    and an adversarial pass proved it: move the real count, update only the six
    surfaces the test names, and the suite stays green while the README asserts
    five derived plus ten authored out of a total of fifteen that no longer adds
    up, and quotes a line derive.py no longer prints.

    So this scans instead of matching fixed needles. Any sentence anywhere in
    these files that states one of these counts is checked, including ones added
    after this test was written. A pattern with `required` also has to appear at
    least once, so deleting the sentence is not a way to pass.
    """
    data = derive_json()
    d, a, m = data["derived"], data["authored"], data["n_gating"]
    assert d + a == m, (
        f"derive.py is internally inconsistent: {d} derived + {a} authored != {m} gating")
    num = {v: k for k, v in WORDS.items()}

    def val(tok):
        tok = tok.strip().lower()
        return int(tok) if tok.isdigit() else num.get(tok)

    # (regex, tuple of expected values per capture group, required)
    checks = [
        (r"(\w+) of the (\w+) named gating thresholds", (d, m), True),
        (r"and (\d+) of (\d+) named gating thresholds derived", (d, m), True),
        (r"(\d+)%2F(\d+)_derived", (d, m), True),
        (r"(\d+) of (\d+) NAMED gating thresholds are DERIVED", (d, m), True),
        (r"\*\*(\w+) of (\w+)\.\*\*", (d, m), True),
        (r"[Tt]he other (\w+) were typed by hand", (a,), True),
        (r"(\d+) are AUTHORED", (a,), True),
        (r"is one of the (\w+):", (d,), False),
    ]
    problems = []
    for rel in ("README.md", "docs/EVALS.md"):
        text = open(os.path.join(ROOT, rel)).read()
        for pattern, expected, required in checks:
            found = re.findall(pattern, text)
            for hit in found:
                groups = hit if isinstance(hit, tuple) else (hit,)
                got = tuple(val(g) for g in groups)
                if got != expected:
                    problems.append(
                        f"{rel}: {pattern!r} says {got}, derive.py says {expected}")
            if required and not found and rel == "README.md":
                problems.append(f"README.md: no sentence matches {pattern!r}")
    assert not problems, (
        f"derive.py reports {d} derived / {a} authored / {m} gating. "
        + "; ".join(problems))


def test_labelled_pixels_exist():
    """A label pointing at a file that is not in the repo is a claim, not evidence."""
    import csv
    path = os.path.join(ROOT, "evals", "labels.csv")
    with open(path) as fh:
        body = [ln for ln in fh if not ln.lstrip().startswith("#")]
    missing = []
    for row in csv.DictReader(body):
        px = (row.get("pixels") or "").strip()
        if px and px != "withheld" and not os.path.exists(os.path.join(ROOT, px)):
            missing.append(px)
    assert not missing, "labels reference missing files: " + ", ".join(missing)


# --- constants must be live --------------------------------------------------

def test_no_dead_gating_constants():
    """A constant nobody reads still gets read by a human, who then believes it.

    spasm_probe carried FAIL_RATIO and WARN_RATIO long after the gate stopped
    using them, and its docstring described the verdicts they implied. This
    catches the next one mechanically.
    """
    dead = []
    for name in probe_files():
        path = os.path.join(PROBES, name)
        with open(path) as fh:
            tree = ast.parse(fh.read(), filename=path)
        assigned, loaded = {}, set()
        for node in ast.walk(tree):
            # Covers `X = 1` and the annotated `X: float = 1`, which a regex on
            # `^NAME\s*=` silently misses.
            targets = []
            if isinstance(node, ast.Assign):
                targets = [t for t in node.targets if isinstance(t, ast.Name)]
            elif isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name):
                targets = [node.target]
            for t in targets:
                if t.id.isupper() and len(t.id) >= 2:
                    assigned.setdefault(t.id, node.lineno)
            if isinstance(node, ast.Name) and isinstance(node.ctx, ast.Load):
                loaded.add(node.id)
        for const, line in sorted(assigned.items()):
            # AST sees real reads only, so a name that survives merely by being
            # mentioned in a docstring or an f-string no longer counts as used.
            if const not in loaded:
                dead.append(f"{name}:{const}:{line}")
    assert not dead, "assigned but never read: " + ", ".join(dead)


def _main():
    fns = [(k, v) for k, v in sorted(globals().items())
           if k.startswith("test_") and callable(v)]
    failed = 0
    for name, fn in fns:
        try:
            fn()
            print(f"ok    {name}")
        except AssertionError as exc:
            failed += 1
            print(f"FAIL  {name}\n        {exc}")
        except Exception as exc:                      # noqa: BLE001
            failed += 1
            print(f"ERROR {name}\n        {type(exc).__name__}: {exc}")
    print(f"\n{len(fns) - failed} passed, {failed} failed")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(_main())
