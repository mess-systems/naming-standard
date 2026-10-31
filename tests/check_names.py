"""Check name examples and the site and public DNS exception registers.

This is a test, not a tool: it checks that the forms documented in parts 01, 03,
04 and 08 and the example names agree. Codes are read from the tables of
01-naming-conventions.md and from catalog/, so the text stays the source.
Run: python tests/check_names.py
"""
import datetime, glob, re, sys
import yaml

ROOT = __file__.rsplit("/tests/", 1)[0]
DOC = open(f"{ROOT}/01-naming-conventions.md", encoding="utf-8").read()


def table_codes(heading):
    """First-column codes of the table under a heading of 01."""
    part = DOC.split(heading, 1)[1].split("\n### ", 1)[0]
    return set(re.findall(r"^\| `([a-z][a-z0-9-]*)` \|", part, re.M))


def capability_codes():
    part = DOC.split("### 4.3 Capability codes", 1)[1].split("\n### ", 1)[0]
    codes = set()
    for row in re.findall(r"^\| `[a-z-]+` \| `([^`]+)` \|", part, re.M):
        codes.update(row.split())
    return codes


products = yaml.safe_load(open(f"{ROOT}/catalog/products.yaml"))["products"]
envs = yaml.safe_load(open(f"{ROOT}/catalog/environments.yaml"))["environments"]
sites = yaml.safe_load(open(f"{ROOT}/catalog/sites.yaml"))["sites"]
exceptions = yaml.safe_load(open(f"{ROOT}/catalog/dns-exceptions.yaml"))["exceptions"]

PLANES = table_codes("### 4.1 Planes") - {"product"}
DOMAINS = table_codes("### 4.2 Domains") | {d for p in products.values() for d in p["domains"]}
CAPABILITIES = capability_codes()
ENVS = set(envs)
# Words that read as a tool or an exposure, never as an identity, site or code.
TOOL_WORDS = {"ansible", "terraform", "tofu", "opentofu", "netbird", "cursor", "ide", "proxmox", "onprem", "cloud"}
EXPOSURE_WORDS = {"admin", "admins", "private", "public", "internal", "external"}
# The kind of change is a pull request label, never the first part of a branch (08).
CHANGE_WORDS = {"feature", "feat", "fix", "bugfix", "hotfix", "docs", "chore", "release"}

CODE = r"[a-z][a-z0-9]*"
WORDS = r"[a-z][a-z0-9]*(?:-[a-z0-9]+)*"
TS = r"20\d{6}t\d{6}z"
IDENTITY = (r"(?:agent-" + WORDS + r"|user-" + CODE + r"-" + CODE + r"|svc-" + WORDS
            + r"|" + CODE + r"(?:\." + CODE + r")?(?:-adm)?)")
SITE_RE = re.compile(r"^[a-z][a-z0-9]{1,3}$")
DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")


def grammar_a(name):
    m = re.fullmatch(r"(" + WORDS + r")\.(" + CODE + r")\.(" + CODE + r")(?:\.(" + CODE + r"))?\.svc\.mess\.systems", name)
    return bool(m) and m.group(2) in DOMAINS and m.group(3) in PLANES and (m.group(4) is None or m.group(4) in ENVS - {"prd"})


def public_dns(name, register=True):
    """Grammar B under mess.systems, or a registered exception."""
    if register and name in {e["name"] for e in exceptions}:
        return True
    labels = name.split(".")
    if labels[-2:] != ["mess", "systems"] or any(l in EXPOSURE_WORDS or "-" in l and l.split("-")[-1] in EXPOSURE_WORDS for l in labels):
        return False
    rest = labels[:-2]
    if rest == ["www"]:
        return True
    if len(rest) == 2 and rest[1] == "apps":
        return rest[0] in CAPABILITIES
    if rest and rest[-1] == "x" and 2 <= len(rest) <= 4:
        product, left = rest[-2], rest[:-2]
        if product in CAPABILITIES or product in {"apps", "x"}:
            return False
        if len(left) == 2:
            return left[1] in ENVS - {"prd"} and left[0] not in ENVS
        return all(re.fullmatch(WORDS, l) for l in left)
    return False


