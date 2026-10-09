# Naming conventions v2 — mess.systems

> **Status:** v2, evolving. Self-contained: every rule needed to apply it is in this repository.
> **Scope:** every identifier a human or machine reads: DNS, hosts, repos, images, buckets, databases, Kubernetes, observability, catalog IDs. Secrets → [03](03-secrets-conventions.md). Identities → [04](04-identity-conventions.md). Worked migration example → [02](02-worked-example.md).
> **Organisation domain:** `mess.systems` is the organisation's own domain and is used throughout. When adapting the standard, substitute your own registered domain.

## 1. Character rules (apply to every family)

| Rule | Value | Why |
|---|---|---|
| Alphabet | `a-z 0-9 -` | RFC 1123 hostnames, Kubernetes names, S3, container registries, most IdPs |
| Case | lowercase only | DNS is case-insensitive; everything else is not |
| Separator between axes | `-` in names, `.` in DNS and dotted IDs, `/` in paths | one meaning per separator |
| Multi-word token | hyphenated (`data-catalog`), never concatenated or camelCase | readability; DNS allows it |
| `_` | only where `-` is illegal: SQL identifiers, env vars, secret field names | forced by the system |
| Label length | ≤ 63 chars; FQDN ≤ 253 | RFC 1035 |
| Leading/trailing `-` | never | RFC 1123 |
| Digits | allowed; a token never starts with a digit | k8s label values, shell |
| Sequence numbers | two digits, zero-padded (`01`) | sorts correctly |
| Reserved words | `api`, `www`, `app`, `admin`, `internal`, `public`, `prod`, `test`, `svc`, `local`, `cluster` — never a plane, domain, capability, or product code | collide with grammar tokens or RFC 6762/6761 |

## 2. The ten metadata keys

Every object family carries the same keys. DNS encodes the first four (plus env when non-prod). The rest live in the catalog for that family.

| Key | Values | Encoded in |
|---|---|---|
| `plane` | `shared corp eng platform ext <product>` | DNS, host, repo, k8s label, secrets mount |
| `domain` | §4.2 codes | DNS, host, repo, schema |
| `capability` | §4.3 codes | DNS leftmost label, SPIFFE path, MCP target |
| `product` | install code (`keycloak`, `gitea`) | host, repo, image, k8s namespace |
| `env` | `prd dev tst stg` | DNS (non-prod only), host, schema, secrets path (always) |
| `owner` | group ID from [04](04-identity-conventions.md) §5 | catalog, secrets metadata, k8s label |
| `tier` | `t0 t1 t2 t3` (privileged-access tiers, [04](04-identity-conventions.md) §3.1) | catalog, identity group |
| `scope` | `dev tst stg prd` — the highest environment the object is certified for | catalog only |
| `data_class` | `public internal confidential restricted` | catalog, secrets metadata, bucket tag |
| `exposure` | `mesh lan public` | catalog, mesh group — **never in the name** |

Kubernetes label keys: `mess.systems/<key>`. Hypervisor and cloud tags: `<key>-<value>` (`plane-corp`), or native key/value tags where supported. Container registry labels: same as hypervisor tags. Secrets manager: `custom_metadata.<key>`.

## 3. DNS — two grammars, nothing else

### 3.1 Grammar A — internal

```
<capability>.<domain>.<plane>.svc.mess.systems                 # prod
<capability>.<domain>.<plane>.<env>.svc.mess.systems           # dev|tst|stg
<surface>.<product>.svc.mess.systems                           # internal product (plane = product)
```

- `svc.mess.systems` is the internal zone (split-horizon, internal CA + ACME). Not delegated publicly. `svc` here means "service zone", unrelated to Kubernetes `*.svc.cluster.local` — different suffix, different resolver.
- The leftmost label is the **capability**, never the product (`git`, not `gitea`). The product is inventory, not part of the name.
- Env is omitted in prod. Everywhere else (hosts, schemas, secrets) `prd` is written.
- One install → exactly one canonical FQDN. Aliases are redirects, not names.
- **A label is never an authorization input.** Reachability and rights come from mesh groups, IdP groups, secrets-manager policies ([04](04-identity-conventions.md)). Two consumers of the same install use the same name and different groups.

