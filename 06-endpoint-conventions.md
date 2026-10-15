# 06. Endpoint conventions

How employee devices (laptops and desktops) are named, labelled and kept out of service DNS. The worked baseline for these devices is the [endpoint blueprint](https://github.com/mess-systems/blueprints/tree/main/endpoint).

## 1. Why a separate family

The **Host / container / VM** form in [01 section 5](01-naming-conventions.md#5-object-forms) (`<site>-<plane>-<domain>-<product>-<env>-<NN>`) describes deployed service infrastructure. For a laptop, `site`, `domain`, `product` and `env` have no true value: the device moves, runs many products and is not a deployment environment. Forcing it in would invent values and cause renames.

This is a new object **family**, not a new DNS grammar, so [there is still no grammar C](01-naming-conventions.md#33-there-is-no-grammar-c).

## 2. Form

```
<profile>-<form>-<asset-id>          # std-lt-a1b2c3, eng-dt-d4e5f6, paw-lt-g7h8j9
```

| Axis | Code | Meaning |
|---|---|---|
| `profile` | `std` | Standard employee endpoint (default baseline) |
| | `eng` | Engineering endpoint with a genuinely distinct baseline: build tools, AI coding agents, sandboxing, package tooling, different telemetry. Installing an IDE is not enough. |
| | `paw` | Dedicated, hardened privileged-access workstation. Used only for admin work. |
| `form` | `lt` | Laptop |
| | `dt` | Desktop or fixed workstation |
| `asset-id` | 6 chars | Allocated by the authoritative asset system; immutable for the device's life |

- **Not `dev`.** `dev` is the environment code in [01 section 4.4](01-naming-conventions.md#44-environments-and-sites); a code never gets a second meaning.
- **asset-id alphabet.** `a-z 2-9` without `o`, `l`, `i`, which removes the ambiguous characters `0 o 1 l i`. The first character MUST be a letter ([character rules](01-naming-conventions.md#1-character-rules-apply-to-every-family)). This gives 23 × 31⁵, about 6.6 × 10⁸ values. A stable existing asset tag MAY be used if it meets these rules. Serial numbers MUST NOT be used: they leak the manufacturer and are not opaque.
- Regex: `^(std|eng|paw)-(lt|dt)-[a-hjkmnp-z][a-hjkmnp-z2-9]{5}$`. BYOD alias: `^byod-(lt|dt)-[a-hjkmnp-z][a-hjkmnp-z2-9]{5}$`.

## 3. Length

- `std-lt-a1b2c3` is **13** characters. The BYOD alias `byod-lt-q7r8s9` is **14**.
- The binding limit is 15 characters: a [Windows Autopilot device name template](https://learn.microsoft.com/en-us/autopilot/profiles) must be "15 characters or less", and the NetBIOS computer name is also capped at 15 ([Microsoft: naming conventions in AD](https://learn.microsoft.com/en-us/troubleshoot/windows-server/active-directory/naming-conventions-for-computer-domain-site-ou)).
- The [Intune Rename action](https://learn.microsoft.com/en-us/intune/device-management/actions/rename) allows up to 63 characters for Windows (checked 2026-10-12), but not for hybrid-joined devices. One 15-safe grammar avoids two grammars at enrollment and after it.
- Headroom is 2 characters. A new profile code MUST stay at 3 letters and a new form code at 2.

## 4. What never goes into an endpoint name

Site, env, domain, product, user handle, department, OS, model, serial, compliance state and privilege tier. All of these change over the device's life or are policy inputs that belong in metadata. **A name never grants access.**

## 5. Metadata

The shared keys from [01 section 2](01-naming-conventions.md#2-the-ten-metadata-keys) apply where meaningful (`plane`, `owner`, `tier`, `data_class`, `exposure`). `domain`, `product`, `env` and `scope` do not apply; `capability` is always `endpoint`. Endpoint-specific keys:

| Key | Example | Purpose |
|---|---|---|
| `plane` | `corp`, `eng`, `shared` | Trust zone |
| `owner` | `role-endpoint-engineers` | Accountable management group |
| `tier` | `t2`, `t1`, `t0` | Highest tier the device is certified for (never in the name) |
| `data_class` | `confidential` | Maximum expected local data class |
| `exposure` | `mesh` | Normal connectivity posture |
| `ownership` | `org`, `personal`, `partner` | Legal and operational ownership |
| `endpoint_profile` | `std`, `eng`, `paw` | Applied security and software baseline |
| `device_form` | `lt`, `dt` | Form factor |
| `asset_id` | `a1b2c3` | Immutable inventory identity |
| `assigned_to` | IdP subject or empty | Current custodian; never in the name |
| `management` | `full`, `work-profile`, `registered` | Degree of enterprise control |
| `compliance_state` | from the device management tool | Dynamic posture; never in the name |

As labels and tags these keys use the hyphenated form of [05](05-labels-and-tags.md) (`endpoint-profile`, `device-form`). The record is keyed by the durable device management or directory device ID, or a hardware-backed device identity, not by the hostname.

**Profile and plane.** The profile selects the baseline; the plane selects the trust zone. An `eng` endpoint is normally `plane=eng`; `std` and `paw` are normally `corp` or `shared`. The catalog MUST validate the pairing and flag exceptions for review.

## 6. Capability code `endpoint`

`endpoint` is the [capability code](01-naming-conventions.md#43-capability-codes-unique-across-all-domains) for everything that runs on the employee device: device management agents, security and access agents, remote support, AI client control, local container runtimes. It is used in catalogs, the tech radar and cost tags. It never appears in an endpoint name or in service DNS, because endpoints have no service DNS name.

The tech radar and software catalog category `device` covers the same area (user devices, not network gear or IoT). It is a catalog code, not a name token.

## 7. DNS and registration

- Endpoints get **no static records** in the service zone (`*.svc.mess.systems`, [01 section 3](01-naming-conventions.md#3-dns-two-grammars-nothing-else)). The name lives in the catalog and the device management tool. It MAY appear in dynamic DNS or mDNS on a local segment. A name such as `std-lt-a1b2c3.corp.mess.systems` is a grammar C and is refused.
- The name is registered in the endpoint catalog **before enrollment**, as [01 section 9](01-naming-conventions.md#9-naming-procedure) requires for every name.

## 8. BYOD

- A personally owned device keeps its owner-controlled hostname and gets no corporate endpoint name, DNS record or SPIFFE node identity.
- The device management tool MAY assign the alias `byod-<form>-<asset-id>`, for inventory and audit only.
- Policy comes from authoritative `ownership`, enrollment mode, attestation, certificate issuer and compliance, never from the alias ([NIST SP 800-46r2](https://nvlpubs.nist.gov/nistpubs/SpecialPublications/NIST.SP.800-46r2.pdf), [NIST SP 800-114r1](https://nvlpubs.nist.gov/nistpubs/specialpublications/nist.sp.800-114r1.pdf)).

## 9. PAW is a class, not a tier

The refusals reject tier in a name (`admin.`, `t0-`). `paw` is allowed because it names a durable device class with its own hardening baseline, not a privilege level ([Microsoft: privileged access devices](https://learn.microsoft.com/en-us/security/privileged-access-workstations/privileged-access-devices), [CISA AA25-212A](https://www.cisa.gov/news-events/cybersecurity-advisories/aa25-212a)).

- `t0` and `t1` never appear in the hostname. With separate PAW hardware per tier, the device management profile may be named `paw-t0` while the hostname stays `paw-<form>-<asset-id>`. The name says "this is a PAW"; the catalog says which tier.
- An ordinary laptop is never named `paw` just because its user is an administrator.

## 10. SPIFFE

A fully managed device that passes attestation may get the node ID `spiffe://mess.systems/node/<endpoint-name>`, for example `spiffe://mess.systems/node/std-lt-a1b2c3` ([04 section 8](04-identity-conventions.md#8-spiffe--spire)). Never a user handle. BYOD gets no node identity.

## 11. Refusals (reject the name if…)

| Smell | Rule broken |
|---|---|
| user handle, department, site, env, OS, model, serial, compliance state or tier in an endpoint name (`ws-jdoe-01`, `paw-t0-...`) | [What never goes into an endpoint name](#4-what-never-goes-into-an-endpoint-name) |
| laptop or desktop named with the Host / container / VM form | [Why a separate family](#1-why-a-separate-family) |
| `dev` used as an endpoint profile | [Form](#2-form) |
| static DNS record for an endpoint in the service zone | [DNS and registration](#7-dns-and-registration) |
| corporate endpoint name, DNS record or SPIFFE node ID given to a BYOD device | [BYOD](#8-byod) |
| serial number used as `asset-id` | [Form](#2-form) |
