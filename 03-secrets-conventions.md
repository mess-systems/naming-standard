# Secrets conventions — OpenBao / HashiCorp Vault

> **Status:** v2, evolving. Rules derive from [01-naming-conventions.md](01-naming-conventions.md): a secret belongs to its consumer, the plane is the first isolation boundary, vendors are catalog IDs, environments are isolated.
> **Typical starting point:** one KV v2 mount `secret/` with several competing path shapes (§7). **Target:** `https://secrets.iam.shared.svc.mess.systems`, one mount per plane, one path grammar.
> No secret values appear in this file. Names only. Written for OpenBao / HashiCorp Vault KV v2; the path and naming rules carry over to other secrets managers.

## 1. Principles applied

| # | Rule | Source |
|---|---|---|
| S1 | A secret lives at the path of its **consumer**, because policies grant path prefixes and a policy is issued to a consumer | Vault/OpenBao policy guidance |
| S2 | Mount = plane. Blast radius and audit follow the first isolation axis | 01 §4.1 |
| S3 | `env` is **always** in the path, prod included. Stores are not zone-shortened | 01 §3.1 |
| S4 | Vendor credentials sit under the capability that talks to the vendor, item `provider-<vendor>` | 01 §8 |
| S5 | Humans have no personal secrets in OpenBao. Personal → `passwords.iam.corp` (a password manager). Privileged human access → OIDC login + policy, never a stored token | NIST AC-2 |
| S6 | Break-glass credentials are separate items named `admin`, sealed by policy to `tier-t0-superadmin`, and every read is alerted | privileged-access tiers ([04](04-identity-conventions.md) §3.1) |
| S7 | One secret per item, several fields per secret. Fields use standard `snake_case` names so consumers are portable | portability |
| S8 | Every secret carries `custom_metadata` with the ten keys from 01 §2 plus `rotation` and `issuer` | discoverability, audit |
| S9 | Prod secrets never appear in a non-prod path. Non-prod items are minted, not copied | environment isolation |
| S10 | Policy and AppRole names **are** identity names ([04](04-identity-conventions.md) §2). No `-policy`, `-role` suffixes | one name per identity |

## 2. Mounts

| Mount | Type | Holds |
|---|---|---|
| `shared/` | kv-v2 | control-plane secrets (IAM, PKI, DNS, mesh, observability, infra) |
| `corp/` | kv-v2 | staff-facing services, staff agents |
| `eng/` | kv-v2 | SDLC/ADLC tooling |
| `platform/` | kv-v2 | product-shared runtime |
| `ext/` | kv-v2 | partner/demo portals |
| `<product>/` | kv-v2 | one mount per product (e.g. `shopfront/`, `ledger/`) |
| `pki-int/` | pki | internal issuing CA |
| `transit/` | transit | encryption-as-a-service keys, named `<application>` |
| `auth/approle` | auth | workloads without SPIFFE |
| `auth/jwt-<idp>` (e.g. `jwt-keycloak`) | auth | humans and CI via OIDC |
| `auth/jwt-spire` | auth | SPIFFE workloads (target) |
| `auth/kubernetes-<cluster>` | auth | Kubernetes service accounts |

A legacy `secret/` mount stays until every path in §7 has moved, then is disabled.

## 3. Path grammar

```
<mount>/<domain>/<capability>/<env>/<item>
<mount>/<domain>/<agent-id>/<env>/<item>          # agents: agent-id replaces capability
<product>/<component>/<env>/<item>                # product mounts
```

| Token | Values |
|---|---|
| `<domain>` | 01 §4.2 |
| `<capability>` | 01 §4.3 — the consumer's capability |
| `<agent-id>` | `agent-<name>` from [04](04-identity-conventions.md) §2 (agents consume several capabilities, so they are their own node) |
| `<env>` | `prd dev tst stg` — required |
| `<item>` | §4 |

Depth is fixed at four below the mount. Deeper paths are refused; more structure means another item, not another level.

## 4. Items and fields

Standard items (use these before inventing one):

| Item | Meaning | Standard fields |
|---|---|---|
| `config` | app-level secrets (signing keys, session secret) | `secret_key`, `encryption_key`, `jwt_secret` |
| `db` | database credential of the consumer | `host`, `port`, `database`, `username`, `password`, `dsn` |
| `oidc` | this app's OIDC client at `sso.iam.shared` | `issuer`, `client_id`, `client_secret`, `redirect_uri` |
| `api` | this app's own admin/API token, for operators and automation | `url`, `token` |
| `admin` | break-glass local account (S6) | `username`, `password` |
| `clients` | keys this app **issues** to callers (issuer copy) | one field per caller identity, name = identity ID |
| `provider-<vendor>` | credential for an external vendor (S4) | `api_key`, `base_url`, `account_id` |
| `<capability>` | credential this consumer holds **for** another capability (consumer copy) | fields as issued (`api_key`, `token`, `url`) |
| `tls` | certificate material when not ACME | `cert`, `key`, `ca` |
| `join-tokens`, `regcred`, `webhook` | narrowly named operational items | as needed |

Field rules: `snake_case`, lowercase; `url` always includes scheme; no field named after an env var (`MESH_API_KEY` → `api_key`).

`custom_metadata` (S8): `plane, domain, capability, product, env, owner, tier, data_class, rotation` (`90d` | `365d` | `manual`), `issuer` (identity that created it), `consumer` (identity that reads it).