### 3.2 Grammar B — public

```
<surface>.<product-domain>            # www | app | api | docs | status | auth
<capability>.apps.mess.systems        # ext plane on the brand domain
www.mess.systems                      # brand
```

- Public names never contain plane, domain, env, or vendor.
- `apps.mess.systems` is the **only** public sub-zone of the brand. It carries `ext` capabilities (partner/demo portals). It is grammar B with the brand as the product.
- A single public vanity name for a control plane that must be reachable before the mesh is up (e.g. the mesh coordinator) is allowed as a recorded, documented exception — not a pattern.

### 3.3 There is no grammar C

| Common anti-pattern | Why it is not a name | Target |
|---|---|---|
| `*.admin.corp.lan`, `*.private.corp.lan` | exposure in the name | same FQDN, different mesh/IdP group |
| `*.mesh`, `*.apps.mesh` | mesh-internal pseudo-TLD; not resolvable outside the mesh DNS | grammar A |
| `vcenter.corp.lan` (product, not capability) | violates leftmost-is-capability | `compute.infra.shared.svc.mess.systems` |
| repo-folder names (`infra/llm-proxy`) | a repository folder is not a naming axis | `gateway.ai.corp` |

## 4. Codes

### 4.1 Planes

| Code | Consumer | Trust |
|---|---|---|
| `shared` | control planes everyone depends on (IAM, PKI, secrets, DNS, mesh, observability, hypervisor) | highest |
| `corp` | employees | internal |
| `eng` | engineers building products | internal |
| `platform` | runtime shared by products | product |
| `<product>` | one product's own runtime | product |
| `ext` | partners, demos, public-facing portals | external |

### 4.2 Domains

| Code | Domain | Default plane |
|---|---|---|
| `iam` | identity, access, PKI, secrets, passwords | shared |
| `gov` | architecture, policy, CMDB, ADRs | corp |
| `sec` | detection, vuln mgmt, SIEM | shared |
| `obs` | metrics, logs, traces, alerting (see README open questions) | shared |
| `net` | DNS, mesh, edge, firewall | shared |
| `infra` | compute, storage, backup, hypervisor | shared |
| `sdlc` | code, CI, artifacts, GitOps | eng |
| `adlc` | AI/agent lifecycle, evals, policy sidecars | eng |
| `ai` | inference, gateway, speech, vision, agents | corp |
| `data` | warehouse, pipelines, catalog, BI, document store | platform |
| `collab` | chat, wiki, docs, video | corp |
| `comm` | mail, notifications | corp |
| `biz` | ERP/CRM/finance | corp |
| `itsm` | service desk, change | corp |
| `api` | API management for products | platform |
| `edge` | ingress for products | platform |

### 4.3 Capability codes (unique across all domains)

A code has **one meaning** in the whole company. The same code may appear in several planes (`egress.net.corp`, `egress.net.platform`) because plane is a different axis; it may not appear in two domains.

| Domain | Codes |
|---|---|
| `iam` | `sso directory pki spiffe secrets passwords b2b` |
| `gov` | `cmdb archrepo adr policy catalog demo audit` |
| `sec` | `siem vuln ids scan` |
| `obs` | `dashboards metrics logs traces alerts` |
| `net` | `dns mesh ingress egress firewall` |
| `infra` | `compute storage backup k8s` |
| `sdlc` | `git ci oci packages gitops flags hub-cache` |
| `adlc` | `registry sandbox evals` |
| `ai` | `gateway inference stt tts ocr llm-traces kb docs guard` |
| `data` | `warehouse orchestrate transform ingest data-catalog bi docstore convert sql cache objects` |
| `collab` | `chat wiki intranet video` |
| `comm` | `mail notify` |
| `biz` | `crm billing` |
| `itsm` | `service-desk change` |
| `api` | `gateway-api portal-api` |
| `edge` | `lb` |

