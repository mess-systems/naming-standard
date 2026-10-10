# Worked example: migrating a fictional organisation

> **Status:** illustrative. Everything here is fictional: the organisation, hosts, services, and paths exist only to show how the [naming](01-naming-conventions.md), [secrets](03-secrets-conventions.md), and [identity](04-identity-conventions.md) conventions are applied together.
> **Domain substitution:** the standard uses the organisation domain `mess.systems`. This example uses **`northwind.example`** (reserved by [RFC 2606](https://www.rfc-editor.org/rfc/rfc2606) and [RFC 6761](https://www.rfc-editor.org/rfc/rfc6761)) to show that the company domain is a parameter: `svc.mess.systems` becomes `svc.northwind.example`, `spiffe://mess.systems` becomes `spiffe://northwind.example`, and so on.

## 1. Setting

Northwind Traders runs about a dozen services on a two-node hypervisor in its office (site `hq`) and one VM in a public cloud (site `cld`). Over five years it accumulated names like:

- `grafana.corp.lan`, `grafana-admin.corp.lan`: product names and exposure in the name;
- `git.corp.lan` and `gitea.corp.lan`: two names for one install;
- `vm042`, `srv-old-2`, `docker1`: hosts with no meaning;
- `*.int.corp.lan` vs `*.corp.lan`: an "internal" sub-zone that is really an access rule;
- one secrets-manager mount `secret/` with paths by vendor, by product, and by person.

`.lan` is not a reserved TLD and cannot get public-CA certificates, so the target internal zone is `svc.northwind.example` (split-horizon, not delegated publicly).

## 2. Zones

| Zone | Target | Grammar |
|---|---|---|
| Internal services | `svc.northwind.example` | A |
| Management hosts | `mgmt.northwind.example` | host names, not capabilities |
| Public ext | `apps.northwind.example` | B, brand as product |
| Brand | `www.northwind.example` | B |
| Product | `app.shopfront.example` | B |

## 3. Services: intake and encoding

Intake follows the [naming procedure](01-naming-conventions.md#9-naming-procedure): plane, domain, capability, product, env. All services here are production, so grammar A omits env while hosts, schemas, and secrets write `prd`.

| Legacy name | Intake (plane / domain / capability / product) | Target FQDN | Application | Owner |
|---|---|---|---|---|
| `grafana.corp.lan`, `grafana-admin.corp.lan` | shared / obs / dashboards / Grafana | `dashboards.obs.shared.svc.northwind.example` | `shared-obs-grafana` | `role-sre-observers` |
| `prometheus.corp.lan` | shared / obs / metrics / Prometheus | `metrics.obs.shared.svc.northwind.example` | `shared-obs-prometheus` | `role-sre-observers` |
| `keycloak.int.corp.lan` | shared / iam / sso / Keycloak | `sso.iam.shared.svc.northwind.example` | `shared-iam-keycloak` | `tier-t1-platform-ops` |
| `vault.int.corp.lan` | shared / iam / secrets / OpenBao | `secrets.iam.shared.svc.northwind.example` | `shared-iam-openbao` | `tier-t0-superadmin` |
| `git.corp.lan`, `gitea.corp.lan` | eng / sdlc / git / Gitea | `git.sdlc.eng.svc.northwind.example` | `eng-sdlc-gitea` | `role-platform-engineers` |
| `jenkins.corp.lan` | eng / sdlc / ci / Jenkins | `ci.sdlc.eng.svc.northwind.example` | `eng-sdlc-jenkins` | `role-platform-engineers` |
| `registry.corp.lan` | eng / sdlc / oci / Harbor | `oci.sdlc.eng.svc.northwind.example` | `eng-sdlc-harbor` | `role-platform-engineers` |
| `pg01.corp.lan` | shared / data / sql / PostgreSQL | `sql.data.shared.svc.northwind.example` | `shared-data-postgres` | `role-platform-engineers` |
| `chat.corp.lan` | corp / collab / chat / Mattermost | `chat.collab.corp.svc.northwind.example` | `corp-collab-mattermost` | `role-platform-engineers` |
| `wiki.corp.lan` | corp / collab / wiki / Wiki.js | `wiki.collab.corp.svc.northwind.example` | `corp-collab-wikijs` | `role-developers` |
| `llm.corp.lan`, `llm-ui.corp.lan` | corp / ai / gateway / agentgateway | `gateway.ai.corp.svc.northwind.example` (UI = `/ui` path) | `corp-ai-agentgateway` | `role-agent-operators` |
| `demo.corp.lan` (public) | ext / gov / demo / demo portal | `demo.apps.northwind.example` | `ext-gov-demo-portal` | `role-developers` |

Decisions made on the way:

- `grafana-admin` is not a second name. Admin access becomes the group `app-dashboards-admin` (see [app groups](04-identity-conventions.md#33-app-groups-access-to-one-capability)), and the service keeps a single FQDN (see [grammar A](01-naming-conventions.md#31-grammar-a-internal) and [single base URL](01-naming-conventions.md#6-single-base-url)).
- `gitea.corp.lan` becomes a 90-day redirect to the canonical FQDN, then is removed (see [single base URL](01-naming-conventions.md#6-single-base-url)).
- `*.int.corp.lan` encoded exposure. All names move to grammar A; who may reach them is decided by a mesh or IdP group (see [mesh VPN groups](04-identity-conventions.md#4-mesh-vpn-groups)).
- The LLM UI is a path on the gateway, not a second FQDN (one install, one name).

## 4. Hosts

Form: `<site>-<plane>-<domain>-<product>-<env>-<NN>` (see [object forms](01-naming-conventions.md#5-object-forms)). Management interfaces live under `mgmt.northwind.example`.

| Legacy host | Runs | Target host |
|---|---|---|
| `hv1`, `hv2` | hypervisor nodes | `hq-shared-infra-pve-prd-01`, `hq-shared-infra-pve-prd-02` |
| `vm042` | Grafana + Prometheus | `hq-shared-obs-grafana-prd-01` (Prometheus is a second application on the same host) |
| `srv-old-2` | Gitea | `hq-eng-sdlc-gitea-prd-01` |
| `docker1` | Jenkins | `hq-eng-sdlc-jenkins-prd-01` |
| `pg01` | PostgreSQL | `hq-shared-data-postgres-prd-01` |
| `cloud-vm-1` | demo portal | `cld-ext-gov-portal-prd-01` |
| `ws-jdoe-01` | a workstation | unchanged; workstations are not service hosts |

## 5. Secrets and identities

One mount per plane replaces `secret/` (see [mounts](03-secrets-conventions.md#2-mounts)):

| Legacy (`secret/`) | Target | Rule |
|---|---|---|
| `grafana/oidc` | `shared/obs/dashboards/prd/oidc` | capability, not product (see [secrets refusals](03-secrets-conventions.md#9-refusals)) |
| `postgres/root` | `shared/data/sql/prd/admin` | break-glass item, t0 only (rule [S6](03-secrets-conventions.md#1-principles-applied)) |
| `jenkins/registry` | `eng/sdlc/ci/prd/oci` | consumer copy, named after the capability it unlocks |
| `llm/acmeai` | `corp/ai/gateway/prd/provider-acmeai` | vendor is an item, not a node (rule [S4](03-secrets-conventions.md#1-principles-applied)) |
| `users/jdoe/*` | **refused** | personal secrets go to the password manager (rule [S5](03-secrets-conventions.md#1-principles-applied)) |

Identities and groups (see the [identity conventions](04-identity-conventions.md)):

| Legacy | Target | Kind |
|---|---|---|
| `jdoe` (daily + admin) | `jdoe` and `jdoe-adm` | human, human admin (rule [I5](04-identity-conventions.md#1-principles-applied)) |
| shared `root` on Postgres | `breakglass-sql-01` | break-glass account |
| `jenkins` service user | `svc-eng-sdlc-jenkins` | service account |
| `release-bot` | `agent-release-notes`, operator `jdoe` | agent |
| group `admins` | `tier-t0-superadmin` | tier group |
| group `devs` | `role-developers` | role group |
| group `grafana-admins` | `app-dashboards-admin` | app group |

## 6. Certificates

Per-name ACME is the default. Only endpoints that cannot use ACME get a pre-issued wildcard, one per used `<domain>.<plane>` pair (see [TLS](01-naming-conventions.md#7-tls)):

```
*.obs.shared.svc.northwind.example
*.sdlc.eng.svc.northwind.example
```

Public: `*.apps.northwind.example` and `*.shopfront.example` via DNS-01.

## 7. Names refused during the migration

- `grafana-public.apps.northwind.example`: exposure in a name; internal tools are not published on the ext zone.
- `gitea.sdlc.eng.svc.northwind.example`: product as leftmost label.
- `ci.sdlc.eng.prd.svc.northwind.example`: env in a prod DNS name.
- `shared/obs/grafana/oidc`: no env, product as a node.
- group `platform-admins`: tier and role in one name.

## 8. Cutover order

1. Register every target in the catalog (owner, tier, data_class, exposure).
2. Stand up the internal zone and CA; issue certificates for the new names.
3. Add new FQDNs alongside legacy ones; legacy names become redirects (90 days).
4. Create groups and identities; migrate secrets mount by mount, then disable `secret/`.
5. Rename hosts during normal maintenance windows.
6. Remove redirects and legacy groups; close the migration table.
