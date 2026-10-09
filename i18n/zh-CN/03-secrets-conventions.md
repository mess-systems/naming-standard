[English](../../03-secrets-conventions.md) | [Русский](../ru/03-secrets-conventions.md) | **简体中文**

> **译文说明。** 本文为标准 v2 版本的译文，源提交 `b6791c2`。英文文本为规范性文本：如有任何不一致，以英文版本为准。

# 机密规范——OpenBao / HashiCorp Vault

> **状态：** v2，持续演进中。规则源自 [01-naming-conventions.md](01-naming-conventions.md)：机密归属于其使用方，平面是第一道隔离边界，供应商是目录 ID，各环境相互隔离。
> **典型起点：** 一个 KV v2 挂载点 `secret/`，其中存在多种相互竞争的路径形态（§7）。**目标：** `https://secrets.iam.shared.svc.mess.systems`，每个平面一个挂载点 (mount)，一种路径语法。
> 本文件中不包含任何机密值，只有名称。本文针对 OpenBao / HashiCorp Vault KV v2 编写；路径和命名规则同样适用于其他机密管理器。

## 1. 所采用的原则

| # | 规则 | 依据 |
|---|---|---|
| S1 | 机密存放在其**使用方**的路径下，因为策略授予的是路径前缀，而策略是颁发给使用方的 | Vault/OpenBao 策略指南 |
| S2 | 挂载点 = 平面。影响范围和审计遵循第一隔离维度 | 01 §4.1 |
| S3 | 路径中**始终**包含 `env`，生产环境也不例外。存储不按区域缩写 | 01 §3.1 |
| S4 | 供应商凭据放在与该供应商交互的能力之下，条目为 `provider-<vendor>` | 01 §8 |
| S5 | 人员在 OpenBao 中没有个人机密。个人机密 → `passwords.iam.corp`（密码管理器）。人员的特权访问 → OIDC 登录 + 策略，绝不使用存储的令牌 | NIST AC-2 |
| S6 | 紧急访问 (break-glass) 凭据是名为 `admin` 的独立条目，通过策略仅限 `tier-t0-superadmin` 访问，每次读取都会触发告警 | 特权访问层级（[04](04-identity-conventions.md) §3.1） |
| S7 | 每个条目一个机密，每个机密包含多个字段。字段使用标准的 `snake_case` 名称，以便使用方可移植 | 可移植性 |
| S8 | 每个机密都带有 `custom_metadata`，包含 01 §2 中的十个键以及 `rotation` 和 `issuer` | 可发现性、审计 |
| S9 | 生产机密绝不出现在非生产路径中。非生产条目单独创建，而不是复制 | 环境隔离 |
| S10 | 策略和 AppRole 的名称**就是**身份名称（[04](04-identity-conventions.md) §2）。不加 `-policy`、`-role` 后缀 | 每个身份一个名称 |

## 2. 挂载点

| 挂载点 | 类型 | 存放内容 |
|---|---|---|
| `shared/` | kv-v2 | 控制平面机密（IAM、PKI、DNS、网状网络、可观测性、基础设施） |
| `corp/` | kv-v2 | 面向员工的服务、员工使用的智能体 |
| `eng/` | kv-v2 | SDLC/ADLC 工具 |
| `platform/` | kv-v2 | 产品共享运行时 |
| `ext/` | kv-v2 | 合作伙伴/演示门户 |
| `<product>/` | kv-v2 | 每个产品一个挂载点（例如 `shopfront/`、`ledger/`） |
| `pki-int/` | pki | 内部签发 CA |
| `transit/` | transit | 加密即服务密钥，以 `<application>` 命名 |
| `auth/approle` | auth | 不使用 SPIFFE 的工作负载 |
| `auth/jwt-<idp>`（例如 `jwt-keycloak`） | auth | 通过 OIDC 认证的人员和 CI |
| `auth/jwt-spire` | auth | SPIFFE 工作负载（目标） |
| `auth/kubernetes-<cluster>` | auth | Kubernetes 服务账号 |

遗留的 `secret/` 挂载点保留到 §7 中的所有路径迁移完毕，然后停用。

## 3. 路径语法