This table is an example reference set, not an inventory; extend or trim it per organisation using the rule below.

Adding a code: check uniqueness across the whole table, hyphenate multi-word, register the capability in the capability catalog first, then here.

### 4.4 Environments and sites

| Env | Code | Site | Code |
|---|---|---|---|
| production | `prd` | on-premises data centre | `dc1` |
| staging | `stg` | public cloud tenant | `cld` |
| test | `tst` | | |
| development | `dev` | | |

Site codes are short, organisation-specific, and listed in the catalog; the two above are examples.

## 5. Object forms

| Family | Form | Example |
|---|---|---|
| Internal FQDN | §3.1 | `git.sdlc.eng.svc.mess.systems` |
| Public FQDN | §3.2 | `app.shopfront.example` |
| Application (catalog, `service.name`, OIDC slug, AppRole) | `<plane>-<domain>-<product>` | `eng-sdlc-gitea` |
| Host / container / VM | `<site>-<plane>-<domain>-<product>-<env>-<NN>` | `dc1-eng-sdlc-gitea-prd-01` |
| Hypervisor node | `<site>-shared-infra-<hypervisor>-<env>-<NN>` | `dc1-shared-infra-kvm-prd-01` |
| Git org / repo | org `<plane>` · repo `<domain>-<product>` | `eng/sdlc-gitea` |
| Container image | `oci.sdlc.eng.svc.mess.systems/<plane>-<domain>/<product>[-<component>]:<tag>` | `oci.sdlc.eng.svc.mess.systems/corp-ai/litellm:1.4.0` |
| Registry project (e.g. Harbor) | `<plane>-<domain>` | `corp-ai` |
| Package feed | `<ecosystem>-<plane>` or `<ecosystem>-proxy` | `npm-proxy`, `pypi-eng` |
| S3 / object bucket | `<plane>-<domain>-<capability>-<env>` | `platform-data-warehouse-prd` |
| Postgres database | `<plane>_<domain>_<capability>_<env>` | `eng_sdlc_git_prd` |
| Postgres / ClickHouse schema | same as database | `platform_data_warehouse_prd` |
| Dataset / dbt mart | `<plane>.<domain>.<table>` | `platform.data.catalog_coverage` |
| Kubernetes namespace | `<product>[-<env>]`; platform services use capability | `shopfront-stg`, `gitops` |
| Kubernetes workload | `<product>-<context>-<role>` | `shopfront-api-web` |
| Kubernetes label | `mess.systems/<key>=<value>` | `mess.systems/plane=platform` |
| Provider catalog ID | `<vendor>.<service>` | `acmecloud.foundation-models` |
| LLM route prefix (gateway) | `<provider-short>/<model>`; `local/` = corp inference | `acmecloud/large-chat` |
| MCP target (gateway) | capability code; providers `<vendor>-<service>` | `convert`, `acmesearch-web` |
| OTel `service.name`, Prometheus `job`, Loki `service_name` | application form | `corp-ai-litellm` |
| Dashboard folder (e.g. Grafana) / dashboard uid | folder `<plane>-<domain>` · uid `<application>-<view>` | `corp-ai` / `corp-ai-litellm-overview` |
| Alert rule | `<Domain><Capability><Symptom>` | `AiGatewayHighErrorRate` |
| Ansible inventory group | `<plane>_<domain>` and `<application>` | `corp_ai`, `corp_ai_litellm` |
| OpenTofu resource name | `<application>_<env>` | `corp_ai_litellm_prd` |
| Certificate (internal) | `*.<domain>.<plane>.svc.mess.systems` per domain-plane pair | `*.ai.corp.svc.mess.systems` |
| System mail sender | `<capability>@mess.systems` | `alerts@mess.systems` |

