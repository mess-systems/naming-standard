# 08. Operations objects

Forms for the objects that appear while systems run: branches and tags, CI jobs, backups, hypervisor guests, gateway routes, DNS records and PostgreSQL objects. The axes and the characters are those of the [naming conventions](01-naming-conventions.md); there is no new grammar.

## 1. Git branches and tags

| Object | Form | Example |
|---|---|---|
| Default branch | `main` | `main` |
| Working branch | `<identity-id>/<topic>` | `jdoe/pg-access`, `user-jdoe-cursor/pg-access`, `agent-code-review/fix-typo` |
| Working branch for an issue | `<identity-id>/<issue>-<topic>` | `jdoe/142-pg-access` |
| Release maintenance branch | `release/v<X>.<Y>` | `release/v1.4` |
| Release tag | `v<X>.<Y>.<Z>`, immutable, as for [container images](07-deployment-and-tenants.md#125-container-images-and-registry) | `v1.4.0` |
| Pre-release tag | `v<X>.<Y>.<Z>-rc.<n>` ([SemVer](https://semver.org/)) | `v1.4.0-rc.1` |

- `<identity-id>` is an ID from [identity kinds](04-identity-conventions.md#2-identity-kinds): a human, a human's tool or an agent, so the branch shows who created it.
- `<topic>` uses `a-z0-9-`, is at most 40 characters long, and never contains a tool, host, customer or secret.
- The kind of change (feature, fix, docs) is a pull request label ([issue and PR labels](05-labels-and-tags.md#6-issue-and-pr-labels)), not part of the branch name.
- Agents and humans' tools do not push to `main` or `release/*`; this is a branch protection rule, not a naming rule.

## 2. CI and scheduled jobs

### 2.1 Workflows and jobs

| Object | Form | Example |
|---|---|---|
| Workflow file | `<purpose>.yml` | `ci.yml`, `release.yml`, `iac-plan.yml`, `iac-apply.yml` |
| Job ID | `<verb>[-<object>]` | `lint`, `test`, `build-image`, `plan`, `apply` |
| Deployment environment | the env code ([environments and sites](01-naming-conventions.md#44-environments-and-sites)) | `prd`, `stg` |
| Artifact | `<application>-<version>[-<platform>]` | `eng-sdlc-forgejo-v1.4.0-linux-amd64` |

### 2.2 Runners

Runner labels follow [CI runner labels](05-labels-and-tags.md#3-ci-runner-labels); a runner is named by the host form or as the component `ci-runner` ([infrastructure as code and runners](07-deployment-and-tenants.md#127-infrastructure-as-code-and-runners)). There are no new forms.

### 2.3 Scheduled jobs (cron, systemd timer, CronJob)

| Object | Form | Example |
|---|---|---|
| Job | `<application>-<action>[-<schedule>]` | `shared-data-postgres-backup-daily` |
| Kubernetes CronJob | the same without the plane, when the namespace already carries it | `postgres-backup-daily` |
| `<schedule>` | `hourly`, `daily`, `weekly`, `monthly`, or omitted | `daily` |

## 3. Backups and snapshots

| Object | Form | Example |
|---|---|---|
| Backup repository (repository, datastore, bucket) | the bucket form: `<plane>-infra-backup-<env-or-class>` | `shared-infra-backup-prd` |
| Backup job | `<application>-<env>-<schedule>` | `shared-data-postgres-prd-daily` |
| Snapshot | `<application>-<env>-<timestamp>` | `shared-data-postgres-prd-20261031t020000z` |
| `<timestamp>` | UTC, ISO 8601 basic format, lower case: `YYYYMMDDtHHMMSSz` | `20261031t020000z` |
| Snapshot tags | `application`, `env`, `kind` (`full`, `incr`, `wal`), `retention` (`daily`, `weekly`, `monthly`) | `kind=full` |

- A snapshot name has no host: the snapshot belongs to the application, not to a machine.
- Backup encryption keys follow the [path grammar](03-secrets-conventions.md#3-path-grammar) of the secrets conventions: `<mount>/infra/backup/<env>/<application>`.

## 4. Hypervisor guests

| Object | Form | Example |
|---|---|---|
| VM or container name | the host name ([object forms](01-naming-conventions.md#5-object-forms)) | `dc1-shared-data-postgres-prd-01` |
| Guest tags | the keys of [labels and tags](05-labels-and-tags.md) (`plane`, `domain`, `capability`, `env`, `owner`) | `plane=shared` |
| Resource pool | `<plane>` or `<plane>-<env-class>` | `shared`, `eng-nonprod` |
| Image template | `tpl-<os>-<version>` | `tpl-debian-13` |

The numeric ID of a guest (VM ID, container number) is inventory, not a name: it is never used in DNS, groups, secret paths or documents. If ranges per plane are needed, they are recorded in the catalog of the site, not in the standard.

## 5. API gateways

| Object | Form | Example |
|---|---|---|
| Route on the public surface of a product | `<product>-<service>-<version>` | `x-store-v1` |
| Route to an internal capability | `<application>[-<purpose>]` | `corp-ai-gateway-mcp` |
| Upstream (backend) | `<application>-<env>` or `<product>-<service>-<env>` | `x-store-prd` |
| Consumer | the client ID from [gateway client identities](04-identity-conventions.md#9-gateway-client-identities) | `svc-x-records-store`, `agent-code-review` |
| Listener | `<protocol>-<port>` | `https-443` |
| MCP target, LLM route prefix | unchanged, see [object forms](01-naming-conventions.md#5-object-forms) | `k8s`, `dashboards` |

## 6. DNS records

| Record | Form | Example |
|---|---|---|
| Internal service | `A`/`AAAA`, or `CNAME` to the canonical grammar-A name | `sql.data.shared.svc.mess.systems` |
| Host | `<host>.mgmt.mess.systems`: the management zone is internal like `svc.mess.systems`, holds hosts only, and the site is already in the host name | `dc1-shared-data-postgres-prd-01.mgmt.mess.systems` |
| Product | `CNAME` of a surface to the proxy or load balancer of the product | `arch.x.mess.systems` |
| Product wildcard | one per product domain and one per non-production env: `*.<product>.x.mess.systems`, `*.<env>.<product>.x.mess.systems` | `*.arch.x.mess.systems` |
| Ownership challenge (ACME, services) | `_<purpose>.<name>` `TXT` | `_acme-challenge.arch.x.mess.systems` |
| CAA | on the brand zone and its sub-zones | `x.mess.systems CAA 0 issue "<ca>"` |

- A wildcard covers exactly one label ([RFC 4592](https://www.rfc-editor.org/rfc/rfc4592)): `*.x.mess.systems` matches `arch.x.mess.systems` but not `api.stg.arch.x.mess.systems`, which needs its own wildcard or a record per name.
- Every public record outside grammars A and B is listed in `catalog/dns-exceptions.yaml` ([grammar B: public](01-naming-conventions.md#32-grammar-b-public)).

## 7. PostgreSQL objects

| Object | Form | Example |
|---|---|---|
| Cluster, corporate contour | the application: `<plane>-<domain>-<product>` | `shared-data-postgres` |
| Cluster, product contour | [environment class](07-deployment-and-tenants.md#121-environment-class) | `x-records-store-nonprod` |
| Database, schema | [object forms](01-naming-conventions.md#5-object-forms) | `eng_sdlc_git_prd` |
| Role, temporary user | [database roles](04-identity-conventions.md#11-database-roles), [temporary database users](04-identity-conventions.md#111-temporary-database-users) | `eng_sdlc_git_ro`, `v_oidc_jdoe_eng_sdlc_git_ro_20261031t020000z_k7m2qa` |
| Replication slot | `<consumer>_<purpose>` (snake_case) | `svc_shared_infra_backup_wal` |
| Publication, subscription | `<database>_<purpose>` | `eng_sdlc_git_prd_cdc` |

## 8. Refusals (reject the name if…)

| Smell | Rule broken |
|---|---|
| branch without `<identity-id>/`, or with a tool name instead of an ID (`cursor/fix`) | [Git branches and tags](#1-git-branches-and-tags) |
| release tag rewritten after publication | [Git branches and tags](#1-git-branches-and-tags) |
| host or IP address in the name of a snapshot, job or route | [Backups and snapshots](#3-backups-and-snapshots), [API gateways](#5-api-gateways) |
| VM ID or container number as a name or part of a name | [Hypervisor guests](#4-hypervisor-guests) |
| a name two labels below a wildcard that relies on that wildcard | [DNS records](#6-dns-records) |
| public DNS record outside the grammars without an entry in the exceptions register | [DNS records](#6-dns-records) |
