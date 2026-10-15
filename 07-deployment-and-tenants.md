# 07. Deployment and tenants

The rules for the **product contour**: the cloud-native products that mess.systems builds, runs and sells, how they are deployed across providers, regions and cells, and how tenants are identified. All examples use the fictional company mess.systems and its fictional **product X** (`x`), a simple records application with login, subscription, an admin console, an API with webhooks and payments.

This part was shaped by an external review of the standard; thanks to the reviewer.

## 1. Two contours

mess.systems has two contours. They share the character rules, the "names never authorize" rule, the catalog-first procedure, the secrets and identity conventions, and the label grammar of [05](05-labels-and-tags.md). They differ in what a name is made of.

| | Corporate contour | Product contour |
|---|---|---|
| What it covers | Internal services, the `corp`, `eng`, `shared` and `ext` planes, employee devices | Products sold to customers, their environments, cells and tenants |
| Rules | [01](01-naming-conventions.md) to [06](06-endpoint-conventions.md), unchanged | This part, on top of the shared rules |
| Logical identity | `<capability>.<domain>.<plane>` | `<service>.<domain>.<product>` |
| Uniqueness of the leftmost code | Capability code unique in the whole company | Service unique within its product |
| Internal DNS, production | env omitted: `git.sdlc.eng.svc.mess.systems` | env always written: `store.records.x.prd.svc.mess.systems` |
| Public DNS | `www.mess.systems`, `<capability>.apps.mess.systems` | `api.<product-domain>`, `api.stg.<product-domain>` |
| Cost axis | `capability` | `product`, `domain`, `service` |
| SPIFFE trust domain | `mess.systems`, non-prod `<env>.mess.systems` | `product.mess.systems`, `nonprod.product.mess.systems`, `sandbox.product.mess.systems` |

**How they coexist.**

