# Secrets conventions for OpenBao and HashiCorp Vault

> **Status:** v2, evolving. Rules derive from the [naming conventions](01-naming-conventions.md): a secret belongs to its consumer, the plane is the first isolation boundary, vendors are catalog IDs, environments are isolated.
> **Typical starting point:** one KV v2 mount `secret/` with several competing path shapes (see [migration](#7-migration-from-legacy-paths-illustrative)). **Target:** `https://secrets.iam.shared.svc.mess.systems`, one mount per plane, one path grammar.
> No secret values appear in this file. Names only. Written for the KV v2 engine of [OpenBao](https://openbao.org/docs/secrets/kv/kv-v2/) and [HashiCorp Vault](https://developer.hashicorp.com/vault/docs/secrets/kv/kv-v2); the path and naming rules carry over to other secrets managers.

## 1. Principles applied

| # | Rule | Source |
|---|---|---|
| S1 | A secret lives at the path of its **consumer**, because policies grant path prefixes and a policy is issued to a consumer | [OpenBao](https://openbao.org/docs/concepts/policies/) and [Vault](https://developer.hashicorp.com/vault/docs/concepts/policies) policy guidance |
| S2 | Mount = plane. Blast radius and audit follow the first isolation axis | [Planes](01-naming-conventions.md#41-planes) |
| S3 | `env` is **always** in the path, prod included. Stores are not zone-shortened | [Grammar A: internal](01-naming-conventions.md#31-grammar-a-internal) |
| S4 | Vendor credentials sit under the capability that talks to the vendor, item `provider-<vendor>` | [Providers and egress](01-naming-conventions.md#8-providers-and-egress) |
| S5 | Humans have no personal secrets in OpenBao. Personal secrets go to `passwords.iam.corp` (a password manager). Privileged human access uses an OIDC login plus a policy, never a stored token | [NIST SP 800-53 AC-2](https://csrc.nist.gov/projects/cprt/catalog#/cprt/framework/version/SP_800_53_5_2_0/home?element=AC-02) |
| S6 | Break-glass credentials are separate items named `admin`, sealed by policy to `tier-t0-superadmin`, and every read is alerted | privileged-access tiers ([Tier groups](04-identity-conventions.md#31-tier-groups-privilege)) |
| S7 | One secret per item, several fields per secret. Fields use standard `snake_case` names so consumers are portable | portability |
| S8 | Every secret carries `custom_metadata` with the [ten metadata keys](01-naming-conventions.md#2-the-ten-metadata-keys) plus `rotation` and `issuer` | discoverability, audit |
| S9 | Prod secrets never appear in a non-prod path. Non-prod items are minted, not copied | environment isolation |
| S10 | Policy and AppRole names **are** identity names ([Identity kinds](04-identity-conventions.md#2-identity-kinds)). No `-policy`, `-role` suffixes | one name per identity |

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

A legacy `secret/` mount stays until every path listed under [migration](#7-migration-from-legacy-paths-illustrative) has moved, then is disabled.

## 3. Path grammar

```
<mount>/<domain>/<capability>/<env>/<item>
<mount>/<domain>/<agent-id>/<env>/<item>          # agents: agent-id replaces capability
<product>/<component>/<env>/<item>                # product mounts
```

| Token | Values |
|---|---|
| `<domain>` | [Domains](01-naming-conventions.md#42-domains) |
| `<capability>` | the consumer's capability, from [Capability codes](01-naming-conventions.md#43-capability-codes-unique-across-all-domains) |
| `<agent-id>` | `agent-<name>` from [Identity kinds](04-identity-conventions.md#2-identity-kinds) (agents consume several capabilities, so they are their own node) |
| `<env>` | `prd dev tst stg`, required |
| `<item>` | [Items and fields](#4-items-and-fields) |

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

Field rules: `snake_case`, lowercase; `url` always includes the scheme; no field is named after an env var (`api_key`, not `MESH_API_KEY`).

`custom_metadata` (S8): `plane, domain, capability, product, env, owner, tier, data_class, rotation` (`90d` | `365d` | `manual`), `issuer` (identity that created it), `consumer` (identity that reads it).

## 5. Policies

| Kind | Name | Grants |
|---|---|---|
| Consumer policy | `<identity-id>` (e.g. `corp-ai-litellm`, `agent-code-review`) | `read` on its own `<mount>/<domain>/<capability>/<env>/*`; `read` on consumer copies it needs |
| Tier policy (humans) | `tier-t0-superadmin`, `tier-t1-platform-ops`, `tier-t2-developer`, `tier-t3-readonly` | t0: all mounts incl. `admin` items, alerted; t1: `shared/`, `platform/`, `eng/` except `admin`; t2: `eng/` and `<product>/` non-`admin`; t3: `list` + metadata only |
| Role policy | `role-<function>` | domain-scoped read/write for that function (e.g. `role-security-engineers` gets `*/sec/*`) |
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

## 7. Migration from legacy paths (illustrative)

The legacy paths below are fictional but show the five typical shapes found in a single `secret/` mount: by vendor, by product, by team, by person, and by tier.

| Legacy (`secret/`) | Target | Notes |
|---|---|---|
| `bots/code-review` (+ `/tracing`) | `corp/ai/agent-code-review/prd/gateway`, `.../llm-traces` | consumer copies; items named after the capability they unlock |
| `llm-gateway/clients` | `corp/ai/gateway/prd/clients` | issuer copy; field names become identity IDs ([Gateway client identities](04-identity-conventions.md#9-gateway-client-identities)) |
| `llm-gateway/keys` | `corp/ai/gateway/prd/provider-acmeai`, `provider-acmecloud` | one item per vendor |
| `acmecloud/vm-api` | `shared/infra/compute/prd/provider-acmecloud` | vendor as node → vendor as item |
| `grafana/oidc` | `shared/obs/dashboards/prd/oidc` | product node → capability node |
| `postgres/admin` | `shared/data/sql/prd/admin` | break-glass |
| `ci/registry-pull` | `eng/sdlc/ci/prd/oci` | consumer = CI |
| `shopfront/db` | `shopfront/api/prd/db` | already product-shaped; add component and env |
| `services/<other>` | under the consuming capability | resolve one by one |
| `dev/<username>/*` | **refused** | rule [S5](#1-principles-applied): password manager or IdP-issued tokens |
| `platform/*`, `admin/*` (tier-shaped) | tier policies ([Policies](#5-policies)) | paths are not tiers |

UI links change from `https://<legacy-host>/ui/vault/secrets/secret/list` to `https://secrets.iam.shared.svc.mess.systems/ui/vault/secrets/<mount>/kv/list/<domain>/<capability>/<env>/`.

## 8. Worked example: an LLM gateway

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
- Vendor name as a path node (`acmecloud/`, `github/`); vendors are items (`provider-*`).
- Product name as a node under a plane mount (`mongodb/`, `grafana/`); use the capability instead.
- Path without `env`.
- Field named like an env var, or in UPPER/kebab case.
- `admin` item readable by any non-t0 policy.
- Policy or role name that differs from the identity name.
- Copying a prod secret into `dev|tst|stg`.
