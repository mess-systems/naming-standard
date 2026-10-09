[English](../../01-naming-conventions.md) | **Русский** | [简体中文](../zh-CN/01-naming-conventions.md)

> **Перевод.** Перевод стандарта версии v2, исходный коммит `b6791c2`. Нормативным является английский текст: при любых расхождениях преимущество имеет английская версия.

# Соглашения об именовании v2 — mess.systems

> **Статус:** v2, развивается. Самодостаточен: все правила, необходимые для применения, находятся в этом репозитории.
> **Область действия:** любой идентификатор, который читает человек или машина: DNS, хосты, репозитории, образы, бакеты, базы данных, Kubernetes, наблюдаемость, ID каталога. Секреты → [03](03-secrets-conventions.md). Идентичности → [04](04-identity-conventions.md). Разобранный пример миграции → [02](02-worked-example.md).
> **Домен организации:** `mess.systems` — собственный домен организации, он используется во всём документе. При адаптации стандарта подставьте свой зарегистрированный домен.

## 1. Правила для символов (действуют для всех семейств)

| Правило | Значение | Почему |
|---|---|---|
| Алфавит | `a-z 0-9 -` | имена хостов по RFC 1123, имена Kubernetes, S3, реестры контейнеров, большинство IdP |
| Регистр | только строчные | DNS нечувствителен к регистру; всё остальное — чувствительно |
| Разделитель между осями | `-` в именах, `.` в DNS и ID с точками, `/` в путях | у каждого разделителя одно значение |
| Многословный токен | через дефис (`data-catalog`), никогда слитно и не в camelCase | читаемость; DNS это допускает |
| `_` | только там, где `-` недопустим: идентификаторы SQL, переменные окружения, имена полей секретов | вынуждено системой |
| Длина метки | ≤ 63 символов; FQDN ≤ 253 | RFC 1035 |
| `-` в начале или в конце | никогда | RFC 1123 |
| Цифры | разрешены; токен никогда не начинается с цифры | значения меток k8s, shell |
| Порядковые номера | две цифры с ведущим нулём (`01`) | правильная сортировка |
| Зарезервированные слова | `api`, `www`, `app`, `admin`, `internal`, `public`, `prod`, `test`, `svc`, `local`, `cluster` — никогда не используются как код плоскости, домена, возможности или продукта | конфликтуют с токенами грамматики или RFC 6762/6761 |

## 2. Десять ключей метаданных

Каждое семейство объектов несёт одни и те же ключи. DNS кодирует первые четыре (плюс окружение, если оно не prod). Остальные хранятся в каталоге соответствующего семейства.

| Ключ | Значения | Где кодируется |
|---|---|---|
| `plane` | `shared corp eng platform ext <product>` | DNS, хост, репозиторий, метка k8s, точка монтирования секретов |
| `domain` | коды из §4.2 | DNS, хост, репозиторий, схема |
| `capability` | коды из §4.3 | самая левая метка DNS, путь SPIFFE, цель MCP |
| `product` | код установки (`keycloak`, `gitea`) | хост, репозиторий, образ, пространство имён k8s |
| `env` | `prd dev tst stg` | DNS (только не prod), хост, схема, путь секрета (всегда) |
| `owner` | ID группы из [04](04-identity-conventions.md) §5 | каталог, метаданные секретов, метка k8s |
| `tier` | `t0 t1 t2 t3` (уровни привилегированного доступа, [04](04-identity-conventions.md) §3.1) | каталог, группа идентичностей |
| `scope` | `dev tst stg prd` — наивысшее окружение, для которого объект сертифицирован | только каталог |
| `data_class` | `public internal confidential restricted` | каталог, метаданные секретов, тег бакета |
| `exposure` | `mesh lan public` | каталог, группа mesh-сети — **никогда в имени** |

Ключи меток Kubernetes: `mess.systems/<key>`. Теги гипервизора и облака: `<key>-<value>` (`plane-corp`) или нативные теги «ключ/значение», где они поддерживаются. Метки реестра контейнеров: так же, как теги гипервизора. Менеджер секретов: `custom_metadata.<key>`.

## 3. DNS — две грамматики и ничего больше

### 3.1 Грамматика A — внутренняя

```
<capability>.<domain>.<plane>.svc.mess.systems                 # prod
<capability>.<domain>.<plane>.<env>.svc.mess.systems           # dev|tst|stg
<surface>.<product>.svc.mess.systems                           # internal product (plane = product)
```

