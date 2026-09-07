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
import shutil
import subprocess
import sys
import tempfile

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
        # Required only while some threshold is still authored; the sentence
        # has no sensible form at zero.
        (r"[Tt]he other (\w+) were typed by hand", (a,), a > 0),
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

    # The hero draws this ratio, and tools/render_diagrams.py restates it as a
    # constant rather than importing derive.py, because drawing a picture must
    # not require numpy and ffmpeg. That restatement is the one number in the
    # generator that can go stale, so it is checked against the tool here.
    gen = {}
    with open(os.path.join(ROOT, "tools", "render_diagrams.py")) as fh:
        for node in ast.walk(ast.parse(fh.read())):
            if isinstance(node, ast.Assign) and isinstance(node.targets[0], ast.Tuple):
                names = [t.id for t in node.targets[0].elts if isinstance(t, ast.Name)]
                if "THRESHOLDS_DERIVED" in names:
                    gen = dict(zip(names, [v.value for v in node.value.elts], strict=True))
    assert gen, "render_diagrams.py no longer declares THRESHOLDS_DERIVED"
    assert (gen["THRESHOLDS_DERIVED"], gen["THRESHOLDS_GATING"]) == (d, m), (
        f"render_diagrams.py says {gen['THRESHOLDS_DERIVED']}/"
        f"{gen['THRESHOLDS_GATING']} derived, derive.py says {d}/{m}. "
        "Update the generator and re-run --write.")


def test_no_retired_claim_survives_on_any_surface():
    """The landing page is more than README.md, and the rest is not text-diffable.

    Two claims were retired: that every threshold is derived, and that all four
    gates block. Both lived in FIVE places, including an SVG text node and its
    own aria-label twin. Fixing the visible pixels while leaving the accessible
    text is not fixing it.

    This used to matter more than a normal staleness check, because both SVGs
    were written by a generator that was NOT in this repository: regenerating
    from that private tree would have silently restored both claims with nothing
    to notice. tools/render_diagrams.py closes that hole. Both SVGs are
    generated here now and byte-checked in CI.

    This test stays, and not merely out of caution. A retired CLAIM is a
    sentence, not a number, so no count check can see one; and docs/ and
    README.md are written by hand and always will be. This is the check that
    reads the words.
    """
    # Regexes, not substrings. The first version used bare substrings and flagged
    # two correct sentences: "holds each derived constant inside the interval" and
    # a legend line defining which gates block. A staleness check that cries wolf
    # gets muted, so these match the retired CLAIM shapes only.
    retired = [
        (r"every threshold (?:in|comes|derived|is derived)",
         "the count is whatever derive.py prints, and is not all of them"),
        (r"never typed", "ten of the fifteen were typed by hand"),
        (r"each derived from", "not every probe threshold is derived from labels"),
        (r"probes,\s*each derived", "not every probe threshold is derived"),
        (r"(?:\d+|four)\s+blocking\s+(?:gates|guards)", "three of the four fail open"),
        (r"gates,\s*blocking\b", "three of the four fail open"),
    ]
    surfaces = []
    for sub in ("assets", "docs"):
        d = os.path.join(ROOT, sub)
        for f in sorted(os.listdir(d)):
            if f.endswith((".svg", ".html", ".md")):
                surfaces.append(os.path.join(sub, f))
    surfaces.append("README.md")

    hits = []
    for rel in surfaces:
        text = open(os.path.join(ROOT, rel), errors="ignore").read().lower()
        # The README narrates what it USED to say; that sentence is history, not a claim.
        text = text.replace("used to say every threshold was derived and none was", "")
        text = text.replace("this page used to say every threshold", "")
        for pattern, why in retired:
            m = re.search(pattern, text)
            if m:
                hits.append(f"{rel} still says {m.group(0)!r} ({why})")
    assert not hits, "retired claims are back: " + "; ".join(hits)


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


def test_pipeline_default_inputs_are_tracked():
    """A default input that git ignores makes the pipeline unrunnable on a clone.

    samples/ was generated, verified locally, and skipped in silence by
    `git add -A`, because .gitignore's first line is a blanket *.mp4 and only
    assets/ had a negation. Every local run passed, because the files were on
    that machine. CI caught it only because the runner had no local copy, and
    the tell in the commit output was a quiet "media=0".

    Existing on disk is not the property that matters. Being in the repository
    is. This checks the second one.
    """
    tracked = set(subprocess.run(
        ["git", "ls-files"], cwd=ROOT, capture_output=True, text=True).stdout.split())
    # Whatever the pipeline modules default to under samples/ must be committed.
    wanted = set()
    for name in sorted(os.listdir(os.path.join(ROOT, "pipeline"))):
        if not name.endswith(".py"):
            continue
        src = open(os.path.join(ROOT, "pipeline", name)).read()
        for stem in ("sample-color.mp4", "sample-depth.mp4"):
            if stem in src:
                wanted.add(f"samples/{stem}")
    assert wanted, "no pipeline module references a samples/ default any more"
    problems = []
    for rel in sorted(wanted):
        if rel not in tracked:
            problems.append(f"{rel} is referenced as a default but is NOT tracked by git")
        elif not os.path.exists(os.path.join(ROOT, rel)):
            problems.append(f"{rel} is tracked but missing from the working tree")
    assert not problems, "; ".join(problems)


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


