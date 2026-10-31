# mess.systems naming conventions (v2)

> **Status:** v2, evolving. Self-contained: every rule needed to apply it is in this repository.
> **Scope:** every identifier a human or machine reads: DNS, hosts, repos, images, buckets, databases, Kubernetes, observability, catalog IDs. Secrets are covered by the [secrets conventions](03-secrets-conventions.md), identities by the [identity conventions](04-identity-conventions.md), and a full migration by the [worked example](02-worked-example.md).
> **Organisation domain:** `mess.systems` is the organisation's own domain and is used throughout. When adapting the standard, substitute your own registered domain.

## 1. Character rules (apply to every family)

| Rule | Value | Why |
|---|---|---|
| Alphabet | `a-z 0-9 -` | [RFC 1123](https://www.rfc-editor.org/rfc/rfc1123) hostnames, [Kubernetes names](https://kubernetes.io/docs/concepts/overview/working-with-objects/names/), S3, container registries, most IdPs |
| Case | lowercase only | DNS is case-insensitive; everything else is not |
| Separator between axes | `-` in names, `.` in DNS and dotted IDs, `/` in paths | one meaning per separator |
| Multi-word token | hyphenated (`data-catalog`), never concatenated or camelCase | readability; DNS allows it |
| `_` | only where `-` is illegal: SQL identifiers, env vars, secret field names | forced by the system |
| Label length | ≤ 63 chars; FQDN ≤ 253 | [RFC 1035](https://www.rfc-editor.org/rfc/rfc1035) |
| Leading/trailing `-` | never | RFC 1123 |
| Digits | allowed; a token never starts with a digit | k8s label values, shell |
| Sequence numbers | two digits, zero-padded (`01`) | sorts correctly |
| Reserved words | `api`, `www`, `app`, `admin`, `internal`, `public`, `prod`, `test`, `svc`, `local`, `cluster`; never a plane, domain, capability, or product code | collide with grammar tokens or with names reserved by [RFC 6762](https://www.rfc-editor.org/rfc/rfc6762) and [RFC 6761](https://www.rfc-editor.org/rfc/rfc6761) |

### 1.1 Hyphen parse rule

The hyphen separates the axes of a name and also joins the words of one token (`data-catalog`). A name is parsed by position, so that `dc1-eng-sdlc-data-catalog-prd-01` has exactly one reading.

| Rule | Value |
|---|---|
| Plane and domain codes | one token, no hyphen (`shared`, `eng`, `sdlc`, `obs`) |
| Parsing | left to right along the positions of the form in [object forms](#5-object-forms): the site first (host names only), then plane, then domain, then the product or capability, then env and sequence number when the form has them |
| Env | always a code from [environments and sites](#44-environments-and-sites), so it is recognised by value |
| Sequence number | always two digits in the last position |
| Remainder | everything between the domain and the env (or the end of the name) is one product or capability token, even if it contains hyphens |
| Check | a name is valid only if every position matches its list in `catalog/`; a mismatch is a refusal, not a guess |

Example: `dc1-eng-sdlc-data-catalog-prd-01` is site `dc1`, plane `eng`, domain `sdlc`, product `data-catalog`, env `prd`, number `01`.

Owner, scope and environment qualifiers never go into a name. They live only in labels and tags (`owner`, `scope`, `env`, see [labels and tags](05-labels-and-tags.md)), which are required anyway. A double hyphen is not used as a qualifier separator: it collides with the reserved `xn--` form of DNS labels ([RFC 5891](https://www.rfc-editor.org/rfc/rfc5891)). The RoleBinding form `<role>--<subject>` ([Kubernetes RBAC](04-identity-conventions.md#10-kubernetes-rbac)) is unchanged: it joins two complete names and is not a qualifier.

## 2. The ten metadata keys

Every object family carries the same keys. DNS encodes the first four (plus env when non-prod). The rest live in the catalog for that family.

| Key | Values | Encoded in |
|---|---|---|
| `plane` | `shared corp eng platform ext <product>` | DNS, host, repo, k8s label, secrets mount |
| `domain` | [domain codes](#42-domains) | DNS, host, repo, schema |
| `capability` | [capability codes](#43-capability-codes-unique-across-all-domains) | DNS leftmost label, SPIFFE path, MCP target |
| `product` | install code (`keycloak`, `gitea`) | host, repo, image, k8s namespace |
| `env` | `prd dev tst stg` | DNS (non-prod only), host, schema, secrets path (always) |
| `owner` | group ID (see [owners](04-identity-conventions.md#5-owners)) | catalog, secrets metadata, k8s label |
| `tier` | `t0 t1 t2 t3` (privileged-access tiers, see [tier groups](04-identity-conventions.md#31-tier-groups-privilege)) | catalog, identity group |
| `scope` | `dev tst stg prd`: the highest environment the object is certified for | catalog only |
| `data_class` | `public internal confidential restricted` | catalog, secrets metadata, bucket tag |
| `exposure` | `mesh lan public` | catalog, mesh group; **never in the name** |

[Kubernetes label](https://kubernetes.io/docs/concepts/overview/working-with-objects/labels/) keys: `mess.systems/<key>`. Cloud and hypervisor tags: native key/value tags; `<key>-<value>` (`plane-corp`) only where the platform has no key/value tags. All labels and tags follow [Labels and tags](05-labels-and-tags.md). Container registry labels: same as hypervisor tags. Secrets manager: `custom_metadata.<key>`.

These ten keys describe the **corporate contour**. The **product contour** (products sold to customers, their cells and tenants) uses `product`, `domain`, `service` and `implementation` plus deployment and tenant keys; see [07 Deployment and tenants](07-deployment-and-tenants.md#1-two-contours).

## 3. DNS: two grammars, nothing else

### 3.1 Grammar A: internal

```
<capability>.<domain>.<plane>.svc.mess.systems                 # prod
<capability>.<domain>.<plane>.<env>.svc.mess.systems           # dev|tst|stg
<surface>.<product>.svc.mess.systems                           # superseded by 07 (product contour)
```

- `svc.mess.systems` is the internal zone (split-horizon, internal CA + ACME). Not delegated publicly. `svc` here means "service zone" and is unrelated to Kubernetes `*.svc.cluster.local`, which has a different suffix and a different resolver.
- The leftmost label is the **capability**, never the product (`git`, not `gitea`). The product is inventory, not part of the name.
- Env is omitted in prod. Everywhere else (hosts, schemas, secrets) `prd` is written.
- The product contour writes `prd` in internal DNS as well; see [07 Environments and DNS](07-deployment-and-tenants.md#3-environments-and-dns). The asymmetry is deliberate: corporate names stay short, product names parse the same way in every environment.
- One install has exactly one canonical FQDN. Aliases are redirects, not names.
- **A label is never an authorization input.** Reachability and rights come from mesh groups, IdP groups, and secrets-manager policies (see the [identity conventions](04-identity-conventions.md)). Two consumers of the same install use the same name and different groups.

### 3.2 Grammar B: public

```
<surface>.<product-domain>            # www | app | api | docs | status | auth
<capability>.apps.mess.systems        # ext plane on the brand domain
<surface>.<product>.x.mess.systems    # products in the showcase sub-zone
www.mess.systems                      # brand
```

- Public names never contain plane, domain, env, or vendor. The one exception is the non-production surface of a product (`api.stg.<product-domain>`, see [environments and DNS](07-deployment-and-tenants.md#3-environments-and-dns)).
- The brand has exactly two public sub-zones, and no third:
  - `apps.mess.systems` carries `ext` capabilities (partner/demo portals): `<capability>.apps.mess.systems`. It is grammar B with the brand as the product.
  - `x.mess.systems` carries the products of the product contour ([deployment and tenants](07-deployment-and-tenants.md)): product domain `<product>.x.mess.systems`, surfaces `<surface>.<product>.x.mess.systems`, non-production surfaces `<surface>.<env>.<product>.x.mess.systems`. A product with its own registered domain uses that domain instead of the sub-zone, never both.
- `x` is the label of the sub-zone, not a product code and not the name of a platform. The set of products published in `x.mess.systems` is called the **showcase**. A sub-zone label is never a product code in the organisation's catalog. The fictional product `x` used in the examples of [deployment and tenants](07-deployment-and-tenants.md#2-product-domain-service-implementation) is not in that catalog; there `x.mess.systems` is a placeholder product domain.
- The apex of a product domain (`arch.x.mess.systems`) is the main surface of the product, as `www` is for the brand.
- A public name under `mess.systems` outside grammars A and B is allowed only as a recorded exception in `catalog/dns-exceptions.yaml`: the name, its canonical grammar-A name, the reason, the owner group and a review date. The typical case is a vanity name for a control plane that must be reachable before the mesh is up, such as the mesh coordinator. A name outside both grammars without an entry is refused. An exception is never a pattern for a new name.

```yaml
- name: netbird.mess.systems
  canonical: mesh.net.shared.svc.mess.systems
  reason: the mesh coordinator must be reachable before the mesh is up
  owner: role-platform-engineers
  review: 2027-10-31
```

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
| `obs` | metrics, logs, traces, alerting (see the [open questions](README.md#open-questions) in the README) | shared |
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
| `device` | employee devices, device-side agents, virtual desktops | corp |

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
| `ai` | `gateway inference stt tts ocr llm-traces kb docs guard assistant` |
| `data` | `warehouse orchestrate transform ingest data-catalog bi docstore convert sql cache objects` |
| `collab` | `chat wiki intranet video` |
| `comm` | `mail notify` |
| `biz` | `crm billing` |
| `itsm` | `service-desk change` |
| `api` | `gateway-api portal-api` |
| `edge` | `lb` |
| `device` | `endpoint vdi` |

`endpoint` is device-side: it names what runs on employee devices and never appears in a DNS name; `vdi` is the server-side virtual workplace and is named like any service (`vdi.device.corp.svc.mess.systems`). See [06 Endpoint conventions](06-endpoint-conventions.md#6-capability-code-endpoint).

This table is an example reference set, not an inventory; extend or trim it per organisation using the rule below.

Adding a code: check uniqueness across the whole table, hyphenate multi-word, register the capability in the capability catalog first, then here.

### 4.4 Environments and sites

| Env | Code | Site | Code |
|---|---|---|---|
| production | `prd` | on-premises data centre | `dc1` |
| staging | `stg` | public cloud tenant | `cld` |
| test | `tst` | | |
| development | `dev` | | |
| sandbox (product contour only, see [07](07-deployment-and-tenants.md)) | `sbx` | | |

Site codes are short and organisation-specific; the two above are examples. A site code is registered in `catalog/sites.yaml` before the first host at that site: code (2 to 4 characters, `a-z0-9`, starting with a letter), kind (`own` or `cld`) and owner group. A site code never contains a city, an address or a provider name; the provider is the deployment key `provider` ([deployment keys](07-deployment-and-tenants.md#4-deployment-keys)).

## 5. Object forms

| Family | Form | Example |
|---|---|---|
| Internal FQDN | [grammar A](#31-grammar-a-internal) | `git.sdlc.eng.svc.mess.systems` |
| Public FQDN | [grammar B](#32-grammar-b-public) | `app.shopfront.mess.systems` |
| Application (catalog, `service.name`, OIDC slug, AppRole) | `<plane>-<domain>-<product>` | `eng-sdlc-gitea` |
| Host / container / VM | `<site>-<plane>-<domain>-<product>-<env>-<NN>` | `dc1-eng-sdlc-gitea-prd-01` |
| Hypervisor node | `<site>-shared-infra-<hypervisor>-<env>-<NN>` | `dc1-shared-infra-kvm-prd-01` |
| Enterprise endpoint (laptop, desktop) | `<profile>-<form>-<asset-id>`, see [06 Endpoint conventions](06-endpoint-conventions.md) | `std-lt-a1b2c3` |
| Git org / repo | org `<plane>` · repo `<domain>-<product>` | `eng/sdlc-gitea` |
| Infrastructure-as-code repo, flat organisation | `<plane>-<domain>-iac` | `shared-sec-iac`, `shared-obs-iac` |
| Infrastructure-as-code repo of a product | `<product>-<domain>-iac` | `platform-build-iac`, `shopfront-edge-iac` |
| Infrastructure-as-code repo, organisation per plane | org `<plane>` · repo `<domain>-iac` | `shared/infra-iac` |
| Shared library of roles or modules | owning repo + `-roles` or `-modules` | `shared-infra-iac-roles` |
| Container image | `oci.sdlc.eng.svc.mess.systems/<plane>-<domain>/<product>[-<component>]:<tag>` | `oci.sdlc.eng.svc.mess.systems/corp-ai/agentgateway:1.6.0` |
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
| OTel `service.name`, Prometheus `job`, Loki `service_name` | application form | `corp-ai-agentgateway` |
| Dashboard folder (e.g. Grafana) / dashboard uid | folder `<plane>-<domain>` · uid `<application>-<view>` | `corp-ai` / `corp-ai-agentgateway-overview` |
| Alert rule | `<Domain><Capability><Symptom>` | `AiGatewayHighErrorRate` |
| Ansible inventory group | `<plane>_<domain>` and `<application>` | `corp_ai`, `corp_ai_agentgateway` |
| OpenTofu resource name | `<application>_<env>` | `corp_ai_agentgateway_prd` |
| Certificate (internal) | `*.<domain>.<plane>.svc.mess.systems` per domain-plane pair | `*.ai.corp.svc.mess.systems` |
| System mail sender | `<capability>@mess.systems` | `alerts@mess.systems` |

Infrastructure-as-code repositories: the tool (`ansible`, `opentofu`, `terraform`) and the site (`dc1`, `cld`, a cloud name) are never part of the repository name. They become folders inside (`stacks/<site>/…`, `roles/`, `modules/`); the tool is already recorded in the label `managed-by` ([deployment and tenants](07-deployment-and-tenants.md#7-governance-labels)). One repository serves one pair of plane and domain: two systems of different domains on one machine get two repositories, and the shared machine is described in the inventory. The suffix `-iac` is reserved for infrastructure code.

More object forms live in other parts:

| Object | Where |
|---|---|
| Mount, role and issuer of a secrets engine other than kv (database, ssh, pki) | [engines other than kv](03-secrets-conventions.md#21-engines-other-than-kv) |
| Mesh groups, policies, rules, posture checks, networks, resources, setup keys, nameserver groups | [mesh VPN groups](04-identity-conventions.md#4-mesh-vpn-groups) and the subsections after it |
| Access groups of a product | [product access groups](04-identity-conventions.md#34-product-access-groups) |
| Temporary database user | [temporary database users](04-identity-conventions.md#111-temporary-database-users) |
| Git branch and tag | [Git branches and tags](08-operations-objects.md#1-git-branches-and-tags) |
| CI workflow and job, scheduled job | [CI and scheduled jobs](08-operations-objects.md#2-ci-and-scheduled-jobs) |
| Backup job, snapshot | [backups and snapshots](08-operations-objects.md#3-backups-and-snapshots) |
| Hypervisor guest, resource pool, template | [hypervisor guests](08-operations-objects.md#4-hypervisor-guests) |
| API gateway route, upstream, consumer | [API gateways](08-operations-objects.md#5-api-gateways) |
| DNS record | [DNS records](08-operations-objects.md#6-dns-records) |
| PostgreSQL cluster, replication slot, publication | [PostgreSQL objects](08-operations-objects.md#7-postgresql-objects) |

## 6. Single base URL

One install has one base URL: `https://<fqdn>`. Path-based multi-tenancy (`/admin`, `/ui`) is the product's business; it does not appear in the FQDN. Redirects from old names are allowed for 90 days and listed in the migration table, then removed.

## 7. TLS

- Internal: [ACME](https://www.rfc-editor.org/rfc/rfc8555) against `pki.iam.shared`. Per-name issuance is the default (e.g. an ingress proxy with on-demand TLS). Pre-issued wildcards only for endpoints that cannot use ACME: one per `<domain>.<plane>` pair, listed in the deployment's certificate inventory (the [certificates](02-worked-example.md#6-certificates) step of the worked example shows one).
- Public: public CA via DNS-01 on the product domain. Wildcard per product domain.
- Names in SANs are always the canonical FQDN plus listed redirects, never legacy names.

## 8. Providers and egress

- External vendors are catalog IDs (`<vendor>.<service>`), never internal FQDNs.
- Egress to a vendor goes through the owning capability (`gateway.ai.corp` for LLM providers, `mesh.net.shared` egress groups for network).
- Provider secrets live under the **consuming** capability's path (see [items and fields](03-secrets-conventions.md#4-items-and-fields)).

## 9. Naming procedure

- **Step A, intake.** Fix the axes in this order: plane, domain, capability, product, env, then owner, tier, scope, data_class, and exposure.
- **Step B, encode.** Derive the FQDN ([DNS grammars](#3-dns-two-grammars-nothing-else)), then the application and host names ([object forms](#5-object-forms)), then the family-specific forms. Register the name in the catalog before creating DNS records.
- **Step C, identity and secrets.** Mint the groups and machine role ([identity conventions](04-identity-conventions.md)) and the secrets path ([secrets conventions](03-secrets-conventions.md)).
- **Step D, observe.** Set `service.name` to the application name and the dashboard folder to `<plane>-<domain>`.

## 10. Refusals (reject the name if…)

| Smell | Rule broken |
|---|---|
| product as leftmost label | [Grammar A: internal](#31-grammar-a-internal) |
| exposure or tier in a name (`admin.`, `public.`, `t0-`) | [Grammar A: internal](#31-grammar-a-internal), [The ten metadata keys](#2-the-ten-metadata-keys) |
| env in a prod DNS name | [Grammar A: internal](#31-grammar-a-internal) |
| env missing on a host, schema, bucket, or secrets path | [Object forms](#5-object-forms), [Path grammar](03-secrets-conventions.md#3-path-grammar) |
| vendor as internal FQDN | [Providers and egress](#8-providers-and-egress) |
| two capabilities on one FQDN via paths | [Single base URL](#6-single-base-url) |
| repo folder as name | [There is no grammar C](#33-there-is-no-grammar-c) |
| `_` in DNS or k8s | [Character rules](#1-character-rules-apply-to-every-family) |
| capability code reused with a second meaning | [Capability codes](#43-capability-codes-unique-across-all-domains) |
| new grammar for a "special" case | [There is no grammar C](#33-there-is-no-grammar-c) |
| user, hostname, IP, secret or customer in a label or tag value | [Labels and tags](05-labels-and-tags.md) |
| resource without `cost-center`, `owner`, `env`, `capability` tags | [Labels and tags](05-labels-and-tags.md) |
| product as the cost axis instead of capability | [Labels and tags](05-labels-and-tags.md) |
| forge instance without a `default` runner visible to every organization | [Labels and tags](05-labels-and-tags.md) |
| `sock` or `host` CI runner registered at instance level | [Labels and tags](05-labels-and-tags.md) |
| commit hash or build number as a Kubernetes label | [Labels and tags](05-labels-and-tags.md) |
| label or tag used as an authorization input | [Labels and tags](05-labels-and-tags.md) |
| hyphen in a plane or domain code | [Hyphen parse rule](#11-hyphen-parse-rule) |
| owner, scope or env qualifier added to a name, or `--` used as a qualifier separator | [Hyphen parse rule](#11-hyphen-parse-rule) |
| tool or site in an infrastructure-as-code repository name (`ansible-roles`, `infra-onprem`) | [Object forms](#5-object-forms) |
| two domains in one infrastructure-as-code repository | [Object forms](#5-object-forms) |
| public name under `mess.systems` outside grammars A and B without an entry in `catalog/dns-exceptions.yaml` | [Grammar B: public](#32-grammar-b-public) |
| a third public sub-zone of the brand | [Grammar B: public](#32-grammar-b-public) |
| site code not in `catalog/sites.yaml`, or a site code with a city, address or provider | [Environments and sites](#44-environments-and-sites) |

## 11. Worked encodings

| Intake | FQDN | Application | Host |
|---|---|---|---|
| shared / iam / sso / Keycloak / prd | `sso.iam.shared.svc.mess.systems` | `shared-iam-keycloak` | `dc1-shared-iam-keycloak-prd-01` |
| eng / sdlc / git / Gitea / prd | `git.sdlc.eng.svc.mess.systems` | `eng-sdlc-gitea` | `dc1-eng-sdlc-gitea-prd-01` |
| corp / ai / gateway / agentgateway / prd | `gateway.ai.corp.svc.mess.systems` | `corp-ai-agentgateway` | `dc1-corp-ai-agentgateway-prd-01` |
| corp / ai / gateway / agentgateway / stg | `gateway.ai.corp.stg.svc.mess.systems` | `corp-ai-agentgateway` | `dc1-corp-ai-agentgateway-stg-01` |
| platform / data / docstore / MongoDB / prd | `docstore.data.platform.svc.mess.systems` | `platform-data-mongodb` | `dc1-platform-data-mongodb-prd-01..03` |
| shared / net / mesh / NetBird / prd | `mesh.net.shared.svc.mess.systems` | `shared-net-netbird` | `dc1-shared-net-netbird-prd-01` |
| ext / demo portal | `demo.apps.mess.systems` | `ext-gov-demo-portal` | `cld-ext-gov-portal-prd-01` |
| shopfront (product) / app | `app.shopfront.mess.systems` | `shopfront-api` | `cld-shopfront-api-prd-01` |

The mesh coordinator also has the public vanity name `netbird.mess.systems`, recorded in `catalog/dns-exceptions.yaml` ([grammar B: public](#32-grammar-b-public)).
