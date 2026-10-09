**English** | [Русский](README.ru.md) | [简体中文](README.zh-CN.md)

# mess.systems naming standard

The naming standard of **mess.systems**: one grammar for DNS names, hosts, repositories, images, buckets, databases, Kubernetes objects, observability, secrets paths, and identities (humans, admins, service accounts, AI agents, workloads).

It is a living template: it is applied, questioned, and revised as understanding grows. Use it as-is or adapt it to your own organisation.

**Status:** v2, evolving. Names and rules may still change; changes are recorded in the changelog below.

## Why

Names are the cheapest architecture decision and the most expensive one to change. When every team names things its own way, you get product names in DNS, access rules hidden in hostnames, secrets organised by vendor, and service accounts indistinguishable from AI agents. This standard derives every name from the same few axes, taken in order: **plane, domain, capability, product, env**. As a result, a name can be predicted from intake data and reviewed mechanically.

## Files

| File | What it fixes |
|---|---|
| [01-naming-conventions.md](01-naming-conventions.md) | Character rules, the ten metadata keys, DNS grammars, codes, object forms (hosts, repos, images, buckets, k8s, observability), TLS, procedure, refusals |
| [02-worked-example.md](02-worked-example.md) | A fictional organisation migrating legacy names (`grafana.corp.lan`, `vm042`, `secret/users/...`) to the standard |
| [03-secrets-conventions.md](03-secrets-conventions.md) | Secrets manager (OpenBao / HashiCorp Vault) mounts, paths, items and fields, policies, auth roles, metadata |
| [04-identity-conventions.md](04-identity-conventions.md) | Humans, admins, break-glass, service accounts, agents, groups and tiers, SPIFFE, mesh groups, k8s RBAC, DB roles, gateway clients |
| [CONTRIBUTING.md](CONTRIBUTING.md) | How to propose changes and discussion rules |
| [i18n/](i18n/) | Russian and Simplified Chinese translations (informative) |
| [LICENSE](LICENSE) | CC BY 4.0 |