# --- the diagrams are computed, not typed ------------------------------------

def test_published_svgs_match_their_generator():
    """Both published SVGs must be what tools/render_diagrams.py emits.

    This closes the hole the retired-claim scanner below was only able to
    mitigate. That test's docstring said the SVGs came from a generator NOT in
    this repository, so regenerating from the private tree could silently
    restore a retired claim. The generator is here now, so both files are
    output rather than typed artifacts, and a hand edit to either fails.

    Both are asserted by name, because --check reporting success for a list it
    quietly stopped iterating would pass this test otherwise.
    """
    r = run(["tools/render_diagrams.py", "--check"])
    assert r.returncode == 0, (
        "a published SVG is not what the generator emits. Run "
        "`python3 tools/render_diagrams.py --write` and read the diff.\n"
        + r.stdout + r.stderr)
    for name in ("assets/architecture.svg", "assets/hero.svg"):
        assert f"{name} matches" in r.stdout, (
            f"--check did not report on {name}: " + r.stdout)


def test_stated_counts_agree_on_every_surface():
    """No published surface may state a count the generator disagrees with.

    architecture.svg is generated, but hero.svg is an illustration and is not,
    and docs/architecture.html and the README badges state the same numbers in
    their own formatting. Those were four independent copies of `13 probes` and
    `77 views` that happened to agree. This makes them agree by construction.

    The hit count is asserted as well as the verdict, because a pattern that
    silently stops matching would otherwise report a clean audit of nothing.
    """
    r = run(["tools/render_diagrams.py", "--audit"])
    assert r.returncode == 0, "a surface disagrees with the generator:\n" + \
        r.stdout + r.stderr
    found = re.search(r"(\d+) stated counts", r.stdout)
    assert found, "audit did not report how many counts it checked: " + r.stdout
    assert int(found.group(1)) >= 15, (
        f"audit only found {found.group(1)} stated counts, which means a "
        "pattern stopped matching rather than that the surfaces are clean")


def test_scanner_honours_per_rule_case_flags():
    """A project rule must be able to opt into case-insensitive matching.

    A name is not case-stable in prose. The same identity token gets written
    capitalised, lower, and SHOUTED in a comment, and every project rule ran
    case-SENSITIVE because apply_rule_table never passed the flags argument
    run_rule already accepted. So a rule spelling one capitalisation let the
    others through and reported clean. That is the exact failure this
    repository is about: a check announcing success on input it never examined.

    The negative half carries equal weight. A blanket -i would make the
    built-in identifier rules (tracker keys, chat object ids, both defined as
    uppercase shapes) start matching ordinary lowercase prose, so this asserts
    an unflagged rule stays case-sensitive.

    Line 4 is the word-boundary control. \\b is what keeps a rule from firing on
    every longer word that contains the token, and a scanner whose grep engine
    silently ignores \\b reports a clean audit of nothing.
    """
    script = os.path.join(ROOT, "tools", "pii_scan.sh")
    with tempfile.TemporaryDirectory(dir=ROOT) as tmp:
        rules = os.path.join(tmp, "rules.txt")
        target = os.path.join(tmp, "target.txt")
        with open(rules, "w") as fh:
            # SEVERITY \t CLASS \t LABEL \t REGEX \t FLAGS; absent FLAGS means
            # case-sensitive, which is what every identifier rule relies on.
            fh.write("BLOCKER\tCLASS5-WORKPLACE\tname-any-case\t\\bzebra\\b\t-i\n")
            fh.write("BLOCKER\tCLASS5-WORKPLACE\tid-exact-case\t\\bZQ[0-9]{4}\\b\n")
        with open(target, "w") as fh:
            fh.write("ZEBRA shouted\nzebra lower\nZebra title\n"
                     "zebrafish is a longer word\nZQ1234 identifier\nzq1234 not one\n")
        env = dict(os.environ, PII_CONTEXT_FILE=rules, PII_SCAN_SOFT="1")
        r = subprocess.run(["bash", script, target], cwd=ROOT, env=env,
                           capture_output=True, text=True, timeout=90)
        out = r.stdout + r.stderr
        hits = {}
        for line in out.splitlines():
            parts = line.strip().split(":")
            if len(parts) >= 5 and parts[-1] in ("name-any-case", "id-exact-case"):
                if parts[1].isdigit():
                    hits.setdefault(parts[-1], set()).add(int(parts[1]))
        assert hits.get("name-any-case") == {1, 2, 3}, (
            "a rule carrying -i must match every capitalisation (lines 1, 2, 3) "
            "and must not match the longer word on line 4; got lines "
            f"{sorted(hits.get('name-any-case', []))}\n" + out)
        assert hits.get("id-exact-case") == {5}, (
            "a rule with no flags must stay case-sensitive, or the built-in "
            "uppercase identifier rules start firing on ordinary prose; "
            f"expected only line 5, got {sorted(hits.get('id-exact-case', []))}\n"
            + out)


