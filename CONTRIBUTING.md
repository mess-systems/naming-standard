**English** | [Русский](i18n/ru/CONTRIBUTING.md) | [简体中文](i18n/zh-CN/CONTRIBUTING.md)

# Contributing

Thanks for helping improve the naming standard. It is meant to be argued with: colleagues from different companies and stacks bring the cases that break it.

## Where to talk

| You have… | Use |
|---|---|
| A question, an edge case, "how would you name X?" | GitHub **Discussions** (Q&A or Ideas) |
| A concrete change: new code, changed rule, wrong example, broken link | An **Issue** with the *Proposal* template, then a pull request |
| A typo or obviously broken link | A pull request directly |

## How to propose a change

1. **Search first.** Codes must be unique across all domains (see [capability codes](01-naming-conventions.md#43-capability-codes-unique-across-all-domains)); check the tables and existing issues.
2. **State the problem with an example**, not just the rule you want. Use fictional names (`example.com`, `*.example`, `corp.lan`, `jdoe`, `acmecloud`).
3. **Name what it breaks.** Which files and sections change? Does an existing valid name become invalid (breaking) or does an invalid one become valid (additive)?
4. **Keep the grammar closed.** "We need a special case" is usually a missing code or a group, not a new grammar (see [there is no grammar C](01-naming-conventions.md#33-there-is-no-grammar-c)).
5. **Open a PR** that updates every affected file in one change: rule, tables, worked encodings, refusals, and the [worked example](02-worked-example.md) if relevant.

Editorial rules: English, Markdown, one sentence per rule where possible, tables for mappings. Link to other files and sections with relative links whose text names the target, for example `[capability codes](01-naming-conventions.md#43-capability-codes-unique-across-all-domains)`; do not write bare section numbers or the section sign. Link external standards (RFCs, NIST controls) to their canonical source on first mention.

## Discussion rules

- Be specific and kind. Critique names and rules, not people or employers.
- Argue from constraints (RFCs, product limits, audit and security needs) and from real-world cases described in fictional terms.
- One topic per thread. Link related threads instead of merging them.
- Disagreement is fine; the maintainer decides and records the reasoning in the issue or the changelog.
- Do not share anything confidential to your employer or clients.

## Publication checklist (every issue, discussion, PR, and example)

Before you post, confirm that the text contains **none** of:

- [ ] Real internal hostnames, domains, or zones (yours or anyone else's). Use `example.com`, `*.example`, `corp.lan`.
- [ ] IP addresses, CIDRs, ports, or VPN/mesh details of real networks. If you need addresses, use the documentation ranges from [RFC 5737](https://www.rfc-editor.org/rfc/rfc5737) (`192.0.2.0/24`) or [RFC 3849](https://www.rfc-editor.org/rfc/rfc3849).
- [ ] Secrets or anything that looks like one: tokens, API keys, passwords, private keys, connection strings, real secrets paths.
- [ ] Real usernames, account IDs, group names, or email addresses of people or systems.
- [ ] Container/VM IDs, asset tags, ticket numbers, or internal decision-record IDs from a real organisation.
- [ ] Customer, employer, or vendor-contract details not already public.
- [ ] Screenshots that show any of the above.

Maintainers will edit or remove content that fails this checklist. If you posted something sensitive by mistake, rotate it first, then ask a maintainer to purge it.

## Translations

English files in the repository root are normative. Translations in `i18n/<lang>/` and `README.<lang>.md` are informative; on any discrepancy, the English text prevails.

- Change the English text first. A translation may lag behind the English; it must never add to or contradict it.
- To update a translation, translate the changed sections and set the source commit in its header note to the English commit it now matches (`git log -1 --format=%h -- <file>`).
- Translate explanations only. Never translate names, tokens, codes, FQDNs, paths, table identifier columns, or code blocks. Keep the heading numbers and the Markdown structure; translate link text, and point anchors at the translated heading of the sibling file.
- Relative links in a translation point to translated siblings (`03-secrets-conventions.md`) and reach root files with `../../` (`../../LICENSE`).
- A new language gets `i18n/<lang>/` with a [BCP 47](https://www.rfc-editor.org/info/bcp47) tag (`ru`, `zh-CN`), a `README.<lang>.md`, and an entry in every language switcher.

## License of contributions

By contributing you agree that your contribution is licensed under [CC BY 4.0](LICENSE), the same as the rest of the text.
