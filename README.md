# mess.systems naming standard

The naming standard of **mess.systems**: one grammar for DNS names, hosts, repositories, images, buckets, databases, Kubernetes objects, observability, secrets paths, and identities (humans, admins, service accounts, AI agents, workloads).

It is a living template: it is applied, questioned, and revised as understanding grows. Use it as-is or adapt it to your own organisation.

**Status:** v2, evolving. Names and rules may still change; changes are recorded in the changelog below.

## Why

Names are the cheapest architecture decision and the most expensive one to change. When every team names things its own way, you get product names in DNS, access rules hidden in hostnames, secrets organised by vendor, and service accounts indistinguishable from AI agents. This standard derives every name from the same few axes — **plane → domain → capability → product → env** — so that a name can be predicted from intake data and reviewed mechanically.

## Files

| File | What it fixes |
|---|---|
| [01-naming-conventions.md](01-naming-conventions.md) | Character rules, the ten metadata keys, DNS grammars, codes, object forms (hosts, repos, images, buckets, k8s, observability), TLS, procedure, refusals |
| [02-worked-example.md](02-worked-example.md) | A fictional organisation migrating legacy names (`grafana.corp.lan`, `vm042`, `secret/users/...`) to the standard |
| [03-secrets-conventions.md](03-secrets-conventions.md) | Secrets manager (OpenBao / HashiCorp Vault) mounts, paths, items and fields, policies, auth roles, metadata |
| [04-identity-conventions.md](04-identity-conventions.md) | Humans, admins, break-glass, service accounts, agents, groups and tiers, SPIFFE, mesh groups, k8s RBAC, DB roles, gateway clients |
| [CONTRIBUTING.md](CONTRIBUTING.md) | How to propose changes and discussion rules |
| [LICENSE](LICENSE) | CC BY 4.0 |

Start with 01 §9 (procedure) and 01 §11 (worked encodings), then read 02.

## Core ideas in one screen

- **Two DNS grammars, no third.** Internal: `<capability>.<domain>.<plane>[.<env>].svc.<company-domain>`. Public: `<surface>.<product-domain>`. The leftmost label is the capability, never the product.
- **One install → one name.** Aliases are time-boxed redirects.
- **Names carry no authorization.** Labels route and identify; access comes from groups and policies (NIST AC-6).
- **Same ten metadata keys everywhere** (`plane, domain, capability, product, env, owner, tier, scope, data_class, exposure`). DNS encodes four; catalogs, secrets metadata, k8s labels, and hypervisor tags carry the rest.
- **Identity kind is visible in the ID.** Agents are not service accounts: they act autonomously, need an accountable human operator, and get their own prefix and secrets node.
- **Secrets live with their consumer**, one mount per plane, path `<domain>/<capability>/<env>/<item>`, policy per consumer identity.
- **Three group prefixes**: `tier-`, `role-`, `app-`.
- **Trust domain ≠ DNS zone** (SPIFFE).
- **Lowercase, digits, hyphen** in every external identifier; `snake_case` only where the system forbids hyphens.
- **Product-agnostic.** Products named in examples (IdP, secrets manager, mesh VPN, git forge, registry, dashboards…) are interchangeable illustrations, not requirements.

`mess.systems` is the organisation's own domain and appears in the examples; replace it with yours when adapting.

## Design rationale

The standard is checked against RFC 1035/1123/8499 constraints and common enterprise practice: Microsoft Cloud Adoption Framework resource naming, Vault/OpenBao path guidance, the SPIFFE specification, Kubernetes naming, NIST SP 800-53 AC-2/AC-6.

Questioned and kept:

| Question | Decision | Why |
|---|---|---|
| Six labels in prod (`sso.iam.shared.svc.mess.systems`) too deep? | Keep | RFC limits are 63/label, 253 total. Per-name ACME certs make wildcard depth matter only for non-ACME endpoints. Depth buys a derivable name |
| `svc` collides with Kubernetes `svc.cluster.local`? | Keep `svc` | Different suffix, different resolver (01 §3.1) |
| Private pseudo-TLD (`.lan`, `.corp`, `.internal`)? | No — use a subdomain of a registered domain | Cannot get public-CA certs. `.local` is mDNS (RFC 6762) — never use |
| Env omitted in prod DNS but present on hosts/schemas? | Keep | DNS is zone-shortened; inventories are not |
| One shared LLM gateway keeps one name (`gateway.ai.corp`) even when products use it? | Keep | One install → one name; `gateway.ai.platform` is reserved, not minted |

## Changelog

### v2 (current)

- Multi-word codes are hyphenated (`data-catalog`, `hub-cache`, `service-desk`), never concatenated.
- Capability codes are unique across **all** domains (e.g. the document database is `docstore`, not `docs`; LLM tracing is `llm-traces`, not `traces`; the AI guardrail is `guard`, not `policy`).
- The public `apps.<brand>` zone is defined as the `ext` zone under grammar B.
- Host form gains a leading site code: `<site>-<plane>-<domain>-<product>-<env>-<NN>`.
- Added secrets (03) and identity (04) conventions; one metadata label set applied everywhere.
- SPIFFE trust domain is the organisation (`spiffe://mess.systems`), path `/<plane>/<domain>/<capability>`.
- Explicit rule: a DNS label is never an authorization input.

### v1

- Capability-first internal grammar, shallow public grammar, plane as the first isolation axis, one install → one URL, providers as catalog IDs.

## Open questions

- A generic cutover runbook (order for DNS, secrets mounts, SPIFFE trust domain). 02 §8 sketches one.
- Whether `obs` stays a separate domain or folds into `infra`.

## Discussing and contributing

- **Questions, ideas, "how would you name X?"** → GitHub Discussions.
- **Concrete change proposals** (new code, rule change, bug in an example) → an Issue using the *Proposal* template, then a pull request.
- Read [CONTRIBUTING.md](CONTRIBUTING.md) first, especially the publication checklist: never post real internal hostnames, IPs, secrets, or personal data in issues, discussions, or examples.

## License

Text licensed under [Creative Commons Attribution 4.0 International (CC BY 4.0)](LICENSE). You may share and adapt it, including commercially, with attribution: "mess.systems naming standard, CC BY 4.0".