```
<mount>/<domain>/<capability>/<env>/<item>
<mount>/<domain>/<agent-id>/<env>/<item>          # agents: agent-id replaces capability
<product>/<component>/<env>/<item>                # product mounts
```

| 令牌 | 取值 |
|---|---|
| `<domain>` | 01 §4.2 |
| `<capability>` | 01 §4.3——使用方的能力 |
| `<agent-id>` | [04](04-identity-conventions.md) §2 中的 `agent-<name>`（智能体会使用多种能力，因此自成一个节点） |
| `<env>` | `prd dev tst stg`——必填 |
| `<item>` | §4 |

挂载点以下的深度固定为四级。更深的路径一律拒绝；需要更多结构时应增加条目，而不是增加层级。

## 4. 条目与字段

标准条目 (item)（在自创条目之前请先使用这些）：

| 条目 | 含义 | 标准字段 |
|---|---|---|
| `config` | 应用级机密（签名密钥、会话密钥） | `secret_key`、`encryption_key`、`jwt_secret` |
| `db` | 使用方的数据库凭据 | `host`、`port`、`database`、`username`、`password`、`dsn` |
| `oidc` | 本应用在 `sso.iam.shared` 上的 OIDC 客户端 | `issuer`、`client_id`、`client_secret`、`redirect_uri` |
| `api` | 本应用自身的管理/API 令牌，供操作员和自动化使用 | `url`、`token` |
| `admin` | 紧急访问本地账号（S6） | `username`、`password` |
| `clients` | 本应用**颁发**给调用方的密钥（颁发方副本） | 每个调用方身份一个字段，字段名 = 身份 ID |
| `provider-<vendor>` | 外部供应商的凭据（S4） | `api_key`、`base_url`、`account_id` |
| `<capability>` | 使用方**为访问**另一个能力而持有的凭据（使用方副本） | 按颁发时的字段（`api_key`、`token`、`url`） |
| `tls` | 不使用 ACME 时的证书材料 | `cert`、`key`、`ca` |
| `join-tokens`、`regcred`、`webhook` | 用途单一、命名明确的运维条目 | 按需 |

字段规则：`snake_case`，小写；`url` 始终包含协议方案；字段不以环境变量命名（`MESH_API_KEY` → `api_key`）。

`custom_metadata`（S8）：`plane, domain, capability, product, env, owner, tier, data_class, rotation`（`90d` | `365d` | `manual`），`issuer`（创建该机密的身份），`consumer`（读取该机密的身份）。

## 5. 策略

| 类型 | 名称 | 授予权限 |
|---|---|---|
| 使用方策略 | `<identity-id>`（例如 `corp-ai-litellm`、`agent-code-review`） | 对自身的 `<mount>/<domain>/<capability>/<env>/*` 拥有 `read`；对所需的使用方副本拥有 `read` |
| 层级策略（人员） | `tier-t0-superadmin`、`tier-t1-platform-ops`、`tier-t2-developer`、`tier-t3-readonly` | t0：所有挂载点，包括 `admin` 条目，并触发告警；t1：`shared/`、`platform/`、`eng/`，`admin` 除外；t2：`eng/` 和 `<product>/` 中非 `admin` 的条目；t3：仅 `list` + 元数据 |
| 角色策略 | `role-<function>` | 针对该职能的域范围读写权限（例如 `role-security-engineers` → `*/sec/*`） |
| 限定读取策略 | `<identity-id>-<capability>-ro` | 当使用方恰好需要一个他方条目时使用，例如 `eng-sdlc-jenkins-packages-ro` |

HCL 路径形式：`path "<mount>/data/<domain>/<capability>/<env>/*"`，列表操作另加 `metadata/`。除 `tier-t0-superadmin` 外，对所有策略拒绝 `*/admin`。

## 6. 认证角色与令牌

| 认证方式 | 角色名称 | 绑定对象 | 策略 | TTL |
|---|---|---|---|---|
| `approle` | `<identity-id>` | 每台主机一个 secret-id，绑定 CIDR | `<identity-id>` | 令牌 1 小时，可续期至 24 小时 |
| `jwt-<idp>` | `<group-id>`（`tier-t1-platform-ops`、`role-developers`） | IdP 组声明 (claim) | 对应的层级/角色策略 | 8 小时 |
| `jwt-spire` | `<identity-id>` | SPIFFE ID `spiffe://mess.systems/<plane>/<domain>/<capability>` | `<identity-id>` | 1 小时 |
| `kubernetes-<cluster>` | `<namespace>-<serviceaccount>` | SA + 命名空间 | `<identity-id>` | 1 小时 |

