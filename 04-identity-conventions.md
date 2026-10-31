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
| Node | `spiffe://mess.systems/node/<host>` | `spiffe://mess.systems/node/dc1-corp-ai-agentgateway-prd-01` | join token / attestor | SPIRE |
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

### 3.4 Product access groups

App groups describe access to a capability of the corporate contour. A product of the product contour ([deployment and tenants](07-deployment-and-tenants.md)) has no capability, so access to it is described by its product code.

| Form | When | Example |
|---|---|---|
| `app-<product>-<access>` | access to the whole product | `app-arch-user` |
| `app-<product>-<service>-<access>` | access to one service of the product | `app-arch-store-editor` |

- `<access>` comes from the same list: `user`, `editor`, `admin`.
- A product code is never equal to a [capability code](01-naming-conventions.md#43-capability-codes-unique-across-all-domains), so that `app-<code>-user` has one reading; the check runs against `catalog/products.yaml`.
- A product code is a code of the product contour, not the name of a vendor product, so the refusal of vendor product names in groups still holds.
- Groups of a product's customers (tenants) are never created in the staff IdP; they live in the IdP of the product and follow the [tenant keys](07-deployment-and-tenants.md#5-tenants).

## 4. Mesh VPN groups

| Group form | Contains | Example |
|---|---|---|
| `zone-<plane>` | resources (peers/routes) of that plane | `zone-shared`, `zone-corp`, `zone-eng`, `zone-platform`, `zone-ext` |
| `tier-*`, `role-*` | human peers, synced from the IdP | `role-developers` |
| `svc-<application>` | service peers | `svc-eng-sdlc-jenkins` |
| `egress-<plane>` | egress gateways | `egress-corp` |
| `site-<code>` | location | `site-dc1`, `site-cld` |
| `router-<site>` | routing peers into the network of a site, for devices without a mesh agent | `router-dc1` |

A router is not an egress gateway: an egress gateway lets traffic out to the internet, a router lets mesh peers into the local network of a site.

Policies: `<subject-group> -> <target-group>`, where the target is `zone-<plane>` or the narrower `svc-<application>`. Typical legacy mappings: an all-access `admins` group becomes `tier-t0-superadmin`, a `devs` group becomes `role-developers`, and ad-hoc tag-style groups become the matching `tier-*` or `role-*` group.

### 4.1 Mesh policies, rules and posture checks

| Object | Form | Example |
|---|---|---|
| Policy | `<subject-group> -> <target-group>` (ASCII arrow with a space on each side) | `role-platform-engineers -> svc-shared-data-postgres` |
| Policy split by protocol | the above + ` (<protocol>)` | `role-developers -> svc-shared-net-dns (udp)` |
| Rule inside a policy | the [IANA service name](https://www.iana.org/assignments/service-names-port-numbers/) of the port; several names joined with `-` | `postgresql`, `https`, `ssh`, `ssh-https` |
| Rule for a port with no IANA name, or a port that does not serve its IANA service | `<protocol>-<port>` | `tcp-9100`, `tcp-8200` |
| Posture check | `posture-<what>-<condition>` | `posture-client-current`, `posture-os-supported` |

- One policy per pair of groups. The protocol suffix is used only when the mesh product allows one protocol per rule and the pair needs two.
- Direction is a property of the rule (one-way by default), not part of the name.
- The built-in policy `Default` keeps its product name and is disabled. No policy has the built-in `All` group as subject or target.

### 4.2 Mesh networks, resources and keys

| Object | Form | Example |
|---|---|---|
| Network of a site | `site-<site>` (same as the site group) | `site-dc1` |
| Network resource: one host | the host name ([object forms](01-naming-conventions.md#5-object-forms)) | `dc1-shared-net-dns-prd-01` |
| Network resource: a service on several hosts | `<site>-<application>` | `dc1-shared-net-dns` |
| Network resource: a subnet | `<site>-<plane>-<purpose>` | `dc1-shared-mgmt` |
| Setup key | the host name it is issued for; one-off | `dc1-shared-data-postgres-prd-01` |
| Setup key for a group of machines (ephemeral peers only) | `<application>-<env>-ephemeral` | `platform-build-ci-runner-prd-ephemeral` |
| Service user of the mesh for infrastructure as code | `svc-<iac-repo>` ([object forms](01-naming-conventions.md#5-object-forms)) | `svc-shared-net-iac` |

Addresses, subnets and VLAN numbers never go into a mesh name; they live in the description of the resource and in the inventory.

### 4.3 Mesh DNS

| Object | Form | Example |
|---|---|---|
| Nameserver group | the zone with dots replaced by hyphens, then the site | `svc-mess-systems-dc1` |
| Search domain | only `svc.mess.systems`; no per-site search domains | `svc.mess.systems` |

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
| Realm (or tenant) of the staff IdP | `<org>`, one per organisation | `mess-systems` |
| Realm of a product IdP | `<product>-<env>` | `arch-prd`, `arch-stg` |
| OIDC client of an agent | the agent ID | `agent-code-review` |
| OIDC client of a human's tool (CLI agent, IDE) | the tool's account ID | `user-jdoe-cursor` |
| Token audience of a target service | the application of the target service | `shared-data-postgres`, `corp-infra-kubernetes-mcp-server` |

Object kinds follow common IdPs (Keycloak, Entra ID, Okta, …); map them to your product's equivalents.

- A human's tool (`user-<handle>-<tool>`) acts on behalf of a human and with that human's groups, narrowed. An agent (`agent-<name>`) acts on its own and has an operator. The choice depends on who starts the action, not on the tool product.
- In a token exchange ([RFC 8693](https://www.rfc-editor.org/rfc/rfc8693)) the subject is the human and the actor (`act`) is the client of the tool or the agent, named as in the table above.

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
| `spiffe://corp.lan/node/vm042` | `spiffe://mess.systems/node/dc1-corp-ai-agentgateway-prd-01` |
| `spiffe://corp.lan/node/ws-jdoe-01` | `spiffe://mess.systems/node/std-lt-a1b2c3` (an [endpoint name](06-endpoint-conventions.md), never a user handle; only for fully managed, attested devices; BYOD gets no node identity) |

Agents: `spiffe://mess.systems/corp/ai/agent-<name>`. Paths follow **capability codes**, never repository folders.

The product contour has its own trust domains for prod, non-prod and sandbox; see [07 SPIFFE](07-deployment-and-tenants.md#9-spiffe).

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

| Object | Form | Legacy and target (illustrative) |
|---|---|---|
| ServiceAccount | `svc-<workload>` | `ci` becomes `svc-ci` |
| Role / ClusterRole for humans | `<group>-<scope>-<access>` | `view-all` becomes `role-developers-cluster-ro`; `sandbox-viewer` becomes `role-developers-sandbox-ro` |
| Role for a SA | `<sa>-<scope>-<access>` | `ci-read` becomes `svc-ci-workload-ro`; `ci-gitops` becomes `svc-ci-gitops-rw` |
| RoleBinding | `<role>--<subject>` | `role-developers-sandbox-ro--role-developers` |
| GitOps project (e.g. Argo CD) | `<plane>` or `<product>` | `default` becomes `eng`, product apps become `<product>` |
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

### 11.1 Temporary database users

Temporary database users are issued by the database engine of the secrets manager ([engines other than kv](03-secrets-conventions.md#21-engines-other-than-kv)). The name says how, who, with which role and when access was obtained, so a line of the database log can be read without the audit log of the secrets manager, and the audit log confirms it.

```
v_<auth>_<identity>_<role>_<ts>_<rand6>
```

| Part | Meaning | Example |
|---|---|---|
| `v_` | marks a temporary user | `v_` |
| `<auth>` | how the requester logged in to the secrets manager, a code from the table below | `oidc` |
| `<identity>` | ID of the human, tool or agent ([identity kinds](#2-identity-kinds)) with `-` replaced by `_` | `jdoe`, `user_jdoe_cursor`, `agent_code_review` |
| `<role>` | the `NOLOGIN` database role the user is a member of | `eng_sdlc_git_ro` |
| `<ts>` | time of issue in UTC, `YYYYMMDDtHHMMSSz`, as for [snapshots](08-operations-objects.md#3-backups-and-snapshots) | `20261031t020000z` |
| `<rand6>` | 6 characters `[a-z0-9]` | `k7m2qa` |

| Auth mount ([mounts](03-secrets-conventions.md#2-mounts)) | `<auth>` |
|---|---|
| `auth/jwt-<idp>` (humans and CI via OIDC) | `oidc` |
| `auth/jwt-spire` | `spire` |
| `auth/kubernetes-<cluster>` | `k8s` |
| `auth/approle` | `approle` |

- Only `[a-z0-9_]`, so the name needs no quoting in SQL, like the other database role names.
- At most 63 characters (the PostgreSQL limit). With `<auth>` = `oidc` the fixed part takes 32 characters, which leaves 31 for `<identity>` and `<role>` together (28 for `approle`).
- If the name does not fit, `<identity>` is shortened; the role, the time and the random part are never shortened. Truncating the finished name as a whole (`truncate 63`) is refused, because it cuts off the time and the random part.
- A temporary user never owns objects and never gets DDL rights; DDL runs as the `<…>_owner` role through a pipeline.
- Examples: `v_oidc_jdoe_eng_sdlc_git_ro_20261031t020000z_k7m2qa` (51 characters), `v_oidc_user_jdoe_cursor_eng_sdlc_git_ro_20261031t020000z_k7m2qa` (63).

Template for OpenBao (`username_template` of the connection), for `auth/jwt-keycloak` with `user_claim = preferred_username`:

```
{{ printf "v_%s_%s_%s_%s" (.DisplayName | replace "jwt-keycloak-" "oidc-" | replace "-" "_" | truncate 21) (.RoleName) (timestamp "20060102t150405z") (random 6 | lowercase) }}
```

`truncate 21` (`oidc_` plus 16 characters of `<identity>`) fits roles of up to 15 characters; a longer role needs a smaller number. Check the template on a test connection: the time in the database log must match the UTC time of issue in the audit log.

Comparison with the default template of OpenBao (`v-%s-%s-%s-%s` with `random 20`, `unix_time` and `truncate 63` on the whole name):

| Property | Default template | This standard |
|---|---|---|
| Auth method | derived from the mount prefix | a code from the table |
| Time | Unix time, 10 digits, at the end | UTC `YYYYMMDDtHHMMSSz` before the random part: readable and sortable |
| Separator | `-`, which needs quoting in SQL | `_`, like the other database role names |
| Random part | 20 characters, mixed case | 6 characters `[a-z0-9]`; time plus random part make the name unique |
| Longer than 63 | the end of the name is cut, with the time and the random part | `<identity>` is shortened |

## 12. Tokens, robots, credentials IDs

| System | Form | Example |
|---|---|---|
| Registry robot (e.g. Harbor) | `robot$<project>+<consumer-id>` | `robot$corp-ai+svc-eng-sdlc-jenkins` |
| Git forge token / deploy key | `<consumer-id>` (+ `--<purpose>`) | `svc-eng-sdlc-jenkins--clone` |
| CI credential ID | secrets path with `/` replaced by `-` | `eng-sdlc-ci-prd-packages` |
| Package registry token | `<consumer-id>` | `svc-eng-sdlc-jenkins` |
| Dashboards service account | `svc-<application>` | `svc-corp-ai-agentgateway` |
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
- Mesh group outside the forms of [mesh VPN groups](#4-mesh-vpn-groups) (`admins`, `servers`, `vpn-users`).
- Mesh policy with the built-in `All` group as subject or target ([mesh policies](#41-mesh-policies-rules-and-posture-checks)).
- Address, subnet or VLAN number in the name of a mesh object ([mesh networks, resources and keys](#42-mesh-networks-resources-and-keys)).
- Product code equal to a capability code ([product access groups](#34-product-access-groups)).
- Temporary database user outside the form of [temporary database users](#111-temporary-database-users) (no auth code or time, with `-`, truncated as a whole to 63) or with DDL rights.
