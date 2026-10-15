# 06. 终端约定

> 译文仅供参考；规范文本为[英文版](../../06-endpoint-conventions.md)。

员工设备（笔记本和台式机）如何命名、打标签，以及为何不进入服务 DNS。这些设备的参考架构见 [endpoint blueprint](https://github.com/mess-systems/blueprints/tree/main/endpoint)。

## 1. 为什么单独成族

[01 第 5 节](01-naming-conventions.md)中的**主机 / 容器 / 虚拟机**形式（`<site>-<plane>-<domain>-<product>-<env>-<NN>`）描述的是已部署的服务基础设施。笔记本没有真实的 `site`、`domain`、`product` 和 `env`：设备会移动、运行多种产品，也不是部署环境。强行套用只会编造取值并导致重命名。

这是新的对象**族**，不是新的 DNS 语法，“没有语法 C”的规则依然成立。

## 2. 形式

```
<profile>-<form>-<asset-id>          # std-lt-a1b2c3, eng-dt-d4e5f6, paw-lt-g7h8j9
```

| 维度 | 代码 | 含义 |
|---|---|---|
| `profile` | `std` | 标准员工终端（默认基线） |
| | `eng` | 确有独立基线的工程终端：构建工具、AI 编码代理、沙箱、不同的遥测。仅装了 IDE 不算。 |
| | `paw` | 专用、加固的特权访问工作站，只用于管理工作 |
| `form` | `lt` | 笔记本 |
| | `dt` | 台式机或固定工作站 |
| `asset-id` | 6 个字符 | 由权威资产系统分配，设备生命周期内不变 |

- **不用 `dev`**：它已是环境代码，同一代码不得有第二种含义。
- **asset-id 字母表**：`a-z 2-9`，去掉 `o l i`（排除 `0 o 1 l i`），首字符必须是字母。符合规则的现有资产标签可以使用。禁止使用序列号：它会泄露制造商且不透明。
- 正则：`^(std|eng|paw)-(lt|dt)-[a-hjkmnp-z][a-hjkmnp-z2-9]{5}$`。BYOD 别名：`^byod-(lt|dt)-[a-hjkmnp-z][a-hjkmnp-z2-9]{5}$`。

## 3. 长度

名称为 **13** 个字符，BYOD 别名为 **14** 个字符。硬性上限为 15 个字符，依据是 [Windows Autopilot 名称模板](https://learn.microsoft.com/en-us/autopilot/profiles)和 [NetBIOS 名称](https://learn.microsoft.com/en-us/troubleshoot/windows-server/active-directory/naming-conventions-for-computer-domain-site-ou)。[Intune 重命名](https://learn.microsoft.com/en-us/intune/device-management/actions/rename)对 Windows 允许最多 63 个字符（2026-10-12 核对），但不适用于混合加入的设备。余量只有 2 个字符：新的配置档代码保持 3 个字母，形态代码保持 2 个字母。

## 4. 名称中绝不包含

站点、环境、域、产品、用户名、部门、操作系统、型号、序列号、合规状态或特权层级。**名称从不授予访问权限。**

## 5. 元数据

键：`plane`、`owner`、`tier`、`data_class`、`exposure`，以及 `ownership`（`org`、`personal`、`partner`）、`endpoint_profile`、`device_form`、`asset_id`、`assigned_to`（IdP 主体，绝不进入名称）、`management`（`full`、`work-profile`、`registered`）和 `compliance_state`（来自设备管理工具，绝不进入名称）。`capability` 始终为 `endpoint`。作为标签时按 [05](05-labels-and-tags.md) 使用连字符形式（`endpoint-profile`、`device-form`）。记录以设备管理或目录中的设备 ID 为键，而不是主机名。完整表格见[英文版](../../06-endpoint-conventions.md#5-metadata)。

**配置档与平面。** 配置档决定基线，平面决定信任区：`eng` 终端通常为 `plane=eng`，`std` 和 `paw` 通常为 `corp` 或 `shared`。目录必须校验这一组合。

## 6. 能力代码 `endpoint`

`endpoint` 是员工设备上运行的一切的[能力代码](01-naming-conventions.md)：设备管理代理、安全与访问代理、远程支持、AI 客户端管控、本地容器运行时。它用于目录、技术雷达和成本标签，从不出现在终端名称或服务 DNS 中。

`endpoint` 属于域 `device`（员工设备，不含网络设备和 IoT）。技术雷达和软件目录使用同一代码作为类别，词汇统一。服务器侧的虚拟工作场所（浏览器交付的桌面）是同一域中的能力 `vdi`，按普通服务命名。终端名称中从不包含域。

## 7. DNS 与登记

- 服务区（`*.svc.mess.systems`）中不为终端建静态记录。`std-lt-a1b2c3.corp.mess.systems` 之类的名称属于语法 C，予以拒绝。名称可以出现在本地网段的动态 DNS 或 mDNS 中。
- 名称须在设备注册**之前**登记到目录。

## 8. BYOD

个人设备保留自己的主机名，没有企业名称、DNS 记录和 SPIFFE 节点身份。设备管理工具可另设别名 `byod-<form>-<asset-id>`，仅用于台账和审计。策略只依据权威属性（所有权、注册方式、证明、证书签发者、合规），从不依据别名。

## 9. PAW 是设备类别，不是特权层级

“名称中不得含层级”（`admin.`、`t0-`）的规则不变。`paw` 被允许，因为它表示有独立加固基线的设备类别。即使每个层级有单独的硬件，主机名仍是 `paw-<form>-<asset-id>`，层级只记录在 `tier` 元数据和配置档名称（如 `paw-t0`）中。从名称能看出这是 PAW，层级要到目录里查。普通笔记本不会因为用户是管理员就被命名为 `paw`。

## 10. SPIFFE

通过证明的完全托管设备可以获得节点 ID `spiffe://mess.systems/node/<终端名称>`，例如 `spiffe://mess.systems/node/std-lt-a1b2c3`（[04 第 8 节](04-identity-conventions.md)）。绝不使用用户名。BYOD 没有节点身份。

## 11. 拒绝情形

| 迹象 | 违反的规则 |
|---|---|
| 终端名称中含用户名、部门、站点、环境、操作系统、型号、序列号、合规状态或层级（`ws-jdoe-01`、`paw-t0-...`） | 第 4 节 |
| 笔记本或台式机使用主机 / 容器 / 虚拟机形式命名 | 第 1 节 |
| 以 `dev` 作为终端配置档 | 第 2 节 |
| 在服务区为终端建静态 DNS 记录 | 第 7 节 |
| 为 BYOD 设备分配企业终端名称、DNS 记录或 SPIFFE 节点 ID | 第 8 节 |
| 以序列号作为 `asset-id` | 第 2 节 |