def test_commit_message_hook_enforces_the_same_table_the_scanner_does():
    """The commit message hook had no test, which is why it failed in silence.

    The rule table grew an optional fifth column. This hook still read four
    fields, so every regex became pattern, tab, flag and matched nothing. It
    kept running and kept printing its banner while passing everything,
    including a message carrying a word the file scanner refuses to publish.
    A gate with no test cannot tell you it has stopped being a gate, and this
    one stayed down for hours before anyone ran it by hand.

    Both directions are asserted, because each has already been wrong once.
    A flagged rule must catch every capitalisation, or a shouted name walks
    through. An unflagged rule must NOT match the wrong case, or a brand name
    that doubles as an ordinary English word turns every honest sentence into
    a finding, and a gate that cries wolf gets bypassed rather than answered.
    """
    hook = os.path.join(ROOT, ".githooks", "commit-msg")
    assert os.access(hook, os.X_OK), "the hook is not executable, so git never runs it"

    with tempfile.TemporaryDirectory(dir=ROOT) as tmp:
        subprocess.run(["git", "init", "-q", tmp], check=True, capture_output=True)
        os.makedirs(os.path.join(tmp, "tools"))
        with open(os.path.join(tmp, "tools", "pii_context.txt"), "w") as fh:
            # FIVE columns on the first rule, FOUR on the second. A hook that
            # reads the wrong number of fields fails one of these two.
            fh.write("BLOCKER\tCLASS5-WORKPLACE\tname-any-case\t\\bzebra\\b\t-i\n")
            fh.write("HIGH\tCLASS5-WORKPLACE\tbrand-exact-case\t\\bZebraCorp\\b\n")

        def run_hook(text):
            msg = os.path.join(tmp, "MSG")
            with open(msg, "w") as fh:
                fh.write(text)
            r = subprocess.run(["bash", hook, msg], cwd=tmp, capture_output=True,
                               text=True, timeout=30)
            return r.returncode, r.stdout + r.stderr

        rc, out = run_hook("Fix the ZEBRA handling in the renderer\n")
        assert rc != 0, ("a rule carrying -i must block every capitalisation; the "
                         "shouted spelling is the one that leaked\n" + out)
        assert "name-any-case" in out, "the finding must name its rule: " + out

        rc, out = run_hook("Fix the zebracorp handling\n")
        assert rc == 0, ("an unflagged rule must not match the wrong case, or an "
                         "ordinary word becomes a finding on every commit\n" + out)

        rc, out = run_hook("Rename a variable and tighten a docstring\n")
        assert rc == 0, "a clean message must pass: " + out

        rc, out = run_hook("Fix the ZEBRA handling\n")
        assert "ZEBRA" not in out, (
            "the hook printed the matched text. A gate that echoes the string "
            "into your terminal has moved it, not caught it:\n" + out)


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


def _seed_staged_repo(tmp, staged_text, worktree_text, extra=None):
    """A git repo whose index and working tree deliberately disagree.

    The scanner resolves its own repo root from its own location, so the copy
    under test has to live inside the throwaway repo. That is the same shape
    the commit-message hook test uses.
    """
    tools = os.path.join(tmp, "tools")
    os.makedirs(os.path.join(tmp, "docs"))
    os.makedirs(tools)
    shutil.copy2(os.path.join(ROOT, "tools", "pii_scan.sh"),
                 os.path.join(tools, "pii_scan.sh"))

    def git(*args):
        return subprocess.run(["git", "-C", tmp] + list(args),
                              capture_output=True, text=True, check=True)

    subprocess.run(["git", "init", "-q", tmp], check=True, capture_output=True)
    # git does not validate this field, and an address-shaped literal here is
    # a BLOCKER under the scanner's own class 3 rule. Writing one and then
    # suppressing it would be a test file teaching the reader to wave the
    # finding through, so there is simply no address to suppress.
    git("config", "user.name", "zzqa")
    git("config", "user.email", "zzqa")
    git("commit", "-q", "--allow-empty", "-m", "seed")

    target = os.path.join(tmp, "docs", "note.txt")
    with open(target, "w") as fh:
        fh.write(staged_text)
    git("add", "docs/note.txt")
    # The commit is never made. What is staged is what a commit WOULD carry,
    # and the working tree is then moved away from it, which is the whole point.
    with open(target, "w") as fh:
        fh.write(worktree_text)

    for rel, blob in (extra or {}).items():
        path = os.path.join(tmp, rel)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "wb") as fh:
            fh.write(blob)
        git("add", rel)
    return os.path.join(tools, "pii_scan.sh")


def _run_staged_scan(script, tmp):
    # The roster library and both local-only inputs are pointed at paths that
    # do not exist, so this test measures the built-in rule table and nothing
    # about the machine it runs on.
    env = dict(os.environ,
               PII_PATTERNS_LIB=os.path.join(tmp, "no-roster.sh"),
               PII_CONTEXT_FILE=os.path.join(tmp, "no-context.txt"),
               PII_NAMES_FILE=os.path.join(tmp, "no-names.txt"))
    return subprocess.run(["bash", script, "--staged"], cwd=tmp, env=env,
                          capture_output=True, text=True, timeout=90)