def iac_repo(name):
    lib = re.fullmatch(r"(.+-iac)-(roles|modules)", name)
    if lib:
        name = lib.group(1)
    toks = name.split("-")
    if toks[-1] != "iac" or any(t in TOOL_WORDS or t in sites for t in toks):
        return False
    if len(toks) == 2:                       # <domain>-iac in an organisation per plane
        return toks[0] in DOMAINS
    if len(toks) == 3:                       # <plane|product>-<domain>-iac
        return (toks[0] in PLANES or toks[0] in products) and toks[1] in DOMAINS
    return False


def temp_user(name):
    m = re.fullmatch(r"v_(oidc|spire|k8s|approle)_([a-z0-9_]+)_(" + TS + r")_([a-z0-9]{6})", name)
    return bool(m) and len(name) <= 63 and "__" not in name


GROUP = r"(?:zone-" + CODE + r"|tier-" + WORDS + r"|role-" + WORDS + r"|svc-" + WORDS + r"|egress-" + CODE + r"|site-" + CODE + r"|router-" + CODE + r"|app-" + WORDS + r")"
CHECKS = {
    "branch": lambda n: n == "main" or bool(re.fullmatch(r"release/v\d+\.\d+", n)) or bool(re.fullmatch(r"(" + IDENTITY + r")/(?:\d+-)?([a-z0-9-]{1,40})", n))
        and n.split("/")[0] not in TOOL_WORDS | EXPOSURE_WORDS | CHANGE_WORDS,
    "snapshot": lambda n: bool(re.fullmatch(WORDS + r"-(" + "|".join(ENVS) + r")-" + TS, n)),
    "temp-user": temp_user,
    "iac-repo": iac_repo,
    "mesh-policy": lambda n: bool(re.fullmatch(GROUP + r" -> " + GROUP + r"(?: \((?:tcp|udp)\))?", n)),
    "mesh-rule": lambda n: bool(re.fullmatch(r"(?:[a-z][a-z0-9]*(?:-[a-z][a-z0-9]*)*|(?:tcp|udp)-\d{1,5})", n)),
    "posture-check": lambda n: bool(re.fullmatch(r"posture-" + CODE + r"-" + WORDS, n)),
    "mesh-resource": lambda n: bool(re.fullmatch(WORDS, n)) and n.split("-")[0] in sites,
    "mesh-group": lambda n: bool(re.fullmatch(GROUP, n)) and n not in {"admins", "devs"},
    "secrets-mount": lambda n: bool(re.fullmatch(r"(?:database|ssh)-(" + "|".join(sorted(PLANES)) + r")/|pki-(?:root|int)/", n)),
    "public-dns": public_dns,
    "internal-dns": grammar_a,
}

failures = 0

# Registers.
for code, s in sites.items():
    errs = [] if SITE_RE.match(code) else ["site code form"]
    errs += [] if s.get("kind") in {"own", "cld"} else ["site kind"]
    errs += [] if str(s.get("owner", "")).startswith(("role-", "tier-")) else ["site owner group"]
    ok = not errs
    failures += not ok
    print(("ok   " if ok else "FAIL ") + f"catalog/sites.yaml {code}" + ("" if ok else f": {errs}"))
for e in exceptions:
    errs = [k for k in ("name", "canonical", "reason", "owner", "review") if k not in e]
    if not errs:
        if public_dns(e["name"], register=False):
            errs.append("name is already in grammar B, no exception needed")
        if not grammar_a(e["canonical"]):
            errs.append("canonical is not a grammar-A name")
        if not str(e["owner"]).startswith(("role-", "tier-")):
            errs.append("owner is not a group")
        if not isinstance(e["review"], datetime.date) and not DATE_RE.match(str(e["review"])):
            errs.append("review is not a date")
    ok = not errs
    failures += not ok
    print(("ok   " if ok else "FAIL ") + f"catalog/dns-exceptions.yaml {e.get('name')}" + ("" if ok else f": {errs}"))

# Name examples.
for path in sorted(glob.glob(f"{ROOT}/tests/names/*.yaml")):
    for case in yaml.safe_load(open(path))["cases"]:
        valid = CHECKS[case["kind"]](case["name"])
        ok = valid != bool(case.get("invalid"))
        failures += not ok
        label = f"{path.rsplit('/', 1)[1]} {case['kind']} {case['name']}"
        print(("ok   " if ok else "FAIL ") + label + ("" if ok else (" accepted" if valid else " refused")))

sys.exit(1 if failures else 0)
