[English](../../08-operations-objects.md) | [Русский](../ru/08-operations-objects.md) | **简体中文**

> **译文说明。** 本文为标准 v2.7 版本的译文，源提交 `a60b331`（含链接编辑修订）。英文文本为规范性文本：如有任何不一致，以英文版本为准。

# 08. 运维对象

系统运行时出现的对象的形式：分支与标签、CI 作业、备份、虚拟机管理程序客户机、网关路由、DNS 记录和 PostgreSQL 对象。轴和字符沿用[命名约定](01-naming-conventions.md)；没有新的语法。

## 1. Git 分支与标签

| 对象 | 形式 | 示例 |
|---|---|---|
| 默认分支 | `main` | `main` |
| 工作分支 | `<identity-id>/<topic>` | `jdoe/pg-access`、`user-jdoe-cursor/pg-access`、`agent-code-review/fix-typo` |
| 针对议题的工作分支 | `<identity-id>/<issue>-<topic>` | `jdoe/142-pg-access` |
| 发布维护分支 | `release/v<X>.<Y>` | `release/v1.4` |
| 发布标签 | `v<X>.<Y>.<Z>`，不可变，与[容器镜像](07-deployment-and-tenants.md#125-容器镜像与镜像仓库)相同 | `v1.4.0` |
| 预发布标签 | `v<X>.<Y>.<Z>-rc.<n>`（[SemVer](https://semver.org/)） | `v1.4.0-rc.1` |

- `<identity-id>` 是[身份类型](04-identity-conventions.md#2-身份类型)中的 ID：人员、人员工具或智能体，因此分支表明是谁创建的。
- `<topic>` 使用 `a-z0-9-`，最长 40 个字符，绝不包含工具、主机、客户或机密。
- 变更类型（feature、fix、docs）是拉取请求的标签（[议题和 PR 标签](05-labels-and-tags.md#6-议题和-pr-标签)），不是分支名称的一部分。
- 智能体和人员工具不向 `main` 或 `release/*` 推送；这是分支保护规则，而不是命名规则。

## 2. CI 与计划任务

### 2.1 工作流与作业

| 对象 | 形式 | 示例 |
|---|---|---|
| 工作流文件 | `<purpose>.yml` | `ci.yml`、`release.yml`、`iac-plan.yml`、`iac-apply.yml` |
| 作业 ID | `<verb>[-<object>]` | `lint`、`test`、`build-image`、`plan`、`apply` |
| 部署环境 | 环境代码（[环境与站点](01-naming-conventions.md#44-环境与站点)） | `prd`、`stg` |
| 制品 | `<application>-<version>[-<platform>]` | `eng-sdlc-forgejo-v1.4.0-linux-amd64` |

### 2.2 运行器

运行器标签遵循 [CI 运行器标签](05-labels-and-tags.md#3-ci-运行器标签)；运行器按主机形式命名，或作为组件 `ci-runner` 命名（[基础设施即代码与运行器](07-deployment-and-tenants.md#127-基础设施即代码与运行器)）。没有新的形式。

### 2.3 计划任务（cron、systemd timer、CronJob）

| 对象 | 形式 | 示例 |
|---|---|---|
| 任务 | `<application>-<action>[-<schedule>]` | `shared-data-postgres-backup-daily` |
| Kubernetes CronJob | 同上但去掉平面，当命名空间已包含平面时 | `postgres-backup-daily` |
| `<schedule>` | `hourly`、`daily`、`weekly`、`monthly`，或省略 | `daily` |

## 3. 备份与快照

| 对象 | 形式 | 示例 |
|---|---|---|
| 备份仓库（repository、datastore、存储桶） | 存储桶形式：`<plane>-infra-backup-<env-or-class>` | `shared-infra-backup-prd` |
| 备份作业 | `<application>-<env>-<schedule>` | `shared-data-postgres-prd-daily` |
| 快照 | `<application>-<env>-<timestamp>` | `shared-data-postgres-prd-20261031t020000z` |
| `<timestamp>` | UTC，ISO 8601 基本格式，小写：`YYYYMMDDtHHMMSSz` | `20261031t020000z` |
| 快照标签 | `application`、`env`、`kind`（`full`、`incr`、`wal`）、`retention`（`daily`、`weekly`、`monthly`） | `kind=full` |

- 快照名称中没有主机：快照属于应用，而不是机器。
- 备份加密密钥遵循机密约定的[路径语法](03-secrets-conventions.md#3-路径语法)：`<mount>/infra/backup/<env>/<application>`。

## 4. 虚拟机管理程序客户机

| 对象 | 形式 | 示例 |
|---|---|---|
| 虚拟机或容器名称 | 主机名（[对象形式](01-naming-conventions.md#5-对象形式)） | `dc1-shared-data-postgres-prd-01` |
| 客户机标签 | [标签](05-labels-and-tags.md)中的键（`plane`、`domain`、`capability`、`env`、`owner`） | `plane=shared` |
| 资源池 | `<plane>` 或 `<plane>-<env-class>` | `shared`、`eng-nonprod` |
| 镜像模板 | `tpl-<os>-<version>` | `tpl-debian-13` |

客户机的数字 ID（虚拟机 ID、容器编号）属于清单，而不是名称：它绝不用于 DNS、组、机密路径或文档。如果需要按平面划分范围，记录在站点目录中，而不是标准中。

## 5. API 网关

| 对象 | 形式 | 示例 |
|---|---|---|
| 产品公共界面上的路由 | `<product>-<service>-<version>` | `x-store-v1` |
| 到内部能力的路由 | `<application>[-<purpose>]` | `corp-ai-gateway-mcp` |
| 上游（后端） | `<application>-<env>` 或 `<product>-<service>-<env>` | `x-store-prd` |
| 使用方（consumer） | [网关客户端身份](04-identity-conventions.md#9-网关客户端身份)中的客户端 ID | `svc-x-records-store`、`agent-code-review` |
| 监听器（listener） | `<protocol>-<port>` | `https-443` |
| MCP 目标、LLM 路由前缀 | 不变，见[对象形式](01-naming-conventions.md#5-对象形式) | `k8s`、`dashboards` |

## 6. DNS 记录

| 记录 | 形式 | 示例 |
|---|---|---|
| 内部服务 | `A`/`AAAA`，或指向语法 A 规范名称的 `CNAME` | `sql.data.shared.svc.mess.systems` |
| 主机 | `<host>.mgmt.mess.systems`：管理区域与 `svc.mess.systems` 一样是内部区域，只包含主机，站点已在主机名中 | `dc1-shared-data-postgres-prd-01.mgmt.mess.systems` |
| 产品 | 界面指向产品代理或负载均衡器的 `CNAME` | `arch.x.mess.systems` |
| 产品通配符 | 每个产品域名一个，每个非生产环境一个：`*.<product>.x.mess.systems`、`*.<env>.<product>.x.mess.systems` | `*.arch.x.mess.systems` |
| 所有权验证（ACME、服务） | `_<purpose>.<name>` `TXT` | `_acme-challenge.arch.x.mess.systems` |
| CAA | 在品牌区域及其子区域上 | `x.mess.systems CAA 0 issue "<ca>"` |

- 通配符只覆盖一个标签（[RFC 4592](https://www.rfc-editor.org/rfc/rfc4592)）：`*.x.mess.systems` 匹配 `arch.x.mess.systems`，但不匹配 `api.stg.arch.x.mess.systems`，后者需要自己的通配符或逐个名称的记录。
- 语法 A 和 B 之外的每条公共记录都列在 `catalog/dns-exceptions.yaml` 中（[语法 B：公共](01-naming-conventions.md#32-语法-b公共)）。

## 7. PostgreSQL 对象

| 对象 | 形式 | 示例 |
|---|---|---|
| 集群，企业轮廓 | 应用：`<plane>-<domain>-<product>` | `shared-data-postgres` |
| 集群，产品轮廓 | [环境类别](07-deployment-and-tenants.md#121-环境类别) | `x-records-store-nonprod` |
| 数据库、模式 | [对象形式](01-naming-conventions.md#5-对象形式) | `eng_sdlc_git_prd` |
| 角色、临时用户 | [数据库角色](04-identity-conventions.md#11-数据库角色)、[临时数据库用户](04-identity-conventions.md#111-临时数据库用户) | `eng_sdlc_git_ro`、`v_oidc_jdoe_eng_sdlc_git_ro_20261031t020000z_k7m2qa` |
| 复制槽 | `<consumer>_<purpose>`（snake_case） | `svc_shared_infra_backup_wal` |
| 发布、订阅 | `<database>_<purpose>` | `eng_sdlc_git_prd_cdc` |

## 8. 拒绝规则

| 迹象 | 违反的规则 |
|---|---|
| 分支没有 `<identity-id>/`，或用工具名代替 ID（`cursor/fix`） | [Git 分支与标签](#1-git-分支与标签) |
| 发布后被改写的发布标签 | [Git 分支与标签](#1-git-分支与标签) |
| 快照、作业或路由名称中含有主机或 IP 地址 | [备份与快照](#3-备份与快照)、[API 网关](#5-api-网关) |
| 虚拟机 ID 或容器编号作为名称或名称的一部分 | [虚拟机管理程序客户机](#4-虚拟机管理程序客户机) |
| 位于通配符下两级、却依赖该通配符的名称 | [DNS 记录](#6-dns-记录) |
| 语法之外的公共 DNS 记录且未在例外登记册中登记 | [DNS 记录](#6-dns-记录) |