def test_staged_scan_reads_the_index_not_the_working_tree():
    """A secret staged and then cleaned from the file still has to be blocked.

    --staged took its file names from the index and then read its bytes from
    disk, which are two different things the moment they disagree. Stage a key,
    edit the key out of the file, commit: the gate scanned the cleaned-up tree,
    passed, and the commit carried the key anyway. Nothing exotic is needed to
    reach it. Staging a fix and then continuing to edit is ordinary work, and
    so is `git add -p`, which stages half a file by design.

    Three properties, because each one fails differently:
      1. the staged secret blocks even though the tree is clean
      2. the finding names the repository path, not the temporary snapshot the
         bytes were read from, or the output is unusable in a ticket
      3. a secret that is ONLY in the working tree does NOT block, which is
         what proves the index is being read rather than both
    """
    key = "AKIA" + "QQQQZZZZWWWW1111"

    with tempfile.TemporaryDirectory() as tmp:
        script = _seed_staged_repo(tmp,
                                   staged_text=f"aws_key = {key}\n",
                                   worktree_text="aws_key = redacted\n")
        r = _run_staged_scan(script, tmp)
        out = r.stdout + r.stderr
        assert r.returncode == 1, (
            "a key that is staged but no longer in the file must still block: "
            f"the commit carries the staged blob, not the tree\nexit={r.returncode}\n{out}")
        assert "cloud-access-key-id" in out, (
            "the staged blob was not scanned at all\n" + out)
        assert "docs/note.txt" in out, (
            "the finding must name the repository path\n" + out)
        assert "/staged/" not in out and "pii_scan." not in out.split("===")[-1], (
            "a temporary snapshot path leaked into the report\n" + out)

    with tempfile.TemporaryDirectory() as tmp:
        script = _seed_staged_repo(tmp,
                                   staged_text="aws_key = redacted\n",
                                   worktree_text=f"aws_key = {key}\n")
        r = _run_staged_scan(script, tmp)
        out = r.stdout + r.stderr
        assert r.returncode == 0, (
            "a secret that exists only in the working tree is not being "
            "committed, so --staged must pass. Failing here means the tree is "
            f"still being read.\nexit={r.returncode}\n{out}")


def test_staged_scan_materializes_media_blobs_too():
    """Class 7 reads bytes, so media has to come from the index as well.

    Half a fix is the dangerous kind. If only the text list were rebuilt from
    the index, a staged image would be looked for on disk, not found, and drop
    out of the scan in silence: the file count would say it was examined and
    the media count would say nothing was there. So this stages an image and
    then deletes it from the working tree, and asserts the scanner still has
    one media file to look at.
    """
    png = (b"\x89PNG\r\n\x1a\n" + b"\x00\x00\x00\rIHDR"
           + b"\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06\x00\x00\x00"
           + b"\x1f\x15\xc4\x89" + b"\x00" * 64)
    with tempfile.TemporaryDirectory() as tmp:
        script = _seed_staged_repo(tmp,
                                   staged_text="nothing to see\n",
                                   worktree_text="nothing to see\n",
                                   extra={"docs/frame.png": png})
        os.remove(os.path.join(tmp, "docs", "frame.png"))
        r = _run_staged_scan(script, tmp)
        out = r.stdout + r.stderr
        header = [ln for ln in out.splitlines() if ln.startswith("mode=staged")]
        assert header, "the scanner printed no mode line\n" + out
        assert "media=1" in header[0], (
            "a staged image that is no longer on disk must still be read from "
            f"the index, or class 7 quietly examines nothing\n{header}\n{out}")


def test_staged_scan_does_not_skip_names_that_merely_start_with_dots():
    """A leading pair of dots is a filename, not a parent directory.

    Materializing the index needs a guard against a path escaping the snapshot
    root, and the first guard was the glob `..*`, which matches `..env` and
    `..secrets/token` as readily as `../etc`. Those are ordinary legal
    filenames, and a credential in one of them dropped out of the scan without
    a word. A guard that silently excludes real files is worse than no guard,
    because the report still says PASS.
    """
    key = "AKIA" + "QQQQZZZZWWWW1111"
    with tempfile.TemporaryDirectory() as tmp:
        script = _seed_staged_repo(
            tmp, staged_text="clean\n", worktree_text="clean\n",
            extra={"..env": f"aws_key = {key}\n".encode(),
                   "..secrets/token.txt": f"aws_key = {key}\n".encode()})
        r = _run_staged_scan(script, tmp)
        out = r.stdout + r.stderr
        assert r.returncode == 1, (
            "a key in a file whose name begins with dots must block like any "
            f"other\nexit={r.returncode}\n{out}")
        for name in ("..env", "..secrets/token.txt"):
            assert name in out, (
                f"{name} was excluded from the scan by the traversal guard\n" + out)


