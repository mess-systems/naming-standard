[English](../../08-operations-objects.md) | **Русский** | [简体中文](../zh-CN/08-operations-objects.md)

> **Перевод.** Перевод стандарта версии v2.7, исходный коммит `a60b331` с редакторской правкой ссылок. Нормативным является английский текст: при любых расхождениях преимущество имеет английская версия.

# 08. Объекты эксплуатации

Формы для объектов, которые появляются при работе систем: ветки и теги, задачи CI, резервные копии, гостевые машины гипервизора, маршруты шлюзов, записи DNS и объекты PostgreSQL. Оси и символы — те же, что в [соглашениях об именовании](01-naming-conventions.md); новой грамматики нет.

## 1. Ветки и теги Git

| Объект | Форма | Пример |
|---|---|---|
| Ветка по умолчанию | `main` | `main` |
| Рабочая ветка | `<identity-id>/<topic>` | `jdoe/pg-access`, `user-jdoe-cursor/pg-access`, `agent-code-review/fix-typo` |
| Рабочая ветка для задачи | `<identity-id>/<issue>-<topic>` | `jdoe/142-pg-access` |
| Ветка сопровождения релиза | `release/v<X>.<Y>` | `release/v1.4` |
| Тег релиза | `v<X>.<Y>.<Z>`, неизменяемый, как для [образов контейнеров](07-deployment-and-tenants.md#125-образы-контейнеров-и-реестр) | `v1.4.0` |
| Тег предрелиза | `v<X>.<Y>.<Z>-rc.<n>` ([SemVer](https://semver.org/)) | `v1.4.0-rc.1` |

- `<identity-id>` — ID из [видов идентичностей](04-identity-conventions.md#2-виды-идентичностей): человек, инструмент человека или агент, поэтому ветка показывает, кто её создал.
- `<topic>` использует `a-z0-9-`, длиной не более 40 символов и никогда не содержит инструмента, хоста, клиента или секрета.
- Вид изменения (feature, fix, docs) — это метка pull request ([метки задач и PR](05-labels-and-tags.md#6-метки-задач-и-pr)), а не часть имени ветки.
- Агенты и инструменты людей не делают push в `main` или `release/*`; это правило защиты веток, а не правило именования.

## 2. CI и плановые задачи

### 2.1 Рабочие процессы и задачи

| Объект | Форма | Пример |
|---|---|---|
| Файл рабочего процесса | `<purpose>.yml` | `ci.yml`, `release.yml`, `iac-plan.yml`, `iac-apply.yml` |
| ID задачи | `<verb>[-<object>]` | `lint`, `test`, `build-image`, `plan`, `apply` |
| Окружение развёртывания | код окружения ([окружения и площадки](01-naming-conventions.md#44-окружения-и-площадки)) | `prd`, `stg` |
| Артефакт | `<application>-<version>[-<platform>]` | `eng-sdlc-forgejo-v1.4.0-linux-amd64` |

### 2.2 Раннеры

Метки раннеров следуют [меткам CI-раннеров](05-labels-and-tags.md#3-метки-ci-раннеров); раннер именуется по форме хоста или как компонент `ci-runner` ([инфраструктура как код и раннеры](07-deployment-and-tenants.md#127-инфраструктура-как-код-и-раннеры)). Новых форм нет.

### 2.3 Плановые задачи (cron, таймер systemd, CronJob)

| Объект | Форма | Пример |
|---|---|---|
| Задача | `<application>-<action>[-<schedule>]` | `shared-data-postgres-backup-daily` |
| CronJob в Kubernetes | то же без плоскости, когда её уже несёт пространство имён | `postgres-backup-daily` |
| `<schedule>` | `hourly`, `daily`, `weekly`, `monthly` или не указывается | `daily` |

## 3. Резервные копии и снимки

| Объект | Форма | Пример |
|---|---|---|
| Репозиторий резервных копий (repository, datastore, бакет) | форма бакета: `<plane>-infra-backup-<env-or-class>` | `shared-infra-backup-prd` |
| Задача резервного копирования | `<application>-<env>-<schedule>` | `shared-data-postgres-prd-daily` |
| Снимок | `<application>-<env>-<timestamp>` | `shared-data-postgres-prd-20261031t020000z` |
| `<timestamp>` | UTC, базовый формат ISO 8601, в нижнем регистре: `YYYYMMDDtHHMMSSz` | `20261031t020000z` |
| Теги снимка | `application`, `env`, `kind` (`full`, `incr`, `wal`), `retention` (`daily`, `weekly`, `monthly`) | `kind=full` |

- В имени снимка нет хоста: снимок принадлежит приложению, а не машине.
- Ключи шифрования резервных копий следуют [грамматике путей](03-secrets-conventions.md#3-грамматика-путей) соглашений о секретах: `<mount>/infra/backup/<env>/<application>`.

## 4. Гостевые машины гипервизора

| Объект | Форма | Пример |
|---|---|---|
| Имя ВМ или контейнера | имя хоста ([формы объектов](01-naming-conventions.md#5-формы-объектов)) | `dc1-shared-data-postgres-prd-01` |
| Теги гостевой машины | ключи из [меток и тегов](05-labels-and-tags.md) (`plane`, `domain`, `capability`, `env`, `owner`) | `plane=shared` |
| Пул ресурсов | `<plane>` или `<plane>-<env-class>` | `shared`, `eng-nonprod` |
| Шаблон образа | `tpl-<os>-<version>` | `tpl-debian-13` |

Числовой ID гостевой машины (ID ВМ, номер контейнера) — это инвентарь, а не имя: он никогда не используется в DNS, группах, путях секретов или документах. Если нужны диапазоны по плоскостям, они записываются в каталоге площадки, а не в стандарте.

## 5. Шлюзы API

| Объект | Форма | Пример |
|---|---|---|
| Маршрут на публичной поверхности продукта | `<product>-<service>-<version>` | `x-store-v1` |
| Маршрут к внутренней возможности | `<application>[-<purpose>]` | `corp-ai-gateway-mcp` |
| Upstream (бэкенд) | `<application>-<env>` или `<product>-<service>-<env>` | `x-store-prd` |
| Потребитель (consumer) | ID клиента из [идентичностей клиентов шлюза](04-identity-conventions.md#9-идентичности-клиентов-шлюза) | `svc-x-records-store`, `agent-code-review` |
| Слушатель (listener) | `<protocol>-<port>` | `https-443` |
| Цель MCP, префикс маршрута LLM | без изменений, см. [формы объектов](01-naming-conventions.md#5-формы-объектов) | `k8s`, `dashboards` |

## 6. Записи DNS

| Запись | Форма | Пример |
|---|---|---|
| Внутренний сервис | `A`/`AAAA` или `CNAME` на каноническое имя грамматики A | `sql.data.shared.svc.mess.systems` |
| Хост | `<host>.mgmt.mess.systems`: зона управления внутренняя, как `svc.mess.systems`, содержит только хосты, а площадка уже есть в имени хоста | `dc1-shared-data-postgres-prd-01.mgmt.mess.systems` |
| Продукт | `CNAME` поверхности на прокси или балансировщик продукта | `arch.x.mess.systems` |
| Wildcard продукта | один на домен продукта и один на каждое непроизводственное окружение: `*.<product>.x.mess.systems`, `*.<env>.<product>.x.mess.systems` | `*.arch.x.mess.systems` |
| Подтверждение владения (ACME, сервисы) | `_<purpose>.<name>` `TXT` | `_acme-challenge.arch.x.mess.systems` |
| CAA | на зоне бренда и её подзонах | `x.mess.systems CAA 0 issue "<ca>"` |

- Wildcard покрывает ровно одну метку ([RFC 4592](https://www.rfc-editor.org/rfc/rfc4592)): `*.x.mess.systems` подходит для `arch.x.mess.systems`, но не для `api.stg.arch.x.mess.systems`, которому нужен свой wildcard или запись на каждое имя.
- Каждая публичная запись вне грамматик A и B внесена в `catalog/dns-exceptions.yaml` ([грамматика B: публичная](01-naming-conventions.md#32-грамматика-b-публичная)).

## 7. Объекты PostgreSQL

| Объект | Форма | Пример |
|---|---|---|
| Кластер, корпоративный контур | приложение: `<plane>-<domain>-<product>` | `shared-data-postgres` |
| Кластер, продуктовый контур | [класс окружения](07-deployment-and-tenants.md#121-класс-окружения) | `x-records-store-nonprod` |
| База данных, схема | [формы объектов](01-naming-conventions.md#5-формы-объектов) | `eng_sdlc_git_prd` |
| Роль, временный пользователь | [роли баз данных](04-identity-conventions.md#11-роли-баз-данных), [временные пользователи баз данных](04-identity-conventions.md#111-временные-пользователи-баз-данных) | `eng_sdlc_git_ro`, `v_oidc_jdoe_eng_sdlc_git_ro_20261031t020000z_k7m2qa` |
| Слот репликации | `<consumer>_<purpose>` (snake_case) | `svc_shared_infra_backup_wal` |
| Публикация, подписка | `<database>_<purpose>` | `eng_sdlc_git_prd_cdc` |

## 8. Отказы

| Признак | Нарушенное правило |
|---|---|
| ветка без `<identity-id>/` или с именем инструмента вместо ID (`cursor/fix`) | [Ветки и теги Git](#1-ветки-и-теги-git) |
| тег релиза, переписанный после публикации | [Ветки и теги Git](#1-ветки-и-теги-git) |
| хост или IP-адрес в имени снимка, задачи или маршрута | [Резервные копии и снимки](#3-резервные-копии-и-снимки), [Шлюзы API](#5-шлюзы-api) |
| ID ВМ или номер контейнера как имя или часть имени | [Гостевые машины гипервизора](#4-гостевые-машины-гипервизора) |
| имя на две метки ниже wildcard, которое полагается на этот wildcard | [Записи DNS](#6-записи-dns) |
| публичная запись DNS вне грамматик без записи в реестре исключений | [Записи DNS](#6-записи-dns) |