## 5. Policies

| Kind | Name | Grants |
|---|---|---|
| Consumer policy | `<identity-id>` (e.g. `corp-ai-litellm`, `agent-code-review`) | `read` on its own `<mount>/<domain>/<capability>/<env>/*`; `read` on consumer copies it needs |
| Tier policy (humans) | `tier-t0-superadmin`, `tier-t1-platform-ops`, `tier-t2-developer`, `tier-t3-readonly` | t0: all mounts incl. `admin` items, alerted; t1: `shared/`, `platform/`, `eng/` except `admin`; t2: `eng/` and `<product>/` non-`admin`; t3: `list` + metadata only |
| Role policy | `role-<function>` | domain-scoped read/write for that function (e.g. `role-security-engineers` → `*/sec/*`) |
| Scoped read policy | `<identity-id>-<capability>-ro` | when a consumer needs exactly one foreign item, e.g. `eng-sdlc-jenkins-packages-ro` |

HCL path form: `path "<mount>/data/<domain>/<capability>/<env>/*"` plus `metadata/` for list. Deny lists `*/admin` for everything except `tier-t0-superadmin`.

## 6. Auth roles and tokens

| Auth | Role name | Bound to | Policies | TTL |
|---|---|---|---|---|
| `approle` | `<identity-id>` | secret-id per host, CIDR-bound | `<identity-id>` | token 1h, renewable 24h |
| `jwt-<idp>` | `<group-id>` (`tier-t1-platform-ops`, `role-developers`) | IdP group claim | matching tier/role policies | 8h |
| `jwt-spire` | `<identity-id>` | SPIFFE ID `spiffe://mess.systems/<plane>/<domain>/<capability>` | `<identity-id>` | 1h |
| `kubernetes-<cluster>` | `<namespace>-<serviceaccount>` | SA + namespace | `<identity-id>` | 1h |

Token `display_name` = identity ID. Long-lived root/periodic tokens are refused outside break-glass.

## 7. Migration — legacy shapes → target (illustrative)

The legacy paths below are fictional but show the five typical shapes found in a single `secret/` mount: by vendor, by product, by team, by person, and by tier.

| Legacy (`secret/`) | Target | Notes |
|---|---|---|
| `bots/code-review` (+ `/tracing`) | `corp/ai/agent-code-review/prd/gateway`, `.../llm-traces` | consumer copies; items named after the capability they unlock |
| `llm-gateway/clients` | `corp/ai/gateway/prd/clients` | issuer copy; field names → identity IDs ([04](04-identity-conventions.md) §9) |
| `llm-gateway/keys` | `corp/ai/gateway/prd/provider-acmeai`, `provider-acmecloud` | one item per vendor |
| `acmecloud/vm-api` | `shared/infra/compute/prd/provider-acmecloud` | vendor as node → vendor as item |
| `grafana/oidc` | `shared/obs/dashboards/prd/oidc` | product node → capability node |
| `postgres/admin` | `shared/data/sql/prd/admin` | break-glass |
| `ci/registry-pull` | `eng/sdlc/ci/prd/oci` | consumer = CI |
| `shopfront/db` | `shopfront/api/prd/db` | already product-shaped; add component and env |
| `services/<other>` | under the consuming capability | resolve one by one |
| `dev/<username>/*` | **refused** | S5 — password manager or IdP-issued tokens |
| `platform/*`, `admin/*` (tier-shaped) | tier policies §5 | paths are not tiers |

UI: `https://<legacy-host>/ui/vault/secrets/secret/list` → `https://secrets.iam.shared.svc.mess.systems/ui/vault/secrets/<mount>/kv/list/<domain>/<capability>/<env>/`.

## 8. Worked example — an LLM gateway

```
corp/ai/gateway/prd/config                  secret_key
corp/ai/gateway/prd/clients                 agent-code-review, agent-docs-writer, user-jdoe-ide, svc-corp-collab-mattermost, ...
corp/ai/gateway/prd/provider-acmeai         api_key, base_url
corp/ai/gateway/prd/provider-acmecloud      api_key, base_url, account_id
corp/ai/gateway/prd/provider-acmesearch     api_key, base_url
corp/ai/gateway/prd/llm-traces              public_key, secret_key, url
corp/ai/gateway/prd/oidc                    issuer, client_id, client_secret
corp/ai/agent-code-review/prd/gateway       api_key, url          # consumer copy of one field of clients
```

Policy `corp-ai-litellm`: read `corp/data/ai/gateway/prd/*`. Policy `agent-code-review`: read `corp/data/ai/agent-code-review/prd/*`. Neither can read the other. AppRole `agent-code-review` bound to its runner's CIDR; target replacement is `jwt-spire` with `spiffe://mess.systems/corp/ai/agent-code-review`.

## 9. Refusals

- Path deeper than `<mount>/<a>/<b>/<env>/<item>`.
- Vendor name as a path node (`acmecloud/`, `github/`) — vendors are items (`provider-*`).
- Product name as a node under a plane mount (`mongodb/`, `grafana/`) — capability instead.
- Path without `env`.
- Field named like an env var, or in UPPER/kebab case.
- `admin` item readable by any non-t0 policy.
- Policy or role name that differs from the identity name.
- Copying a prod secret into `dev|tst|stg`.