def test_staged_scan_fails_closed_when_a_blob_cannot_be_read():
    """A file that could not be read has not been scanned, and must not pass.

    Materializing the index introduced a way to lose a file quietly: a full
    disk or a damaged object makes the write fail, the path drops out of the
    list, and the scan happily reports PASS on the smaller set. Nothing
    downstream can tell that the set shrank. So an unreadable staged blob is
    exit 2, the scanner-could-not-run code, which the pre-commit hook already
    treats as a hard stop.

    The damage is real rather than simulated: the blob is staged and then its
    object is removed from the object store, so git genuinely cannot produce
    the bytes the index points at.
    """
    with tempfile.TemporaryDirectory() as tmp:
        script = _seed_staged_repo(tmp,
                                   staged_text="a line of nothing\n",
                                   worktree_text="a line of nothing\n")
        sha = subprocess.run(["git", "-C", tmp, "rev-parse", ":docs/note.txt"],
                             capture_output=True, text=True, check=True).stdout.strip()
        obj = os.path.join(tmp, ".git", "objects", sha[:2], sha[2:])
        assert os.path.exists(obj), "expected a loose object in a fresh repo"
        os.remove(obj)

        r = _run_staged_scan(script, tmp)
        out = r.stdout + r.stderr
        assert r.returncode == 2, (
            "an unreadable staged blob must fail the run rather than shrink "
            f"the set being scanned\nexit={r.returncode}\n{out}")
        assert "RESULT: PASS" not in out, (
            "the scan reported a pass on a set it could not fully read\n" + out)
        assert "docs/note.txt" in out, (
            "the run must name the file it could not read\n" + out)


