# Identity conventions: humans, agents, service accounts, groups, roles

> **Status:** v2, evolving. Combines a four-tier privileged-access model (T0 to T3) with the consumer and plane rules of the [naming conventions](01-naming-conventions.md).
> **Product-agnostic.** The rules apply to system categories: identity provider (IdP), secrets manager, mesh VPN, workload identity ([SPIFFE](https://spiffe.io/docs/latest/spiffe-about/overview/)), Kubernetes RBAC, database roles, LLM/MCP gateway clients, container registry robots, git forge and CI tokens. Products named in examples (Keycloak, OpenBao/Vault, SPIRE, Harbor, Gitea, Jenkins, Grafana, and others) are interchangeable illustrations.
> **One identity, one ID, everywhere.** The same string is the IdP username, the secrets-manager policy and machine role, the `x-user-id`, the DB role (with `_`), the OTel `service.name`.

## 1. Principles applied

| # | Rule |
|---|---|
| I1 | **Kind is visible in the ID.** Humans, admins, break-glass, service accounts, agents, workloads have different prefixes because they have different lifecycles, credentials and audit needs |
| I2 | **Agents are not service accounts.** An agent acts autonomously and often on behalf of a human; it gets its own kind, its own secrets node ([Path grammar](03-secrets-conventions.md#3-path-grammar)) and a mandatory `operator` (a human who answers for it) |
| I3 | **Groups grant, names describe.** A DNS label, a hostname, a path never authorises anything ([Grammar A: internal](01-naming-conventions.md#31-grammar-a-internal)) |
| I4 | **Three group prefixes only**: `tier-` (privilege level), `role-` (function), `app-` (access to one capability). Specificity grows from tier to role to app |
| I5 | **Separate admin account** for T0/T1 work (`<handle>-adm`), never the daily account |
| I6 | **Break-glass is an account, not a shared password**: `breakglass-<capability>-<NN>`, sealed, alerted, rotated after use |
| I7 | **Service account = application.** `svc-<plane>-<domain>-<product>`; one per install, one per env when envs exist |
| I8 | **Workload identity is [SPIFFE](https://github.com/spiffe/spiffe/blob/main/standards/SPIFFE-ID.md)**, the path mirrors the capability, and the trust domain is the company, not the DNS zone |
| I9 | **Every identity has `owner` and `expires`** (or `expires: none` justified). Reviews: t0 monthly, t1 quarterly, rest semi-annually |
| I10 | **Names are lowercase kebab**; `_` only where the store forbids `-` (Postgres, ClickHouse, env vars) |

## 2. Identity kinds

| Kind | ID form | Example | Credential | Lives in |
|---|---|---|---|---|
| Human | `<first>.<last>` or short handle | `jdoe` | password + WebAuthn | IdP |
| Human admin | `<handle>-adm` | `jdoe-adm` | WebAuthn only; no email/chat | IdP, tier groups |
| Break-glass | `breakglass-<capability>-<NN>` | `breakglass-sso-01` | sealed password in `<mount>/…/admin` | local to the system |
| Service account | `svc-<plane>-<domain>-<product>[-<env>]` | `svc-eng-sdlc-jenkins` | AppRole / OIDC client / SPIFFE | IdP (machine user) + secrets manager |
| Agent | `agent-<name>` | `agent-code-review`, `agent-docs-writer` | AppRole, later SPIFFE; gateway key | secrets manager, gateway `clients` |
| Human tool | `user-<handle>-<tool>` | `user-jdoe-ide` | gateway key issued to a human's tool | gateway `clients` only |
| Workload | `spiffe://mess.systems/<plane>/<domain>/<capability>` | `spiffe://mess.systems/corp/ai/gateway` | [X.509-SVID](https://github.com/spiffe/spiffe/blob/main/standards/X509-SVID.md) | SPIRE |
| Node | `spiffe://mess.systems/node/<host>` | `spiffe://mess.systems/node/dc1-corp-ai-litellm-prd-01` | join token / attestor | SPIRE |
| External (B2B) | `ext-<org>-<handle>` | `ext-acme-jdoe` | federated via `b2b.iam.shared` | IdP source |

Agents record `operator: <human>` and `scope: <capability list>` in their catalog entry; the gateway enforces `x-user-id = <agent id>` and `x-session-id`.

## 3. Groups

### 3.1 Tier groups (privilege)

| Group | Tier | Who | Reaches |
|---|---|---|---|
| `tier-t0-superadmin` | T0 | 1–2 `-adm` accounts | everything, `admin` items, alerted |
| `tier-t1-platform-ops` | T1 | platform + security engineers' `-adm` accounts | `shared/`, `platform/`, `eng/` control surfaces |
| `tier-t2-developer` | T2 | daily accounts of engineers | `eng/`, product planes, non-prod |
| `tier-t3-readonly` | T3 | observers, auditors, agents by default | list/read dashboards, catalogs |

### 3.2 Role groups (function)

| Group | Purpose |
|---|---|
| `role-platform-engineers` | run shared and platform control planes |
| `role-security-engineers` | detection, vulnerability management, identity hygiene |
| `role-developers` | build and ship products |
| `role-sre-observers` | read observability data, own alerts |
| `role-data-engineers` | own data pipelines, warehouse, catalogs |
| `role-agent-operators` | humans who own agents |

Legacy privilege groups in other schemes (`sg-*`, `*-admins`, `operators`) map onto the `tier-*` group with the same semantics; one prefix scheme remains.

### 3.3 App groups (access to one capability)

`app-<capability>-<access>`, where access is `user`, `editor`, or `admin`.

| Example | Grants |
|---|---|
| `app-dashboards-admin` | dashboards admin (e.g. Grafana) |
| `app-git-admin` | git forge site admin |
| `app-gateway-user` | may call `gateway.ai.corp` |
| `app-warehouse-editor` | warehouse write |

Provisioner defaults such as `app-<name>-operators` become `app-<capability>-admin`. Zone-suffixed providers (`grafana-public/-private/-admin`) are dropped: exposure is handled by a mesh group (see [mesh VPN groups](#4-mesh-vpn-groups)), and admin access by `app-dashboards-admin`.

## 4. Mesh VPN groups

| Group form | Contains | Example |
|---|---|---|
| `zone-<plane>` | resources (peers/routes) of that plane | `zone-shared`, `zone-corp`, `zone-eng`, `zone-platform`, `zone-ext` |
| `tier-*`, `role-*` | human peers, synced from the IdP | `role-developers` |
| `svc-<application>` | service peers | `svc-eng-sdlc-jenkins` |
| `egress-<plane>` | egress gateways | `egress-corp` |
| `site-<code>` | location | `site-dc1`, `site-cld` |

Policies: `<subject-group> → <zone-group>`. Typical legacy mappings: an all-access `admins` group becomes `tier-t0-superadmin`, a `devs` group becomes `role-developers`, and ad-hoc tag-style groups become the matching `tier-*` or `role-*` group.

## 5. Owners

`owner` metadata (see [metadata keys](01-naming-conventions.md#2-the-ten-metadata-keys)) is always a **group**, never a person: `role-platform-engineers`, `role-data-engineers`, `tier-t0-superadmin`. Agents' `operator` is the exception (a human).

## 6. IdP objects

| Object | Name | Example |
|---|---|---|
| Application slug | `<application>` ([Object forms](01-naming-conventions.md#5-object-forms)) | `shared-obs-grafana` |
| Application display name | product name | `Grafana` |
| Provider | `<application>-<protocol>` | `shared-obs-grafana-oidc`, `eng-sdlc-gitea-oidc` |
| Property mapping / scope | `<application>-<claim>` | `shared-obs-grafana-groups` |
| Outpost | `outpost-<plane>-<capability>` | `outpost-shared-ingress` |
| Flow | `flow-<purpose>` | `flow-admin-webauthn` |
| Source (federation) | `src-<vendor>` | `src-github` |

Object kinds follow common IdPs (Keycloak, Entra ID, Okta, …); map them to your product's equivalents.

Legacy slugs named after the product (`grafana`, `argocd`) move to the application form (`shared-obs-grafana`, `eng-sdlc-argocd`). Redirect URIs use canonical FQDNs only (see [single base URL](01-naming-conventions.md#6-single-base-url)).

## 7. Secrets manager (OpenBao / Vault)

Policy = identity ID; AppRole = identity ID; JWT role = group ID. The full rules are in the [policies](03-secrets-conventions.md#5-policies) and [auth roles and tokens](03-secrets-conventions.md#6-auth-roles-and-tokens) sections of the secrets conventions.

| Typical legacy | Target |
|---|---|
| policy `admin` | `tier-t0-superadmin` |
| policy `ops` | `tier-t1-platform-ops` |
| policy `developers` | `tier-t2-developer` |
| policy `read-only` | `tier-t3-readonly` |
| AppRole `<app>` / policy `<app>-read` | `svc-<plane>-<domain>-<product>` (one name) |
| AppRole / policy named after a bot | `agent-<name>` |
| policy `registry-read` (one foreign item) | `<identity-id>-<capability>-ro` (scoped read) |

## 8. SPIFFE / SPIRE

| Legacy (illustrative) | Target |
|---|---|
| trust domain `spiffe://corp.lan` | `spiffe://mess.systems` (non-prod: `spiffe://<env>.mess.systems`) |
| `spiffe://corp.lan/infra/llm-proxy` (repo folder) | `spiffe://mess.systems/corp/ai/gateway` |
| `spiffe://corp.lan/apps/doc-converter` | `spiffe://mess.systems/corp/data/convert` |
| `spiffe://corp.lan/node/vm042` | `spiffe://mess.systems/node/dc1-corp-ai-litellm-prd-01` |
| `spiffe://corp.lan/node/ws-jdoe-01` | `spiffe://mess.systems/node/ws-jdoe-01` (a workstation keeps its name; it is not a service host) |

Agents: `spiffe://mess.systems/corp/ai/agent-<name>`. Paths follow **capability codes**, never repository folders.

## 9. Gateway client identities

Key names in `corp/ai/gateway/prd/clients` and the `x-user-id` header are identity IDs from [identity kinds](#2-identity-kinds).

| Legacy field (illustrative) | Target ID | Kind |
|---|---|---|
| `codereview_bot` | `agent-code-review` | agent |
| `docs_bot` | `agent-docs-writer` | agent |
| `chat_ai` | `svc-corp-collab-mattermost` | service account |
| `tracing` | `svc-corp-ai-langfuse` | service account |
| `shopfront` | `svc-shopfront-api` | product service account |
| `ide` | `user-jdoe-ide` | human tool |

Env var names: `GATEWAY_CLIENT_KEY_<ID_UPPER_SNAKE>` (`GATEWAY_CLIENT_KEY_AGENT_CODE_REVIEW`). MCP targets: capability codes (`convert`, `cmdb`, `archrepo`, `data-catalog`), vendors `<vendor>-<service>` (`acmesearch-web`).

## 10. Kubernetes RBAC

| Object | Form | Legacy → target (illustrative) |
|---|---|---|
| ServiceAccount | `svc-<workload>` | `ci` → `svc-ci` |
| Role / ClusterRole for humans | `<group>-<scope>-<access>` | `view-all` → `role-developers-cluster-ro`; `sandbox-viewer` → `role-developers-sandbox-ro` |
| Role for a SA | `<sa>-<scope>-<access>` | `ci-read` → `svc-ci-workload-ro`; `ci-gitops` → `svc-ci-gitops-rw` |
| RoleBinding | `<role>--<subject>` | `role-developers-sandbox-ro--role-developers` |
| GitOps project (e.g. Argo CD) | `<plane>` or `<product>` | `default` → `eng`, product apps → `<product>` |
| Labels | `mess.systems/plane`, `mess.systems/owner`, … | |

RBAC subjects taken from the OIDC group claim are the `tier-*` and `role-*` groups, unchanged.

## 11. Database roles

Form: `<plane>_<domain>_<capability>_<access>` for capability-owned roles (`ro | rw | owner`), `svc_<plane>_<domain>_<product>` for consumers, `agent_<name>` for agents, `breakglass_<capability>` for local admins.

| Store | Legacy (illustrative) | Target |
|---|---|---|
| ClickHouse | `default` | disabled |
| ClickHouse | `writer` | `corp_data_warehouse_rw` |
| ClickHouse | `readonly` | `corp_data_warehouse_ro` |
| ClickHouse | `bi` (BI tool user) | `svc_corp_data_superset` |
| MongoDB | `admin` | `breakglass_docstore` |
| MongoDB | `bot` | `agent_docs_writer` |
| Postgres | per-app users (`my_app`) | `svc_<plane>_<domain>_<product>`; database `<plane>_<domain>_<capability>_<env>` |

## 12. Tokens, robots, credentials IDs

| System | Form | Example |
|---|---|---|
| Registry robot (e.g. Harbor) | `robot$<project>+<consumer-id>` | `robot$corp-ai+svc-eng-sdlc-jenkins` |
| Git forge token / deploy key | `<consumer-id>` (+ `--<purpose>`) | `svc-eng-sdlc-jenkins--clone` |
| CI credential ID | secrets path with `/` replaced by `-` | `eng-sdlc-ci-prd-packages` |
| Package registry token | `<consumer-id>` | `svc-eng-sdlc-jenkins` |
| Dashboards service account | `svc-<application>` | `svc-corp-ai-litellm` |
| SSH key comment | `<identity-id>@<host>` | `jdoe-adm@dc1-shared-infra-kvm-prd-01` |

## 13. Lifecycle

| Event | Rule |
|---|---|
| Create | intake ([Naming procedure](01-naming-conventions.md#9-naming-procedure)), then identity kind, groups, secrets-manager policy and role, and a catalog entry with `owner` and `expires` |
| Rotate | per `custom_metadata.rotation`; agents and tools 90d; service accounts 365d; break-glass after every use |
| Review | t0 monthly, t1 quarterly, t2/t3 semi-annual; agents with their operator |
| Leave / retire | in this order: disable in the IdP, revoke AppRole secret-ids, drop the DB role, remove the gateway client field, close the catalog entry. Never reuse an ID |

## 14. Refusals

- Group without one of the three prefixes; a fourth prefix.
- Tier and role in one group name (`platform-admins`).
- Product name inside a group (`grafana-admins`; use `app-dashboards-admin`).
- Exposure in a group or provider name (`-public`, `-private`, `-admin` provider).
- Agent registered as `svc-*` or a human's tool registered as an agent.
- Policy/AppRole/JWT-role name that is not an identity or group ID.
- Personal ID used for automation, or `-adm` account with mail/chat.
- Shared account with a shared password (use break-glass accounts).
- Underscore in an ID outside DB roles / env vars.
