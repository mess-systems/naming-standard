# Labels and tags: cost tags, CI runner labels, Kubernetes, cloud, issue labels

> **Status:** v2.1, evolving. Accepted 2026-10-15. Extends [the ten metadata keys](01-naming-conventions.md#2-the-ten-metadata-keys) to every key/value label and tag.
> **Product-agnostic.** Products named here (Forgejo, GitHub, Kubernetes, Cloudflare, cloud.ru, OpenTofu) are illustrations; the rules apply to any platform with labels or tags.
> **A label or tag is never an authorization input**, the same rule as for names.

## Why

A newly created organization on a self-hosted forge could not run any CI job: its workflows asked for a runner label that existed only on runners registered to another organization. The label gave no hint of where the runner was visible, and there was no runner every organization could rely on. Jobs waited in the queue with no error. This part makes scope explicit, defines a default runner, and applies one grammar to cost tags, Kubernetes labels, cloud tags and issue labels.

## 1. Cross-cutting grammar

### 1.1 Characters

- Key: `[a-z][a-z0-9-]*`, with an optional prefix `<org-domain>/` where the platform supports prefixes (Kubernetes) and `<org>.` nowhere else.
- Value: `[a-z0-9][a-z0-9-]*`, a code from the standard's lists, a catalog ID, or a group ID.
- No uppercase, no spaces, no underscores in new keys. Underscores in the ten metadata keys (`data_class`) become hyphens in tags (`data-class`), because several platforms reject `_` in values and hyphen is the standard's separator.
- A token never starts with a digit, as [01 section 1](01-naming-conventions.md#1-character-rules-apply-to-every-family) requires.

### 1.2 Keys

| Key | Values | Source |
|---|---|---|
| `plane` | plane codes | [01 section 4.1](01-naming-conventions.md#41-planes) |
| `domain` | domain codes | [01 section 4.2](01-naming-conventions.md#42-domains) |
| `capability` | capability codes | [01 section 4.3](01-naming-conventions.md#43-capability-codes-unique-across-all-domains) |
| `product` | install code | catalog |
| `env` | `prd stg tst dev` | [01 section 4.4](01-naming-conventions.md#44-environments-and-sites) |
| `owner` | group ID, never a person | [04 section 5](04-identity-conventions.md#5-owners) |
| `data-class` | `public internal confidential restricted` | [01 section 2](01-naming-conventions.md#2-the-ten-metadata-keys) |
| `cost-center` | catalog code, e.g. `cc-platform` | see section 2 |
| `initiative` | catalog code, e.g. `ini-ai-gateway` | see section 2 |

### 1.3 Limits per platform

| Platform | Key limit | Value limit | Charset | Other |
|---|---|---|---|---|
| Kubernetes label | name 63, optional DNS-subdomain prefix up to 253 | 63, may be empty | alphanumerics, `-`, `_`, `.`; starts and ends with an alphanumeric | annotations: total size per object 256 KiB |
| Cloudflare Resource Tagging | 256 | 1024, may be empty | key: Unicode letters, digits, `_`, `.`, `-`; case-sensitive | beta: 10 000 tags per account; `PUT` replaces all tags of a resource |
| cloud.ru Tag Management Service (Advanced) | 36 | 43 | key: letters, digits, `_`, `-`; value also `.` | 10 tags per resource; one value per key |
| cloud.ru Evolution | to be confirmed | to be confirmed | to be confirmed | open note: limits not yet confirmed in public docs (checked 2026-10-15) |
| Forgejo issue/PR label | name, scope before the last `/` | | free text | color required; optional exclusive scope |
| GitHub issue/PR label | name up to 50 | | free text | color required |
| Forgejo / GitHub runner label | short token | | keep to `[a-z0-9-]` | matched exactly by `runs-on` |

The design limit is the smallest common one: **key up to 36 characters, value up to 43**. With the codes above every key/value pair fits.

### 1.4 Never in a label or tag

User names or handles, e-mail addresses, hostnames, IP addresses, serial numbers, secrets or secret paths, access group names used for authorization, customer names, and anything about family or children. The same list applies as for names. Tags are often visible to more people than the resource itself, for example in billing exports.

## 2. Cost tags (FinOps)

| Key | Required | Value | Example |
|---|---|---|---|
| `cost-center` | yes | catalog code `cc-<name>` | `cc-platform` |
| `owner` | yes | group ID | `role-platform-engineers` |
| `env` | yes | env code | `prd` |
| `capability` | yes | capability code | `inference` |
| `initiative` | no | catalog code `ini-<name>` | `ini-exo-pilot` |
| `plane` | no | plane code | `platform` |

- `owner` and `cost-center` are separate: the owner runs the resource, the cost center pays for it.
- `capability`, not `product`, is the cost axis. Spending by capability survives a product swap.
- A resource without the four required tags is reported by the cost check and is not created by IaC modules (OpenTofu modules validate the tags).
- Codes `cc-*` and `ini-*` are registered in the catalog before use. A tag value that is not in the catalog is an error.
- Shared resources get `owner` of the platform group and `cost-center` of the platform; allocation to consumers is a report, not a tag.

## 3. CI runner labels

Forgejo Actions and GitHub Actions both choose a runner by matching `runs-on` against runner labels. Runners are registered at instance, organization or repository level (on GitHub: enterprise, organization or repository, with runner groups). A job sees only runners registered at its own level or above.

### 3.1 Label form

| Label | Meaning | Example |
|---|---|---|
| `default` | baseline runner for ordinary jobs; registered at **instance** level and visible to every organization | `runs-on: default` |
| `<purpose>` | what the runner is for | `docker`, `review`, `gpu`, `build`, `deploy` |
| `<purpose>-<isolation>` | purpose plus isolation level when more than one exists | `docker-socketless`, `docker-sock` |
| `scope-<level>` | where the runner is registered, informative | `scope-instance`, `scope-org`, `scope-repo` |

Isolation codes, from strongest to weakest:

| Code | Meaning |
|---|---|
| `vm` | each job in its own VM or MicroVM |
| `socketless` | container jobs without access to the host container daemon (rootless builder) |
| `sock` | job has the host container socket; equals root on the runner host |
| `host` | job runs directly on the runner host |

### 3.2 Rules

- Every forge instance MUST provide at least one runner with label `default` at instance level. A new organization can then run CI on day one.
- A workflow that needs more than `default` names a purpose label. If the purpose label is not registered at instance level, the workflow's README says so.
- `sock` and `host` runners MUST NOT be registered at instance level. They are org or repo runners, because they give the job control over the host.
- `scope-*` labels are informative and never used in `runs-on`; the forge decides visibility.
- Runner names (not labels) follow the host form of the standard; labels never contain host names.
- On Forgejo the runner label also carries the execution backend after a colon (`docker-socketless:docker://<image>`). Only the part before the colon is the label name and follows this grammar.

## 4. Kubernetes labels and annotations

### 4.1 Labels

| Key | Value | Required |
|---|---|---|
| `app.kubernetes.io/name` | product code | yes |
| `app.kubernetes.io/instance` | application name from the standard's object forms | yes |
| `app.kubernetes.io/component` | component | where relevant |
| `app.kubernetes.io/part-of` | capability code | yes |
| `app.kubernetes.io/managed-by` | tool, e.g. `argocd`, `helm` | yes |
| `app.kubernetes.io/version` | version | no |
| `mess.systems/plane` | plane code | yes |
| `mess.systems/domain` | domain code | yes |
| `mess.systems/env` | env code | yes |
| `mess.systems/owner` | group ID | yes |
| `mess.systems/cost-center` | `cc-*` | yes |
| `mess.systems/data-class` | data class | where data is stored |

In the public standard the prefix is `mess.systems/`. An adopting organization replaces it with its own domain (`example.com/`).

### 4.2 Labels or annotations

- **Label:** short, stable, used in selectors, cost reports or policies: the keys above.
- **Annotation:** everything else: links to the catalog or runbook, `initiative`, descriptions, build metadata, change IDs, contact channels.
- A value that can change on every deploy (commit hash, build number) is never a label.

## 5. Cloud tags

- **Cloudflare:** native key/value tags through Resource Tagging. Use the keys of section 1.2 without prefix. Tags are case-sensitive, so lowercase only. Because `PUT` replaces all tags, tags are managed only by IaC, never by hand.
- **cloud.ru:** native key/value tags. In Tag Management Service a key is up to 36 characters and a value up to 43, with at most 10 tags per resource. The six keys of section 2 plus `data-class` fit in 7. Evolution limits are not yet confirmed (open note).
- Platforms without key/value tags use the existing `<key>-<value>` form (`env-prd`).

## 6. Issue and PR labels

### 6.1 Grammar

`<prefix>/<value>`. Forgejo treats the text before the last `/` as the scope and can make a scope exclusive. GitHub has no scopes, so the same names are used and exclusivity is checked by a workflow.

| Prefix | Exclusive | Color | Allowed values |
|---|---|---|---|
| `type` | yes | blue `#1d76db` | `bug feature docs chore decision research` |
| `stream` | no | green `#0e8a16` | catalog list of work streams |
| `horizon` | yes | purple `#5319e7` | `now next later` |
| `contour` | yes | orange `#d93f0b` | `public private` |
| `initiative` | no | gray `#6a737d` | `ini-*` codes from the catalog |

- One color per prefix, so a label's prefix is visible at a glance.
- Values use the same charset as section 1.1.
- `initiative/` values are the same codes as the cost tag `initiative`, so work and spending join on one key.

### 6.2 Legacy labels

Labels in the legacy form `prefix:value` (`type:bug`) are renamed to `prefix/value` (`type/bug`). Exclusive prefixes are enforced by Forgejo scoped labels and, on GitHub, by a workflow check.