def test_ci_fails_rather_than_passes_when_the_scanner_secret_is_missing():
    """A green tick that means three of the seven classes never ran.

    The workflow printed "ABSENT ... will be SKIPPED" and exited 0, so a
    repository with no secrets configured showed a passing PII gate forever.
    A skipped check is not a passing check, and that sentence is printed by the
    scanner itself; CI was the one surface that did not act on it.

    All four branches are asserted, because three of them are the ways this
    could be fixed wrongly. Failing on a fork would hand a contributor a red
    check they have no way to clear, since a fork cannot read secrets at all.
    Failing on every working-branch push is how a gate gets routed around.
    Passing when the context is unknown is the original defect wearing a hat.
    """
    script = os.path.join(ROOT, "tools", "ci_require_pii_secrets.sh")
    assert os.path.exists(script), "the decision script is missing"

    def run_gate(**over):
        env = {k: v for k, v in os.environ.items()
               if k not in ("PII_CONTEXT", "PII_NAMES", "GITHUB_STEP_SUMMARY")}
        env.update({"IS_FORK": "false", "TARGET_BRANCH": "main",
                    "PUBLICATION_BRANCH": "main"})
        env.update(over)
        r = subprocess.run(["bash", script], cwd=ROOT, env=env,
                           capture_output=True, text=True, timeout=30)
        return r.returncode, r.stdout + r.stderr

    rc, out = run_gate()
    assert rc != 0, ("a missing secret on the publication branch must fail the "
                     "job, not warn and go green\n" + out)
    assert "FAIL" in out, "the failure must say what it is: " + out

    rc, out = run_gate(PII_CONTEXT="x")
    assert rc != 0, ("one secret present is not both; class 4 names still did "
                     "not run\n" + out)
    assert "PII_NAMES" in out, "the failure must name the missing secret: " + out

    # A real rule, in the shape apply_rule_table actually reads: four fields
    # separated by tabs. Anything looser is not a fixture, it is the bug.
    rule = "HIGH\tCLASS5-WORKPLACE\tproject-word\t\\bzebra\\b\n"
    rc, out = run_gate(PII_CONTEXT=rule, PII_NAMES="Jane Doe")
    assert rc == 0, "both secrets present and usable must pass: " + out
    assert "ARMED" in out, out

    # Present is not armed, in three different ways, each of which reported
    # armed at some point while the scanner activated nothing:
    #   comments only, the template pasted straight in
    #   a bare word, which is not a rule and loads as zero rules
    #   tabs flattened to spaces, which is what a paste through a web form does
    for label, ctx, names in (
        ("comments only", "# one rule per line\n", "# one First Last per line\n"),
        ("a bare fragment", "workplaceword\n", "Jane Doe"),
        ("tabs flattened to spaces",
         "HIGH CLASS5-WORKPLACE project-word \\bzebra\\b\n", "Jane Doe"),
        # Consecutive tabs collapse under the scanner's own IFS read, so the
        # regex field lands empty and the rule is skipped. An awk pass with a
        # tab field separator does not collapse them and called this armed.
        ("an empty middle field", "HIGH\tCLASS5-WORKPLACE\t\t\\bzebra\\b\n", "Jane Doe"),
        # The scanner discards grep's complaint about a bad pattern, so a rule
        # that can never fire looks exactly like one that never matched.
        ("a pattern the engine rejects",
         "HIGH\tCLASS5-WORKPLACE\tproject-word\t[unclosed\n", "Jane Doe"),
        ("a roster of nothing but spaces", rule, "   \n"),
        # The report loops over the four severities and counts them with a
        # literal grep, so a rule written `High` records a hit nothing ever
        # counts, displays, or fails on. An invisible finding is worse than no
        # rule: the operator believes the term is guarded.
        ("a severity in the wrong case",
         "High\tCLASS5-WORKPLACE\tproject-word\t\\bzebra\\b\n", "Jane Doe"),
        # Class and label ride in the colon-delimited output line. The scanner
        # already refuses a path carrying a colon for this reason.
        ("a colon in the label",
         "HIGH\tCLASS5-WORKPLACE\tproject:word\t\\bzebra\\b\n", "Jane Doe"),
        # grep takes these without complaint and each one strips the path and
        # line prefix run_rule reads the finding out of, so the rule matches
        # and reports nothing. Exit status alone called them valid.
        ("a flag that suppresses the output the report is parsed from",
         "HIGH\tCLASS5-WORKPLACE\tproject-word\t\\bzebra\\b\t-q\n", "Jane Doe"),
        # One good rule does not excuse a bad one. A malformed row used to be
        # skipped without being counted, so this pair reported ARMED while half
        # of it did nothing.
        ("one good rule beside one pasted with spaces",
         rule + "HIGH CLASS5-WORKPLACE other-word \\bquagga\\b\n", "Jane Doe"),
        # A roster is not armed because ONE name in it survived. An entry the
        # scanner throws away is a third party the operator believes is
        # guarded and is not, which is worse than never listing them.
        ("a roster entry carrying a digit", rule, "Jane Doe\nAgent 007\n"),
        # The killer. A tab-separated read COLLAPSES a run of tabs, so an empty
        # label shifts every field left: label becomes the regex, regex becomes
        # the flags. Severity, class, label and pattern all look valid, the
        # verdict is ARMED, and the scanner hunts for the string `-i` while the
        # term it was configured to guard walks out. Validating with the same
        # collapsing read the scanner uses cannot see this; only a parser that
        # preserves empty columns can.
        ("an empty label that shifts every field left",
         "HIGH\tCLASS5-WORKPLACE\t\t\\bzebra\\b\t-i\n", "Jane Doe"),
        ("a sixth column", rule.rstrip("\n") + "\t-i\textra\n", "Jane Doe"),
    ):
        rc, out = run_gate(PII_CONTEXT=ctx, PII_NAMES=names)
        assert rc != 0, (
            f"{label} arms nothing, so it must not report armed\n" + out)
        assert "NOTE:" in out, (
            "the operator has to be told the secret is set but useless, which "
            f"is a different repair from not set at all ({label})\n" + out)

    rc, out = run_gate(IS_FORK="true")
    assert rc == 0, ("a fork pull request cannot read secrets, so failing it "
                     "hands a contributor a check they cannot clear\n" + out)
    assert "SKIPPED" in out and "not as a pass" in out, (
        "the fork path must report a skip out loud, or it is the same false "
        "green in a different coat\n" + out)

    # A real roster holds O'Connor and Anne-Marie. Letters and spaces alone
    # dropped both without a word, so the scanner accepts hyphens and
    # apostrophes now and these must arm rather than be silently discarded.
    rc, out = run_gate(PII_CONTEXT=rule,
                       PII_NAMES="Sean O'Connor\nAnne-Marie Doe\n")
    assert rc == 0 and "ARMED" in out, (
        "a hyphen and an apostrophe belong in ordinary names, and refusing "
        "them leaves the person they identify unguarded\n" + out)
    scanner = os.path.join(ROOT, "tools", "pii_scan.sh")
    with open(scanner) as fh:
        assert "*[!A-Za-z\\ \\'-]*" in fh.read(), (
            "the scanner still refuses hyphens and apostrophes, so the gate "
            "would arm a roster the scanner then throws half of away")

    # CRLF is what a secret pasted from a Windows editor or a web form looks
    # like, and the stray carriage return lands in the last field on the line.
    # In the flags field grep rejects it outright, in the regex it can never
    # match, and either way the rule is dead while the scanner says nothing.
    # It is normalized away rather than rejected, in the gate and in the
    # workflow that writes the file, so both are reading the same bytes.
    crlf = "HIGH\tCLASS5-WORKPLACE\tproject-word\t\\bzebra\\b\t-i\r\n"
    rc, out = run_gate(PII_CONTEXT=crlf, PII_NAMES="Jane Doe\r\n")
    assert rc == 0 and "ARMED" in out, (
        "a CRLF secret carries usable rules once the carriage returns are "
        "stripped, and stripping them is the fix\n" + out)
    with open(os.path.join(ROOT, ".github", "workflows", "pii-scan.yml")) as fh:
        wf_text = fh.read()
    assert wf_text.count("| tr -d '\\r' > tools/pii_") == 2, (
        "the workflow writes the secret to disk without stripping carriage "
        "returns, so the scanner reads bytes this gate never validated")

    # The validator has to run the invocation the scanner runs, flags and all.
    # Validating the regex alone left the optional fifth field unexamined, so a
    # rule with unusable flags read as valid here and died silently there.
    with open(script) as fh:
        gate_text = fh.read()
    assert 'grep -a -E $flags -e "$re"' in gate_text, (
        "the gate validates a tidier grep call than run_rule actually makes, "
        "which is how an unusable flags field passes validation")

    rc, out = run_gate(TARGET_BRANCH="a-working-branch")
    assert rc == 0, ("a working branch is not the publication moment; a red "
                     "check on every push is how a gate gets bypassed\n" + out)
    assert "WARNING" in out, out

    rc, out = run_gate(TARGET_BRANCH="", PUBLICATION_BRANCH="")
    assert rc != 0, ("an unknown branch context must fail closed. An unknown "
                     "state is not a safe state.\n" + out)