- An object belongs to exactly one contour. The catalog records it as `contour: corp` or `contour: product`.
- A product is already a plane in the corporate contour ([01 section 4.1](01-naming-conventions.md#41-planes): `<product>`). The product contour keeps that: the third label of an internal product name is the product code, and a product code is never one of `shared`, `corp`, `eng`, `ext`.
- Shared services that every product uses (build, registry, product-side observability) are the product **`platform`**, the same code and meaning as the `platform` plane.
- A product uses corporate services (SSO for staff, the forge, the secrets manager) under their corporate names. A corporate service never takes a product-contour name.
- The asymmetry in environments is deliberate: the corporate contour keeps its short production names; the product contour writes `prd` so that every name parses the same way in every environment.

## 2. Product, domain, service, implementation

| Concept | Meaning | Product X example |
|---|---|---|
| `product` | What a customer buys | `x` |
| `domain` | Bounded area inside the product | `records`, `access`, `billing`, `integration`, `admin` |
| `service` | Stable logical service; outlives its implementation | `store`, `export`, `login`, `session`, `subscription`, `payment`, `webhook`, `console` |
| `component` | Conditional: separate deployables of one service | `api`, `worker`, `migrate` |
| `implementation` | Replaceable technology; inventory, never in a name | `postgresql`, `keycloak` |

- A service code is unique **within its product**, not across the company. `x` and another product may both have `login`.
- A domain code may reuse a corporate domain code only with the same meaning (`iam` means identity in both contours). Otherwise it is product-local.
- The implementation is metadata (`implementation` key), never a DNS label, a SPIFFE path segment or an OTel service name. Replacing PostgreSQL does not rename `store`.

Product X, full service list:

| Domain | Services |
|---|---|
| `records` | `store`, `export` |
| `access` | `login`, `session` |
| `billing` | `subscription`, `payment` |
| `integration` | `webhook` |
| `admin` | `console` |

## 3. Environments and DNS

| Env | Code | Contour |
|---|---|---|
| production | `prd` | both |
| staging | `stg` | both |
| test | `tst` | both |
| development | `dev` | both |
| sandbox | `sbx` | product only: short-lived, no customer data, own trust domain |

Internal names in the product contour:

```
<service>.<domain>.<product>.<env>.svc.mess.systems            # product-wide
<service>.<domain>.<cell>.<product>.<env>.svc.mess.systems     # cell-bound
```

- `store.records.x.prd.svc.mess.systems`, `store.records.c01.x.prd.svc.mess.systems`, `login.access.x.stg.svc.mess.systems`.
- `prd` is always written. The corporate rule "env omitted in prod" ([01 section 3.1](01-naming-conventions.md#31-grammar-a-internal)) is not changed and does not apply here.
- A component that needs its own name adds it to the service label: `store-worker.records.x.prd.svc.mess.systems`.

Public names stay clean:

```
api.<product-domain>                 # production
api.stg.<product-domain>             # non-production surface
app.<product-domain>, docs.<product-domain>, status.<product-domain>
```

For product X with the placeholder domain `x.example`: `api.x.example`, `app.x.example`, `api.stg.x.example`. Public names never carry domain, service, cell, region, provider or tenant. Routing a request to a cell is the job of the routing layer, not of the public name.

## 4. Deployment keys

| Key | Meaning | Values | In names |
|---|---|---|---|
| `provider` | Where it runs | catalog codes; own infrastructure and private cloud is the value `own`; public providers get neutral codes (`pub-a`, `pub-b`) | never |
| `jurisdiction` | Legal area whose rules apply | opaque catalog codes (`jur-a`, `jur-b`) | never |
| `region` | Company region code, mapped in the catalog to provider-native regions | `reg-a1`, `reg-b1` | never |
| `site` | Physical or provider location ([01 section 4.4](01-naming-conventions.md#44-environments-and-sites)) | `dc1`, `cld` | never in product-contour names |
| `cell` | Independently deployable copy of the product serving a set of tenants | pooled `c01` to `c99`; dedicated `d<tenant-key>` | yes, the only deployment key in names |
| `tenant-scope` | How tenants share the cell | `pooled`, `dedicated` | never |

**Provider independence.**

- No name contains a provider. A cell moves from `own` to `pub-a` without renaming a service.
- Provider-specific resources (accounts, projects, resource groups, buckets) are rendered from metadata by the provider's own form and limits; the logical identity stays the same on every provider.
- Each product keeps the ability to run on at least two providers, one of which may be `own`. A design that only works on one provider is recorded as an exception with a review date.
- Provider codes are neutral: a provider's commercial name lives in the catalog, not in codes, names or labels.

## 5. Tenants

A tenant is identified by three opaque keys, from the outside in:

| Key | Who | Form | Example |
|---|---|---|---|
| `tenant-operator` | Party that runs the service for the customer: mess.systems itself or a partner | `op-` plus 6 characters | `op-a7k2mz` |
| `tenant-entity` | Legal entity that holds the contract | `le-` plus 6 characters | `le-q4w9np` |
| `tenant-customer` | End customer organisation that uses the product | `ec-` plus 6 characters | `ec-h3t8rd` |

- The 6 characters use the asset-id alphabet of [06](06-endpoint-conventions.md#2-form): `a-z 2-9` without `o l i`, first character a letter. Keys are allocated by the catalog, opaque and immutable. They never contain a customer name, brand, country or contract number.
- The full tenant path is `op-a7k2mz/le-q4w9np/ec-h3t8rd`. A tenant without a partner has mess.systems as operator.
- Examples and documentation use generic names only ("operator A", "entity B", "customer C").
- **Pooled tenants never appear in names.** They are rows and labels.
- **A dedicated tenant** gets its own cell named `d<key>` after the 6 characters of the key of the legal entity (`tenant-entity`): `dq4w9np`. All end customers of that entity share its dedicated cell. Example: `store.records.dq4w9np.x.prd.svc.mess.systems`.

## 6. What goes into a name

| Goes into names | Stays in metadata only |
|---|---|
| `service`, `domain`, `product`, `env`, `cell` (which includes the dedicated tenant key) | `provider`, `jurisdiction`, `region`, `site`, `tenant-scope`, `residency`, pooled tenant keys, `implementation`, `owner`, `cost-center`, `criticality`, `data-class` |

## 7. Governance labels

Labels follow the grammar of [05](05-labels-and-tags.md). Each key has a class:

- **required**: the author sets it; a resource without it fails the check.
- **conditional**: required when its condition holds.
- **derived**: filled by tooling from the catalog or the pipeline; never typed by hand.

| Key | Class | Values | Note |
|---|---|---|---|
| `contour` | required | `corp`, `product` | |
| `product`, `domain`, `service` | required (product contour) | catalog codes | cost axis of the product contour |
| `component` | conditional: the service has more than one deployable | `api`, `worker`, `migrate` | |
| `env` | required | `prd`, `stg`, `tst`, `dev`, `sbx` | |
| `owner` | required | group ID | as in 05 |
| `cost-center` | required | `cc-<name>` | as in 05 |
| `criticality` | required (product contour) | `critical`, `high`, `medium`, `low` | |
| `data-class` | required | `public`, `internal`, `confidential`, `restricted` | as in 05 |
| `residency` | required (product contour) | jurisdiction code, or `any` | required even when `any` |
| `tenant-scope` | required (product contour runtime) | `pooled`, `dedicated` | |
| `cell` | conditional: cell-bound resource | `c01`, `d<key>` | |
| `tenant-operator`, `tenant-entity`, `tenant-customer` | conditional: dedicated resource | `op-…`, `le-…`, `ec-…` | |
| `lifecycle` | conditional: not an ordinary long-lived resource | `ephemeral`, `retiring` | absent means active |
| `provider`, `region`, `jurisdiction`, `site` | derived | from the cell in the catalog | |
| `managed-by` | derived | `opentofu`, `argo-cd`, `ansible` | set by the IaC module or GitOps tool |
| `source-repo` | derived | `<org>/<repo>` | set by CI |
| `implementation` | derived | install code | from the catalog |

**Reconciliation with 05.** The cost tags of [05 section 2](05-labels-and-tags.md#2-cost-tags-finops) stay as they are for the corporate contour. In the product contour the required cost tags are `cost-center`, `owner`, `env`, `product`, `domain`, `service`; `capability` is not set. `initiative` and `plane` remain optional in both contours.

## 8. OpenTelemetry

| Attribute | Product contour | Product X example |
|---|---|---|
| `service.namespace` | `<product>.<domain>` | `x.records` |
| `service.name` | `<service>`, or `<service>-<component>` | `store`, `store-worker` |
| `deployment.environment.name` | env code | `prd` |
| `service.instance.id` | generated per instance | |
| `service.version` | release version | |

Cell, tenant scope and provider are resource attributes with the `mess.systems.` prefix (`mess.systems.cell`), not part of the service name. The corporate contour keeps the application form of [01 section 5](01-naming-conventions.md#5-object-forms).

## 9. SPIFFE

The product contour has three trust domains, separate from the corporate `mess.systems`:

| Trust domain | Environments |
|---|---|
| `spiffe://product.mess.systems` | `prd` |
| `spiffe://nonprod.product.mess.systems` | `stg`, `tst`, `dev` |
| `spiffe://sandbox.product.mess.systems` | `sbx` |

Path: `/<product>/<domain>/<service>[/<cell>]`, with the env as the first segment in the non-prod and sandbox domains: `spiffe://product.mess.systems/x/records/store/c01`, `spiffe://nonprod.product.mess.systems/stg/x/access/login`. Crossing trust domains needs explicit federation; a non-prod workload never holds a production identity.

## 10. Executable standard

The vocabulary and the rules of this part are also data in the repository:

| Path | Content |
|---|---|
| `schema/resource-metadata.schema.json` | JSON Schema for the metadata of a product-contour resource |
| `catalog/*.yaml` | Vocabulary: contours, environments, providers, jurisdictions, regions, cells, product X domains and services, label classes |
| `tests/golden/*.yaml` | Golden examples: metadata and the names it must produce |
| `tests/check_golden.py` | Test that validates the golden examples against the schema and the catalog |

CI runs the test on every pull request. The data files are examples for the fictional product X; an organisation replaces the catalog with its own.

## 11. Refusals (reject the name if…)

| Smell | Rule broken |
|---|---|
| provider, region, jurisdiction or site in a product-contour name | [Deployment keys](#4-deployment-keys) |
| pooled tenant key, customer name or brand in any name | [Tenants](#5-tenants) |
| implementation (`postgresql`, `keycloak`) as a service code | [Product, domain, service, implementation](#2-product-domain-service-implementation) |
| product-contour internal name without env | [Environments and DNS](#3-environments-and-dns) |
| env, cell or domain in a public customer name other than the `stg` surface | [Environments and DNS](#3-environments-and-dns) |
| product code equal to `shared`, `corp`, `eng` or `ext` | [Two contours](#1-two-contours) |
| production and non-production workloads in one trust domain | [SPIFFE](#9-spiffe) |
| resource without `residency` in the product contour | [Governance labels](#7-governance-labels) |
| real provider name as a provider code | [Deployment keys](#4-deployment-keys) |
