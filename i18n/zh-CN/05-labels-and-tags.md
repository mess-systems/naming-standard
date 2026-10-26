[English](../../05-labels-and-tags.md) | [Русский](../ru/05-labels-and-tags.md) | **简体中文**

> **译文说明。** 本文为标准 v2.1 版本的译文。英文文本为规范性文本：如有任何不一致，以英文版本为准。

# 标签与标记：成本标签、CI 运行器标签、Kubernetes、云、议题标签

> **状态：** v2.1，持续演进。2026-10-15 采纳。将[十个元数据键](01-naming-conventions.md)扩展到所有键值标签。
> **与产品无关。** 此处提到的产品（Forgejo、GitHub、Kubernetes、Cloudflare、cloud.ru、OpenTofu）仅为示例；规则适用于任何支持标签的平台。
> **标签从不作为授权依据**，与名称的规则相同。

## 为什么

在自托管代码平台上新建的一个组织无法运行任何 CI 作业：其工作流请求的运行器标签只存在于注册到另一个组织的运行器上。标签无法说明运行器在哪里可见，也没有所有组织都能依赖的运行器。作业在队列中等待且没有任何报错。本部分明确作用域，定义默认运行器，并对成本标签、Kubernetes 标签、云标签和议题标签使用同一语法。

## 1. 通用语法

### 1.1 字符

- 键：`[a-z][a-z0-9-]*`；在平台支持前缀的地方（Kubernetes）可加可选前缀 `<org-domain>/`，其他地方不加 `<org>.` 前缀。
- 值：`[a-z0-9][a-z0-9-]*`，取自本标准的代码列表、目录 ID 或组 ID。
- 新键中不使用大写字母、空格和下划线。十个元数据键中的下划线（`data_class`）在标签中写成连字符（`data-class`），因为一些平台的值不接受 `_`，而连字符本来就是本标准的分隔符。
- 标记从不以数字开头，见 [01 第 1 节](01-naming-conventions.md)。

### 1.2 键

| 键 | 取值 | 来源 |
|---|---|---|
| `plane` | plane 代码 | [01 第 4.1 节](01-naming-conventions.md) |
| `domain` | 域代码 | [01 第 4.2 节](01-naming-conventions.md) |
| `capability` | capability 代码 | [01 第 4.3 节](01-naming-conventions.md) |
| `product` | 安装代码 | 目录 |
| `env` | `prd stg tst dev` | [01 第 4.4 节](01-naming-conventions.md) |
| `owner` | 组 ID，从不是个人 | [04 第 5 节](04-identity-conventions.md) |
| `data-class` | `public internal confidential restricted` | [01 第 2 节](01-naming-conventions.md) |
| `cost-center` | 目录代码，例如 `cc-platform` | 见第 2 节 |
| `initiative` | 目录代码，例如 `ini-ai-gateway` | 见第 2 节 |

### 1.3 各平台限制

| 平台 | 键长度 | 值长度 | 字符集 | 其他 |
|---|---|---|---|---|
| Kubernetes 标签 | 名称 63，可选 DNS 子域前缀最长 253 | 63，可为空 | 字母数字、`-`、`_`、`.`；以字母数字开头和结尾 | 注解：每个对象总大小 256 KiB |
| Cloudflare Resource Tagging | 256 | 1024，可为空 | 键：Unicode 字母、数字、`_`、`.`、`-`；区分大小写 | 测试版：每个账户 10 000 个标签；`PUT` 会替换资源的全部标签 |
| cloud.ru Tag Management Service（Advanced） | 36 | 43 | 键：字母、数字、`_`、`-`；值还允许 `.` | 每个资源 10 个标签；每个键一个值 |
| cloud.ru Evolution | 待确认 | 待确认 | 待确认 | 待确认说明：公开文档中尚未确认限制（2026-10-15 检查） |
| Forgejo 议题/PR 标签 | 名称，最后一个 `/` 之前为作用域 | | 自由文本 | 必须有颜色；作用域可设为互斥 |
| GitHub 议题/PR 标签 | 名称最长 50 | | 自由文本 | 必须有颜色 |
| Forgejo / GitHub 运行器标签 | 短标记 | | 保持在 `[a-z0-9-]` | 由 `runs-on` 精确匹配 |