def test_ci_secret_gate_is_actually_wired_into_the_workflow():
    """The script can be perfect and still never run.

    A gate with a test but no caller passes its test and guards nothing, which
    is the failure mode this repository has hit more than once. So the workflow
    is read: it must invoke the script, and it must carry the fork condition
    that turns a fork pull request into a skipped check rather than a green one.
    """
    wf = os.path.join(ROOT, ".github", "workflows", "pii-scan.yml")
    with open(wf) as fh:
        text = fh.read()
    assert "tools/ci_require_pii_secrets.sh" in text, (
        "the workflow does not call the secret gate, so the gate does not run")
    assert "PUBLICATION_BRANCH: ${{ github.event.repository.default_branch }}" in text, (
        "the publication branch is not passed, so the gate cannot tell the "
        "publication moment from an ordinary push")
    # The old wording promised a warning. It described a green check.
    assert "turns that into a visible warning rather than a silent pass" not in text, (
        "the header still describes the behaviour that was the defect")

    # The enforcement has to be its own JOB. A skipped STEP is a line in a log
    # nobody expands; a skipped JOB is a named check reporting SKIPPED in the
    # checks list, which is the only form of "did not run" a human scanning a
    # pull request and a branch rule can both see.
    try:
        import yaml
    except ImportError:
        return
    doc = yaml.safe_load(text)
    assert "armed-context" in doc["jobs"], (
        "the armed check is not a job, so on a fork it is a buried skipped "
        "step inside a green job rather than a check that says it did not run")
    job = doc["jobs"]["armed-context"]
    assert "head.repo.full_name == github.repository" in job.get("if", ""), (
        "the fork condition is gone from the job, so a fork pull request would "
        "run a credentialed check it cannot possibly satisfy")
    runs = " ".join(s.get("run", "") for s in job["steps"])
    assert "ci_require_pii_secrets.sh" in runs, (
        "the armed-context job does not call the gate, so it guards nothing")


