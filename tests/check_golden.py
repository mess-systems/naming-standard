"""Validate golden examples against the schema and the catalog (07 section 10).

This is a test, not a tool: it checks that the documented rules and the example
data agree. Run: python tests/check_golden.py
"""
import glob, json, sys
import yaml
from jsonschema import Draft202012Validator

ROOT = __file__.rsplit("/tests/", 1)[0]
schema = json.load(open(f"{ROOT}/schema/resource-metadata.schema.json"))
products = yaml.safe_load(open(f"{ROOT}/catalog/products.yaml"))["products"]
envs = yaml.safe_load(open(f"{ROOT}/catalog/environments.yaml"))["environments"]
cells = yaml.safe_load(open(f"{ROOT}/catalog/deployment.yaml"))["cells"]
validator = Draft202012Validator(schema)


def expected(m):
    svc = m["service"] + (f"-{m['component']}" if "component" in m else "")
    labels = [svc, m["domain"]] + ([m["cell"]] if "cell" in m else []) + [m["product"], m["env"]]
    dns = ".".join(labels) + ".svc.mess.systems"
    td = envs[m["env"]]["trust_domain"]
    path = ([m["env"]] if m["env"] != "prd" else []) + [m["product"], m["domain"], m["service"]]
    path += [m["cell"]] if "cell" in m else []
    return {
        "dns": dns,
        "otel": {
            "service.namespace": f"{m['product']}.{m['domain']}",
            "service.name": svc,
            "deployment.environment.name": m["env"],
        },
        "spiffe": f"spiffe://{td}/" + "/".join(path),
    }


failures = 0
for path in sorted(glob.glob(f"{ROOT}/tests/golden/*.yaml")):
    case = yaml.safe_load(open(path))
    m = case["metadata"]
    errors = [e.message for e in validator.iter_errors(m)]
    if not errors:
        doms = products.get(m["product"], {}).get("domains", {})
        if m["service"] not in doms.get(m["domain"], []):
            errors.append("service not in catalog for this product and domain")
        if "cell" in m and m["cell"] not in cells:
            errors.append("cell not in catalog")
    if case.get("invalid"):
        ok = bool(errors)
    else:
        ok = not errors and expected(m) == case["expect"]
        if not errors and not ok:
            errors.append(f"expected {case['expect']}, got {expected(m)}")
    print(("ok   " if ok else "FAIL ") + path.rsplit("/", 1)[1] + ("" if ok else f": {errors}"))
    failures += not ok
sys.exit(1 if failures else 0)