设计上限取最小公共值：**键最长 36 个字符，值最长 43 个字符**。使用上述代码时，所有键值对都在此范围内。

### 1.4 标签中禁止出现的内容

用户名或账号、电子邮件地址、主机名、IP 地址、序列号、机密或机密路径、用于授权的访问组名称、客户名称，以及任何与家庭或儿童有关的信息。与名称适用同一列表。标签的可见范围往往比资源本身更广，例如计费导出。

## 2. 成本标签（FinOps）

| 键 | 必填 | 取值 | 示例 |
|---|---|---|---|
| `cost-center` | 是 | 目录代码 `cc-<name>` | `cc-platform` |
| `owner` | 是 | 组 ID | `role-platform-engineers` |
| `env` | 是 | env 代码 | `prd` |
| `capability` | 是 | capability 代码 | `inference` |
| `initiative` | 否 | 目录代码 `ini-<name>` | `ini-exo-pilot` |
| `plane` | 否 | plane 代码 | `platform` |

- `owner` 与 `cost-center` 分开：所有者运维资源，成本中心为其付费。
- 成本维度是 `capability` 而不是 `product`。按 capability 统计的支出在更换产品后依然有效。
- 缺少四个必填标签的资源会出现在成本检查报告中，并且 IaC 模块不会创建它（OpenTofu 模块校验标签）。
- `cc-*` 和 `ini-*` 代码在使用前登记到目录中。目录中不存在的标签值视为错误。
- 共享资源使用平台组作为 `owner`、平台作为 `cost-center`；向使用方分摊通过报表完成，而不是通过标签。

**产品轮廓。** 其必填成本标签为 `cost-center`、`owner`、`env`、`product`、`domain`、`service`，不设 `capability`。治理标签及其类别（必填、条件、派生）的完整列表见 [07 治理标签](07-deployment-and-tenants.md)。

## 3. CI 运行器标签

Forgejo Actions 和 GitHub Actions 都通过将 `runs-on` 与运行器标签匹配来选择运行器。运行器在实例、组织或仓库级别注册（GitHub 上为企业、组织或仓库级别，并有运行器组）。作业只能看到注册在其自身级别或更高级别的运行器。

### 3.1 标签形式

| 标签 | 含义 | 示例 |
|---|---|---|
| `default` | 普通作业的基础运行器；在**实例**级别注册，所有组织可见 | `runs-on: default` |
| `<purpose>` | 运行器的用途 | `docker`、`review`、`gpu`、`build`、`deploy` |
| `<purpose>-<isolation>` | 存在多种隔离级别时，用途加隔离级别 | `docker-socketless`、`docker-sock` |
| `scope-<level>` | 运行器注册的位置，仅供参考 | `scope-instance`、`scope-org`、`scope-repo` |

隔离代码，从强到弱：

| 代码 | 含义 |
|---|---|
| `vm` | 每个作业运行在自己的 VM 或 MicroVM 中 |
| `socketless` | 容器作业，无法访问宿主机容器守护进程（rootless 构建器） |
| `sock` | 作业可访问宿主机容器套接字；等同于运行器宿主机上的 root |
| `host` | 作业直接在运行器宿主机上运行 |

### 3.2 规则