def test_ship_gate_finds_the_replay_probe_and_fails_closed_without_it():
    """The replay check was skipped in silence on every run, for months.

    The gate resolved the probe against its own directory, guards/, while the
    probe has always lived in probes/. So the path never existed, and the
    `[ -f "$MP" ]` guard read that as "no probe here, carry on" and fell
    straight through to the next check. A replaying clip passed. Nothing in the
    output said the replay check had not run, which is what makes this the
    expensive kind of bug rather than the loud kind.

    Two properties, and the second is what stops the first from coming back
    quietly. The gate must resolve the probe where the probe actually is, and a
    genuinely missing probe must fail closed with exit 64 like unreadable
    input, not be skipped.
    """
    gate = os.path.join(ROOT, "guards", "ship_gate.sh")
    with open(gate) as fh:
        text = fh.read()

    assert 'MP="$SKILL/mirror_probe.py"' in text, (
        "the gate is not looking in the probes directory, so the replay check "
        "resolves to a path that does not exist and is skipped in silence")
    assert os.path.exists(os.path.join(PROBES, "mirror_probe.py")), (
        "the probe the gate resolves to is not there")
    assert 'if [ -f "$MP" ] && [ -z "$ARROWOK" ]' not in text, (
        "a missing probe is being treated as a reason to skip the check, which "
        "is how it disappeared for months")
    # Every other failing path in this gate drops the receipt first. A HOLD that
    # leaves yesterday's approval standing is not a hold: the clip still looks
    # signed off while nothing has been checked.
    missing_branch = text[text.index("mirror_probe.py not found"):]
    assert 'rm -f "$MARK"' in missing_branch[:missing_branch.index("exit 64")], (
        "the missing-probe HOLD leaves an existing receipt in place")
    # All three exits below the probe drop the receipt: probe missing, probe
    # inconclusive, and replay detected. The last is the one that matters most
    # and the one that was unreachable until the probe path was fixed, so it is
    # the one nobody had ever exercised.
    replay_branch = text[text.index("the scene replays itself"):]
    assert 'rm -f "$MARK"' in replay_branch[:replay_branch.index("exit 3")], (
        "a clip the probe just REJECTED keeps its approval receipt")

    # The four outcomes are EXECUTED, not read. Driving the whole gate cannot
    # reach this section without real video: the geometry check reads the file
    # with ffprobe and exits 64 first, so a test that feeds it a text file named
    # clip.mp4 and asserts "nonzero" is only proving the gate rejects a text
    # file. That was the previous version of this test, and deleting the branch
    # under test would have left it green.
    #
    # So the section is lifted out by its own anchors and run with the probe
    # stubbed to each exit code it can return. If the anchors ever move, the
    # extraction raises and this test fails loudly, which is the correct signal.
    block = text[text.index('MP="$SKILL/mirror_probe.py"'):]
    block = block[:block.index('if [ -n "$DIRECTIONAL" ]')]

    def run_replay(probe_exit, replayok="", says=None):
        """probe_exit None means no probe file at all.

        `says` is what the probe prints. The default carries the MIRROR verdict
        line a real probe always prints; passing something else stands in for a
        probe that crashed, which python reports with the same exit 1 the probe
        uses for a detected replay.
        """
        with tempfile.TemporaryDirectory() as tmp:
            skill = os.path.join(tmp, "probes")
            os.makedirs(skill)
            if probe_exit is not None:
                with open(os.path.join(skill, "mirror_probe.py"), "w") as fh:
                    line = says if says is not None else (
                        "MIRROR REPLAYS: stub" if probe_exit == 1 else "MIRROR FORWARD: stub")
                    fh.write(f"import sys\nprint({line!r})\nsys.exit({probe_exit})\n")
            mark = os.path.join(tmp, "receipt")
            with open(mark, "w") as fh:
                fh.write("a receipt from a previous pass\n")
            prelude = ('set -uo pipefail\n'
                       'SKILL="$T_SKILL"\nMARK="$T_MARK"\nF="$T_MARK"\n'
                       'ARROWOK=""\nREPLAYOK="$T_REPLAYOK"\n')
            r = subprocess.run(
                ["bash", "-c", prelude + block + "\nexit 0\n"],
                env=dict(os.environ, T_SKILL=skill, T_MARK=mark,
                         T_REPLAYOK=replayok),
                capture_output=True, text=True, timeout=60)
            return r.returncode, r.stdout + r.stderr, os.path.exists(mark)

    rc, out, receipt = run_replay(None)
    assert rc == 64, f"a missing probe must fail closed with 64, got {rc}\n{out}"
    assert "mirror_probe.py not found" in out, out
    assert not receipt, "the missing-probe HOLD left an existing receipt standing"

    for code in (3, 64):
        rc, out, receipt = run_replay(code)
        assert rc == 64, (
            f"a probe that ran and returned {code} reached no verdict, which must "
            f"fail closed like a missing probe; got {rc}\n{out}")
        assert "no verdict" in out, out
        assert not receipt, (
            f"an inconclusive probe (exit {code}) left an existing receipt standing")

    rc, out, receipt = run_replay(1)
    assert rc == 3, f"a detected replay must hold with 3, got {rc}\n{out}"
    assert "replays itself" in out, out
    assert not receipt, (
        "the clip the probe just REJECTED kept its approval receipt, which is "
        "the worst case of all: it still looks signed off")

    rc, out, receipt = run_replay(1, replayok="the scene is time symmetric")
    assert rc == 0, f"a declared REPLAYOK override must pass, got {rc}\n{out}"
    assert "REPLAY OVERRIDE" in out, out
    assert receipt, "an override is a pass, so the receipt must survive"

    rc, out, receipt = run_replay(0)
    assert rc == 0, f"a clean probe must pass, got {rc}\n{out}"
    assert receipt, "a clean probe must not remove the receipt"

    # A crashed probe exits 1, and so does a detected replay. Only the verdict
    # line tells them apart, and with REPLAYOK set the crash used to walk into
    # the override branch and ship the clip with a receipt and no replay check
    # behind it. Both the bare crash and the crash under an override must hold.
    crashes = (
        ("a bare crash", "", "Traceback: ImportError"),
        ("a crash under an override", "declared symmetric", "Traceback: ImportError"),
        # The nastiest one, and it was live until an adversary reproduced it. A
        # SyntaxError makes python quote the offending SOURCE LINE back at you,
        # and the offending line in this probe is the one that prints the
        # verdict, so the traceback contains the word MIRROR. stderr is folded
        # into the gate's capture, so a loose substring test read that crash as
        # a decision and shipped the clip.
        ("a traceback quoting the verdict line", "declared symmetric",
         '    print(f"MIRROR {out[chr(39)+chr(39)]}: ...  SyntaxError'),
    )
    for label, ok, says in crashes:
        rc, out, receipt = run_replay(1, replayok=ok, says=says)
        assert rc == 64, (
            f"{label} exits 1 exactly like a real replay verdict, so without an "
            f"anchored verdict line it must fail closed; got {rc}\n{out}")
        assert "no verdict matching its exit code" in out, out
        assert not receipt, f"{label} left an approval receipt standing"

    # The verdict must also AGREE with the exit code, or a probe half-rewritten
    # between the two could report forward motion while exiting on a replay.
    rc, out, receipt = run_replay(1, says="MIRROR FORWARD: stub")
    assert rc == 64, f"a FORWARD verdict with a replay exit must hold; got {rc}\n{out}"
    assert not receipt, "a contradictory verdict left an approval receipt standing"

    # A probe that RAN and reached no verdict is the same silent skip wearing
    # different clothes, and it only became reachable here once the probe
    # started running at all. The probe answers 64 for footage it cannot read
    # and 3 for too little visual signal; both used to fall through to the
    # directional check and, with no directional argument, on to a PASS.
    assert 'case "$MPRC" in' in text, (
        "only the replay verdict is handled, so an inconclusive or failed probe "
        "falls through and the clip ships unexamined")
    for code in ("0|1)", "exit 64 ;;"):
        assert code in text, f"the probe status handling is missing {code}"


if __name__ == "__main__":
    sys.exit(_main())