## 6. Single base URL

One install has one base URL: `https://<fqdn>`. Path-based multi-tenancy (`/admin`, `/ui`) is the product's business; it does not appear in the FQDN. Redirects from old names are allowed for 90 days and listed in the migration table, then removed.

## 7. TLS

- Internal: ACME against `pki.iam.shared`. Per-name issuance is default (e.g. an ingress proxy with on-demand TLS). Pre-issued wildcards only for endpoints that cannot ACME: one per `<domain>.<plane>` pair, listed in the deployment's certificate inventory (see [02](02-worked-example.md) §6 for an example).
- Public: public CA via DNS-01 on the product domain. Wildcard per product domain.
- Names in SANs are always the canonical FQDN plus listed redirects, never legacy names.

## 8. Providers and egress

- External vendors are catalog IDs (`<vendor>.<service>`), never internal FQDNs.
- Egress to a vendor goes through the owning capability (`gateway.ai.corp` for LLM providers, `mesh.net.shared` egress groups for network).
- Provider secrets live under the **consuming** capability's path ([03](03-secrets-conventions.md) §4).

## 9. Procedure

**Step A — intake (axes, in order):** plane → domain → capability → product → env → owner/tier/scope/data_class/exposure.
**Step B — encode:** FQDN (§3), application (§5), host (§5), then family-specific forms. Register in the catalog before DNS.
**Step C — identity & secrets:** mint groups/machine role ([04](04-identity-conventions.md)), mint path ([03](03-secrets-conventions.md)).
**Step D — observe:** `service.name` = application; dashboard folder = `<plane>-<domain>`.

## 10. Refusals (reject the name if…)

| Smell | Rule broken |
|---|---|
| product as leftmost label | §3.1 |
| exposure or tier in a name (`admin.`, `public.`, `t0-`) | §3.1, §2 |
| env in a prod DNS name | §3.1 |
| env missing on a host, schema, bucket, or secrets path | §5, [03](03-secrets-conventions.md) |
| vendor as internal FQDN | §8 |
| two capabilities on one FQDN via paths | §6 |
| repo folder as name | §3.3 |
| `_` in DNS or k8s | §1 |
| capability code reused with a second meaning | §4.3 |
| new grammar for a "special" case | §3.3 |

## 11. Worked encodings

| Intake | FQDN | Application | Host |
|---|---|---|---|
| shared / iam / sso / Keycloak / prd | `sso.iam.shared.svc.mess.systems` | `shared-iam-keycloak` | `dc1-shared-iam-keycloak-prd-01` |
| eng / sdlc / git / Gitea / prd | `git.sdlc.eng.svc.mess.systems` | `eng-sdlc-gitea` | `dc1-eng-sdlc-gitea-prd-01` |
| corp / ai / gateway / LiteLLM / prd | `gateway.ai.corp.svc.mess.systems` | `corp-ai-litellm` | `dc1-corp-ai-litellm-prd-01` |
| corp / ai / gateway / LiteLLM / stg | `gateway.ai.corp.stg.svc.mess.systems` | `corp-ai-litellm` | `dc1-corp-ai-litellm-stg-01` |
| platform / data / docstore / MongoDB / prd | `docstore.data.platform.svc.mess.systems` | `platform-data-mongodb` | `dc1-platform-data-mongodb-prd-01..03` |
| shared / net / mesh / Headscale / prd (cloud site) | `mesh.net.shared.svc.mess.systems` | `shared-net-headscale` | `cld-shared-net-headscale-prd-01` |
| ext / demo portal | `demo.apps.mess.systems` | `ext-gov-demo-portal` | `cld-ext-gov-portal-prd-01` |
| shopfront (product) / app | `app.shopfront.example` | `shopfront-api` | `cld-shopfront-api-prd-01` |