- `svc.mess.systems` — внутренняя зона (split-horizon, внутренний УЦ + ACME). Публично не делегируется. `svc` здесь означает «зона сервисов» и не связан с Kubernetes `*.svc.cluster.local` — другой суффикс, другой резолвер.
- Самая левая метка — это **возможность (capability)**, а не продукт (`git`, а не `gitea`). Продукт — это предмет инвентаризации, а не часть имени.
- В prod окружение опускается. Во всех остальных местах (хосты, схемы, секреты) `prd` пишется.
- Одна установка → ровно одно каноническое FQDN. Псевдонимы — это редиректы, а не имена.
- **Метка никогда не является входными данными для авторизации.** Доступность и права определяются группами mesh-сети, группами IdP и политиками менеджера секретов ([04](04-identity-conventions.md)). Два потребителя одной установки используют одно и то же имя и разные группы.

### 3.2 Грамматика B — публичная

```
<surface>.<product-domain>            # www | app | api | docs | status | auth
<capability>.apps.mess.systems        # ext plane on the brand domain
www.mess.systems                      # brand
```

- Публичные имена никогда не содержат плоскость, домен, окружение или вендора.
- `apps.mess.systems` — **единственная** публичная подзона бренда. В ней размещаются возможности `ext` (партнёрские и демо-порталы). Это грамматика B, где в роли продукта выступает бренд.
- Одно публичное «красивое» имя для управляющей плоскости, которая должна быть доступна до поднятия mesh-сети (например, координатор mesh), допускается как зафиксированное и задокументированное исключение — но не как шаблон.

### 3.3 Грамматики C не существует

| Распространённый антипаттерн | Почему это не имя | Целевое состояние |
|---|---|---|
| `*.admin.corp.lan`, `*.private.corp.lan` | уровень доступности (exposure) в имени | то же FQDN, другая группа mesh/IdP |
| `*.mesh`, `*.apps.mesh` | псевдо-TLD внутри mesh; не разрешается за пределами DNS mesh-сети | грамматика A |
| `vcenter.corp.lan` (продукт, а не возможность) | нарушает правило «слева — возможность» | `compute.infra.shared.svc.mess.systems` |
| имена папок репозитория (`infra/llm-proxy`) | папка репозитория — не ось именования | `gateway.ai.corp` |

## 4. Коды

### 4.1 Плоскости

| Код | Потребитель | Доверие |
|---|---|---|
| `shared` | управляющие плоскости, от которых зависят все (IAM, PKI, секреты, DNS, mesh, наблюдаемость, гипервизор) | наивысшее |
| `corp` | сотрудники | внутреннее |
| `eng` | инженеры, создающие продукты | внутреннее |
| `platform` | среда выполнения, общая для продуктов | продуктовое |
| `<product>` | собственная среда выполнения одного продукта | продуктовое |
| `ext` | партнёры, демо, публичные порталы | внешнее |

### 4.2 Домены

| Код | Домен | Плоскость по умолчанию |
|---|---|---|
| `iam` | идентичность, доступ, PKI, секреты, пароли | shared |
| `gov` | архитектура, политики, CMDB, ADR | corp |
| `sec` | обнаружение угроз, управление уязвимостями, SIEM | shared |
| `obs` | метрики, логи, трассировки, оповещения (см. открытые вопросы в README) | shared |
| `net` | DNS, mesh, edge, межсетевой экран | shared |
| `infra` | вычисления, хранение, резервное копирование, гипервизор | shared |
| `sdlc` | код, CI, артефакты, GitOps | eng |
| `adlc` | жизненный цикл ИИ и агентов, оценки (evals), sidecar-политики | eng |
| `ai` | инференс, шлюз, речь, зрение, агенты | corp |
| `data` | хранилище данных, конвейеры, каталог, BI, документное хранилище | platform |
| `collab` | чат, вики, документы, видео | corp |
| `comm` | почта, уведомления | corp |
| `biz` | ERP/CRM/финансы | corp |
| `itsm` | служба поддержки, управление изменениями | corp |
| `api` | управление API для продуктов | platform |
| `edge` | входящий трафик (ingress) для продуктов | platform |

### 4.3 Коды возможностей (уникальны во всех доменах)

Код имеет **одно значение** во всей компании. Один и тот же код может встречаться в нескольких плоскостях (`egress.net.corp`, `egress.net.platform`), поскольку плоскость — это другая ось; но он не может встречаться в двух доменах.