令牌的 `display_name` = 身份 ID。除紧急访问外，拒绝长期有效的 root 令牌和周期性令牌。

## 7. 迁移——遗留形态 → 目标（示意）

下列遗留路径为虚构，但展示了单个 `secret/` 挂载点中常见的五种形态：按供应商、按产品、按团队、按人员和按层级。

| 遗留（`secret/`） | 目标 | 说明 |
|---|---|---|
| `bots/code-review`（+ `/tracing`） | `corp/ai/agent-code-review/prd/gateway`、`.../llm-traces` | 使用方副本；条目以其所解锁的能力命名 |
| `llm-gateway/clients` | `corp/ai/gateway/prd/clients` | 颁发方副本；字段名 → 身份 ID（[04](04-identity-conventions.md) §9） |
| `llm-gateway/keys` | `corp/ai/gateway/prd/provider-acmeai`、`provider-acmecloud` | 每个供应商一个条目 |
| `acmecloud/vm-api` | `shared/infra/compute/prd/provider-acmecloud` | 供应商作为节点 → 供应商作为条目 |
| `grafana/oidc` | `shared/obs/dashboards/prd/oidc` | 产品节点 → 能力节点 |
| `postgres/admin` | `shared/data/sql/prd/admin` | 紧急访问 |
| `ci/registry-pull` | `eng/sdlc/ci/prd/oci` | 使用方 = CI |
| `shopfront/db` | `shopfront/api/prd/db` | 已是产品形态；补充组件和环境 |
| `services/<other>` | 放到使用方能力之下 | 逐一处理 |
| `dev/<username>/*` | **拒绝** | S5——使用密码管理器或 IdP 颁发的令牌 |
| `platform/*`、`admin/*`（按层级划分） | §5 中的层级策略 | 路径不是层级 |

UI：`https://<legacy-host>/ui/vault/secrets/secret/list` → `https://secrets.iam.shared.svc.mess.systems/ui/vault/secrets/<mount>/kv/list/<domain>/<capability>/<env>/`。

## 8. 完整示例——LLM 网关

```
corp/ai/gateway/prd/config                  secret_key
corp/ai/gateway/prd/clients                 agent-code-review, agent-docs-writer, user-jdoe-ide, svc-corp-collab-mattermost, ...
corp/ai/gateway/prd/provider-acmeai         api_key, base_url
corp/ai/gateway/prd/provider-acmecloud      api_key, base_url, account_id
corp/ai/gateway/prd/provider-acmesearch     api_key, base_url
corp/ai/gateway/prd/llm-traces              public_key, secret_key, url
corp/ai/gateway/prd/oidc                    issuer, client_id, client_secret
corp/ai/agent-code-review/prd/gateway       api_key, url          # consumer copy of one field of clients
```

策略 `corp-ai-litellm`：读取 `corp/data/ai/gateway/prd/*`。策略 `agent-code-review`：读取 `corp/data/ai/agent-code-review/prd/*`。两者都无法读取对方的内容。AppRole `agent-code-review` 绑定到其运行器 (runner) 的 CIDR；目标替代方案是使用 `spiffe://mess.systems/corp/ai/agent-code-review` 的 `jwt-spire`。

## 9. 拒绝规则

- 路径深度超过 `<mount>/<a>/<b>/<env>/<item>`。
- 供应商名称作为路径节点（`acmecloud/`、`github/`）——供应商应为条目（`provider-*`）。
- 产品名称作为平面挂载点下的节点（`mongodb/`、`grafana/`）——应改用能力。
- 路径中没有 `env`。
- 字段以环境变量命名，或使用大写/kebab 风格。
- `admin` 条目可被任何非 t0 策略读取。
- 策略或角色名称与身份名称不一致。
- 将生产机密复制到 `dev|tst|stg`。