Start with the [naming procedure](01-naming-conventions.md#9-naming-procedure) and the [worked encodings](01-naming-conventions.md#11-worked-encodings), then read the [worked example](02-worked-example.md).

## Core ideas in one screen

- **Two DNS grammars, no third.** Internal: `<capability>.<domain>.<plane>[.<env>].svc.<company-domain>`. Public: `<surface>.<product-domain>`. The leftmost label is the capability, never the product.
- **One install, one name.** Aliases are time-boxed redirects.
- **Names carry no authorization.** Labels route and identify; access comes from groups and policies (least privilege, [NIST SP 800-53 AC-6](https://csrc.nist.gov/projects/cprt/catalog#/cprt/framework/version/SP_800_53_5_2_0/home?element=AC-06)).
- **Same ten metadata keys everywhere** (`plane, domain, capability, product, env, owner, tier, scope, data_class, exposure`). DNS encodes four; catalogs, secrets metadata, k8s labels, and hypervisor tags carry the rest.
- **Identity kind is visible in the ID.** Agents are not service accounts: they act autonomously, need an accountable human operator, and get their own prefix and secrets node.
- **Secrets live with their consumer**, one mount per plane, path `<domain>/<capability>/<env>/<item>`, policy per consumer identity.
- **Three group prefixes**: `tier-`, `role-`, `app-`.
- **The trust domain is not the DNS zone** ([SPIFFE](https://spiffe.io/docs/latest/spiffe-about/overview/)).
- **Lowercase, digits, hyphen** in every external identifier; `snake_case` only where the system forbids hyphens.
- **Product-agnostic.** Products named in examples (IdP, secrets manager, mesh VPN, git forge, registry, dashboards…) are interchangeable illustrations, not requirements.

`mess.systems` is the organisation's own domain and appears in the examples; replace it with yours when adapting.

## Design rationale

The standard is checked against the DNS constraints of [RFC 1035](https://www.rfc-editor.org/rfc/rfc1035), [RFC 1123](https://www.rfc-editor.org/rfc/rfc1123), and [RFC 9499](https://www.rfc-editor.org/rfc/rfc9499), and against common enterprise practice: [Microsoft Cloud Adoption Framework resource naming](https://learn.microsoft.com/en-us/azure/cloud-adoption-framework/ready/azure-best-practices/resource-naming), [OpenBao](https://openbao.org/docs/concepts/policies/) and [Vault](https://developer.hashicorp.com/vault/docs/concepts/policies) policy and path guidance, the [SPIFFE ID specification](https://github.com/spiffe/spiffe/blob/main/standards/SPIFFE-ID.md), [Kubernetes object names](https://kubernetes.io/docs/concepts/overview/working-with-objects/names/), and the [NIST SP 800-53](https://csrc.nist.gov/pubs/sp/800/53/r5/upd1/final) controls [AC-2](https://csrc.nist.gov/projects/cprt/catalog#/cprt/framework/version/SP_800_53_5_2_0/home?element=AC-02) (account management) and [AC-6](https://csrc.nist.gov/projects/cprt/catalog#/cprt/framework/version/SP_800_53_5_2_0/home?element=AC-06) (least privilege).

Questioned and kept:

| Question | Decision | Why |
|---|---|---|
| Six labels in prod (`sso.iam.shared.svc.mess.systems`) too deep? | Keep | RFC 1035 allows 63 characters per label and 253 per name. Per-name ACME certificates make wildcard depth matter only for endpoints that cannot use ACME. Depth buys a derivable name |
| `svc` collides with Kubernetes `svc.cluster.local`? | Keep `svc` | Different suffix, different resolver (see [grammar A](01-naming-conventions.md#31-grammar-a-internal)) |
| Private pseudo-TLD (`.lan`, `.corp`, `.internal`)? | No, use a subdomain of a registered domain | Public CAs do not issue certificates for it. `.local` is reserved for mDNS ([RFC 6762](https://www.rfc-editor.org/rfc/rfc6762)), so never use it |
| Env omitted in prod DNS but present on hosts/schemas? | Keep | DNS is zone-shortened; inventories are not |
| One shared LLM gateway keeps one name (`gateway.ai.corp`) even when products use it? | Keep | One install, one name; `gateway.ai.platform` is reserved, not minted |

## Changelog

### v2 (current)

- Multi-word codes are hyphenated (`data-catalog`, `hub-cache`, `service-desk`), never concatenated.
- Capability codes are unique across **all** domains (e.g. the document database is `docstore`, not `docs`; LLM tracing is `llm-traces`, not `traces`; the AI guardrail is `guard`, not `policy`).
- The public `apps.<brand>` zone is defined as the `ext` zone under grammar B.
- Host form gains a leading site code: `<site>-<plane>-<domain>-<product>-<env>-<NN>`.
- Added [secrets](03-secrets-conventions.md) and [identity](04-identity-conventions.md) conventions; one metadata label set applied everywhere.
- SPIFFE trust domain is the organisation (`spiffe://mess.systems`), path `/<plane>/<domain>/<capability>`.
- Explicit rule: a DNS label is never an authorization input.

### v1

- Capability-first internal grammar, shallow public grammar, plane as the first isolation axis, one install with one URL, providers as catalog IDs.

## Open questions

- A generic cutover runbook (order for DNS, secrets mounts, SPIFFE trust domain). The [cutover order](02-worked-example.md#8-cutover-order) in the worked example sketches one.
- Whether `obs` stays a separate domain or folds into `infra`.

## Discussing and contributing

- **Questions, ideas, "how would you name X?"**: start a thread in [GitHub Discussions](https://github.com/mess-systems/naming-standard/discussions).
- **Concrete change proposals** (new code, rule change, bug in an example): open an [issue](https://github.com/mess-systems/naming-standard/issues) with the *Proposal* template, then a pull request.
- Read [CONTRIBUTING.md](CONTRIBUTING.md) first, especially the publication checklist: never post real internal hostnames, IPs, secrets, or personal data in issues, discussions, or examples.

## Translations

- English is the normative text; on any discrepancy, the English version prevails.
- Translations live in `i18n/<lang>/` under the same filenames: Russian in `i18n/ru/`, Simplified Chinese in `i18n/zh-CN/`. Translated READMEs are `README.ru.md` and `README.zh-CN.md` in the repository root.
- Only explanations are translated. Names, tokens, codes, FQDNs, paths, and code blocks are identical in every language.
- Each translation records in its header the English source commit it matches. To update one, follow the *Translations* section of [CONTRIBUTING.md](CONTRIBUTING.md).

## License

Text licensed under [Creative Commons Attribution 4.0 International (CC BY 4.0)](LICENSE) ([license deed](https://creativecommons.org/licenses/by/4.0/)). You may share and adapt it, including commercially, with attribution: "mess.systems naming standard (https://github.com/mess-systems/naming-standard), CC BY 4.0".