| Домен | Коды |
|---|---|
| `iam` | `sso directory pki spiffe secrets passwords b2b` |
| `gov` | `cmdb archrepo adr policy catalog demo audit` |
| `sec` | `siem vuln ids scan` |
| `obs` | `dashboards metrics logs traces alerts` |
| `net` | `dns mesh ingress egress firewall` |
| `infra` | `compute storage backup k8s` |
| `sdlc` | `git ci oci packages gitops flags hub-cache` |
| `adlc` | `registry sandbox evals` |
| `ai` | `gateway inference stt tts ocr llm-traces kb docs guard` |
| `data` | `warehouse orchestrate transform ingest data-catalog bi docstore convert sql cache objects` |
| `collab` | `chat wiki intranet video` |
| `comm` | `mail notify` |
| `biz` | `crm billing` |
| `itsm` | `service-desk change` |
| `api` | `gateway-api portal-api` |
| `edge` | `lb` |

Эта таблица — пример эталонного набора, а не инвентарь; расширяйте или сокращайте её под свою организацию по правилу ниже.

Добавление кода: проверьте уникальность по всей таблице, многословные коды пишите через дефис, сначала зарегистрируйте возможность в каталоге возможностей, затем здесь.

### 4.4 Окружения и площадки

| Окружение | Код | Площадка | Код |
|---|---|---|---|
| продуктивное | `prd` | собственный (on-premises) ЦОД | `dc1` |
| предпродуктивное (staging) | `stg` | тенант в публичном облаке | `cld` |
| тестовое | `tst` | | |
| разработка | `dev` | | |

Коды площадок короткие, специфичны для организации и перечислены в каталоге; два приведённых выше — примеры.

## 5. Формы объектов

| Семейство | Форма | Пример |
|---|---|---|
| Внутреннее FQDN | §3.1 | `git.sdlc.eng.svc.mess.systems` |
| Публичное FQDN | §3.2 | `app.shopfront.example` |
| Приложение (каталог, `service.name`, slug OIDC, AppRole) | `<plane>-<domain>-<product>` | `eng-sdlc-gitea` |
| Хост / контейнер / ВМ | `<site>-<plane>-<domain>-<product>-<env>-<NN>` | `dc1-eng-sdlc-gitea-prd-01` |
| Узел гипервизора | `<site>-shared-infra-<hypervisor>-<env>-<NN>` | `dc1-shared-infra-kvm-prd-01` |
| Git-организация / репозиторий | организация `<plane>` · репозиторий `<domain>-<product>` | `eng/sdlc-gitea` |
| Образ контейнера | `oci.sdlc.eng.svc.mess.systems/<plane>-<domain>/<product>[-<component>]:<tag>` | `oci.sdlc.eng.svc.mess.systems/corp-ai/litellm:1.4.0` |
| Проект реестра (например, Harbor) | `<plane>-<domain>` | `corp-ai` |
| Фид пакетов | `<ecosystem>-<plane>` или `<ecosystem>-proxy` | `npm-proxy`, `pypi-eng` |
| S3 / бакет объектного хранилища | `<plane>-<domain>-<capability>-<env>` | `platform-data-warehouse-prd` |
| База данных Postgres | `<plane>_<domain>_<capability>_<env>` | `eng_sdlc_git_prd` |
| Схема Postgres / ClickHouse | как у базы данных | `platform_data_warehouse_prd` |
| Набор данных / витрина dbt | `<plane>.<domain>.<table>` | `platform.data.catalog_coverage` |
| Пространство имён Kubernetes | `<product>[-<env>]`; платформенные сервисы используют возможность | `shopfront-stg`, `gitops` |
| Рабочая нагрузка Kubernetes | `<product>-<context>-<role>` | `shopfront-api-web` |
| Метка Kubernetes | `mess.systems/<key>=<value>` | `mess.systems/plane=platform` |
| ID провайдера в каталоге | `<vendor>.<service>` | `acmecloud.foundation-models` |
| Префикс маршрута LLM (шлюз) | `<provider-short>/<model>`; `local/` = корпоративный инференс | `acmecloud/large-chat` |
| Цель MCP (шлюз) | код возможности; провайдеры `<vendor>-<service>` | `convert`, `acmesearch-web` |
| OTel `service.name`, Prometheus `job`, Loki `service_name` | форма приложения | `corp-ai-litellm` |
| Папка дашбордов (например, Grafana) / uid дашборда | папка `<plane>-<domain>` · uid `<application>-<view>` | `corp-ai` / `corp-ai-litellm-overview` |
| Правило оповещения | `<Domain><Capability><Symptom>` | `AiGatewayHighErrorRate` |
| Группа инвентаря Ansible | `<plane>_<domain>` и `<application>` | `corp_ai`, `corp_ai_litellm` |
| Имя ресурса OpenTofu | `<application>_<env>` | `corp_ai_litellm_prd` |
| Сертификат (внутренний) | `*.<domain>.<plane>.svc.mess.systems` на каждую пару «домен-плоскость» | `*.ai.corp.svc.mess.systems` |
| Системный отправитель почты | `<capability>@mess.systems` | `alerts@mess.systems` |