- 每个代码托管实例必须（MUST）在实例级别至少提供一个带 `default` 标签的运行器。这样新组织第一天就能运行 CI。
- 需要 `default` 以外能力的工作流应指定用途标签。如果该用途标签未在实例级别注册，工作流的 README 中须说明。
- `sock` 和 `host` 运行器不得（MUST NOT）在实例级别注册，只能是组织或仓库级运行器，因为它们让作业控制宿主机。
- `scope-*` 标签仅供参考，从不用于 `runs-on`；可见性由代码托管平台决定。
- 运行器名称（不是标签）遵循本标准的主机形式；标签从不包含主机名。
- 在 Forgejo 中，运行器标签在冒号后还带有执行后端（`docker-socketless:docker://<image>`）。只有冒号之前的部分是标签名，并遵循本语法。

## 4. Kubernetes 标签和注解

### 4.1 标签

| 键 | 取值 | 必填 |
|---|---|---|
| `app.kubernetes.io/name` | 产品代码 | 是 |
| `app.kubernetes.io/instance` | 本标准对象形式中的应用名称 | 是 |
| `app.kubernetes.io/component` | 组件 | 适用时 |
| `app.kubernetes.io/part-of` | capability 代码 | 是 |
| `app.kubernetes.io/managed-by` | 工具，例如 `argocd`、`helm` | 是 |
| `app.kubernetes.io/version` | 版本 | 否 |
| `mess.systems/plane` | plane 代码 | 是 |
| `mess.systems/domain` | 域代码 | 是 |
| `mess.systems/env` | env 代码 | 是 |
| `mess.systems/owner` | 组 ID | 是 |
| `mess.systems/cost-center` | `cc-*` | 是 |
| `mess.systems/data-class` | 数据分级 | 存储数据时 |

在公开标准中前缀为 `mess.systems/`。采用本标准的组织将其替换为自己的域名（例如 `<org-domain>/`）。

### 4.2 标签还是注解

- **标签：** 简短、稳定，用于选择器、成本报表或策略：即上表中的键。
- **注解：** 其他一切：目录或运行手册链接、`initiative`、描述、构建元数据、变更 ID、联系渠道。
- 每次部署都可能变化的值（提交哈希、构建号）从不作为标签。

## 5. 云标签

- **Cloudflare：** 通过 Resource Tagging 使用原生键值标签。使用第 1.2 节的键，不加前缀。标签区分大小写，因此只用小写。由于 `PUT` 会替换全部标签，标签只由 IaC 管理，不手工修改。
- **cloud.ru：** 原生键值标签。在 Tag Management Service 中，键最长 36 个字符，值最长 43 个字符，每个资源最多 10 个标签。第 2 节的六个键加上 `data-class` 共 7 个。Evolution 的限制尚未确认（待确认说明）。
- 不支持键值标签的平台使用现有的 `<key>-<value>` 形式（`env-prd`）。

## 6. 议题和 PR 标签

### 6.1 语法

`<prefix>/<value>`。Forgejo 将最后一个 `/` 之前的文本视为作用域，并可将作用域设为互斥。GitHub 没有作用域，因此使用相同名称，互斥性由工作流检查。

| 前缀 | 互斥 | 颜色 | 允许的值 |
|---|---|---|---|
| `type` | 是 | 蓝色 `#1d76db` | `bug feature docs chore decision research` |
| `stream` | 否 | 绿色 `#0e8a16` | 目录中的工作流列表 |
| `horizon` | 是 | 紫色 `#5319e7` | `now next later` |
| `contour` | 是 | 橙色 `#d93f0b` | `public private` |
| `initiative` | 否 | 灰色 `#6a737d` | 目录中的 `ini-*` 代码 |

- 每个前缀一种颜色，一眼即可看出标签的前缀。
- 值使用与第 1.1 节相同的字符集。
- `initiative/` 的值与成本标签 `initiative` 使用相同代码，因此工作与支出通过同一个键关联。

### 6.2 旧形式标签

旧形式 `prefix:value`（`type:bug`）的标签重命名为 `prefix/value`（`type/bug`）。互斥前缀在 Forgejo 中由作用域标签保证，在 GitHub 中由工作流检查保证。