## 6. Единый базовый URL

У одной установки один базовый URL: `https://<fqdn>`. Мультиарендность на основе путей (`/admin`, `/ui`) — дело продукта; в FQDN она не отражается. Редиректы со старых имён допускаются на 90 дней и вносятся в таблицу миграции, после чего удаляются.

## 7. TLS

- Внутренний: ACME через `pki.iam.shared`. По умолчанию сертификат выпускается на каждое имя (например, ingress-прокси с TLS по требованию). Заранее выпущенные wildcard-сертификаты — только для конечных точек, которые не умеют ACME: по одному на пару `<domain>.<plane>`, с учётом в реестре сертификатов развёртывания (пример см. в [02](02-worked-example.md) §6).
- Публичный: публичный УЦ через DNS-01 на домене продукта. Один wildcard на домен продукта.
- Имена в SAN — всегда каноническое FQDN плюс перечисленные редиректы, но никогда не унаследованные имена.

## 8. Провайдеры и исходящий трафик

- Внешние вендоры — это ID каталога (`<vendor>.<service>`), а не внутренние FQDN.
- Исходящий трафик к вендору идёт через возможность-владельца (`gateway.ai.corp` для LLM-провайдеров, группы egress `mesh.net.shared` для сети).
- Секреты провайдеров хранятся по пути **потребляющей** возможности ([03](03-secrets-conventions.md) §4).

## 9. Процедура

**Шаг A — сбор исходных данных (intake), оси по порядку:** плоскость → домен → возможность → продукт → окружение → владелец/уровень/scope/data_class/exposure.
**Шаг B — кодирование:** FQDN (§3), приложение (§5), хост (§5), затем формы конкретных семейств. Регистрация в каталоге — до DNS.
**Шаг C — идентичности и секреты:** создать группы/машинную роль ([04](04-identity-conventions.md)), создать путь ([03](03-secrets-conventions.md)).
**Шаг D — наблюдаемость:** `service.name` = приложение; папка дашбордов = `<plane>-<domain>`.

## 10. Отказы (отклоните имя, если…)

| Признак | Нарушенное правило |
|---|---|
| продукт в самой левой метке | §3.1 |
| уровень доступности или уровень привилегий в имени (`admin.`, `public.`, `t0-`) | §3.1, §2 |
| окружение в prod-имени DNS | §3.1 |
| нет окружения в хосте, схеме, бакете или пути секрета | §5, [03](03-secrets-conventions.md) |
| вендор как внутреннее FQDN | §8 |
| две возможности на одном FQDN через пути | §6 |
| папка репозитория в роли имени | §3.3 |
| `_` в DNS или k8s | §1 |
| код возможности повторно используется со вторым значением | §4.3 |
| новая грамматика для «особого» случая | §3.3 |

## 11. Разобранные примеры кодирования

| Исходные данные (intake) | FQDN | Приложение | Хост |
|---|---|---|---|
| shared / iam / sso / Keycloak / prd | `sso.iam.shared.svc.mess.systems` | `shared-iam-keycloak` | `dc1-shared-iam-keycloak-prd-01` |
| eng / sdlc / git / Gitea / prd | `git.sdlc.eng.svc.mess.systems` | `eng-sdlc-gitea` | `dc1-eng-sdlc-gitea-prd-01` |
| corp / ai / gateway / LiteLLM / prd | `gateway.ai.corp.svc.mess.systems` | `corp-ai-litellm` | `dc1-corp-ai-litellm-prd-01` |
| corp / ai / gateway / LiteLLM / stg | `gateway.ai.corp.stg.svc.mess.systems` | `corp-ai-litellm` | `dc1-corp-ai-litellm-stg-01` |
| platform / data / docstore / MongoDB / prd | `docstore.data.platform.svc.mess.systems` | `platform-data-mongodb` | `dc1-platform-data-mongodb-prd-01..03` |
| shared / net / mesh / Headscale / prd (cloud site) | `mesh.net.shared.svc.mess.systems` | `shared-net-headscale` | `cld-shared-net-headscale-prd-01` |
| ext / demo portal | `demo.apps.mess.systems` | `ext-gov-demo-portal` | `cld-ext-gov-portal-prd-01` |
| shopfront (product) / app | `app.shopfront.example` | `shopfront-api` | `cld-shopfront-api-prd-01` |
