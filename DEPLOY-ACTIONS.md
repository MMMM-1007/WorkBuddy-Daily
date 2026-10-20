# ☁️ 把 WorkBuddy-Daily 部署到 GitHub Actions

**这个文件夹在哪**：`D:\DeepseekWork\workbuddy-actions\`
（打开方法：按 `Win + R`，粘贴这个路径，回车）

文件夹里你需要的东西只有三个：

| 文件 | 干什么用 |
| :--- | :--- |
| `1-先拿凭据.bat` | 双击 → 短信登录，拿 WorkBuddy 凭据（RT） |
| `2-一键部署.bat` | 双击 → 按提示粘贴两串东西 → 自动建仓、上传、开 Actions |
| `DEPLOY-ACTIONS.md` | 就是本文（说明书 / 排错表） |

其余 `.py` / `.yml` 是真正跑签到的代码和工作流，**不用你手动动它们**。

---

## 0. 两个词到底指什么

| 词 | 是什么 | 从哪来 | 长什么样 |
| :--- | :--- | :--- | :--- |
| **PAT** | *Personal Access Token*，GitHub 的**授权码**。有了它，程序才能代表**你**在你自己的账号下建仓库、传文件、写配置。它跟你 GitHub 账号密码是两回事，可以单独撤销、单独设有效期 | 你自己在 GitHub 网页上点出来（下面 6 步） | `ghp_` 开头一长串，只显示一次 |
| **RT** | *Refresh Token*，你 **WorkBuddy 账号的登录续期令牌**。签到脚本就是用它在云端登录你的账号干活，并且每轮自动换新，所以能长期不用你管 | 用 `1-先拿凭据.bat` 走短信验证码登录，脚本打印出 `手机号:AT:RT` | 一行 `13800000000:eyJhbGci...:eyJhbGci...` |

一句话：**PAT 是「让程序能操作你的 GitHub」，RT 是「让程序能登录你的 WorkBuddy」。** 两个都不是我能替你生成的。

### PAT 在哪点出来（6 步，约 1 分钟）

1. 浏览器登录 <https://github.com>，点右上角头像 → **Settings**
2. 左侧菜单拉到最底 → **Developer settings**
3. **Personal access tokens** → **Tokens (classic)**
4. 右上 **Generate new token** → **Generate new token (classic)**
5. *Note* 随便写（如 `workbuddy`）；*Expiration* 选 90 days；下面权限**只勾两个**：
   - ☑ **`repo`**（整块，含子项）
   - ☑ **`workflow`**
6. 拉到底 **Generate token** → 复制页面上那串 `ghp_...`（**关掉页面就再也看不到**）

> 页面上勾选界面是英文的，`repo` / `workflow` 就是这两个单词，别勾别的。

---

## 1. 最短路径：双击两次

1. 双击 **`1-先拿凭据.bat`** → 输入手机号 → 收到短信填验证码 → 记下打印的 `手机号:AT:RT`
2. 双击 **`2-一键部署.bat`** → 粘贴 PAT 回车 → 粘贴刚才那行 RT 回车 → 等它跑完
3. 看到 `✅ 部署完成` 就好了：仓库已在你账号下建好（默认私有），定时已开

跑完去 <https://github.com> 看新仓库的 **Actions** 标签页，能看到一次运行记录，绿色 ✅ 即成功。
之后每天北京时间 **07:00 / 12:00 / 23:30** 自动跑，你不用管。

> 没有 RT 也能先建仓（部署向导会提示跳过），之后到仓库
> Settings → Secrets and variables → Actions 里补 `WORKBUDDY_REFRESH_TOKEN` 即可。

---

## 2. 命令行路线（等价，想手动控制时用）

本目录 = 一个**可直接上传的独立仓库**：脚本 + 加固版工作流 + 部署器都在里面。

| 路线 | 需要什么 | 耗时 | 适合 |
| :--- | :--- | :---: | :--- |
| **A 一键脚本** | 一个 GitHub PAT | 2 分钟 | 想全自动，本机没装 git 也行 |
| **B 网页三步** | 只需要浏览器 | 5 分钟 | 不想把 PAT 交给任何程序 |

两条路产出的仓库完全一样。

---

## 3. 先拿到 `手机号:AT:RT`（等价于双击 `1-先拿凭据.bat`）

这是唯一无法代劳的一步（要收短信验证码）。一条命令搞定（自动选解释器、自动补依赖）：

```powershell
cd D:\DeepseekWork\workbuddy-actions
.\deploy\login.ps1 -Phone 13800000000
# 已经是交互式输入手机号的话，直接 .\deploy\login.ps1
```

跑完会打印一行 `13800000000:eyJ...:eyJ...`（同时存到 `wb_login_result.json`，已被 `.gitignore` 屏蔽）。
多账号就多跑几次，凑成多行。

> 格式铁律：`手机号:AT:RT`，冒号分隔，**顺序不能反**（AT 的 `typ=Bearer`，RT 的 `typ=Offline`）。
> 反了会得到 `12153 token format error`。

---

## 4. 命令行一键部署

```powershell
cd D:\DeepseekWork\workbuddy-actions

# 先看计划，不落地
.\deploy\deploy.ps1 --token ghp_你的PAT --rt "13800000000:eyJ...:eyJ..." --dry-run

# 真部署（默认私有仓库，令牌自动永续）
.\deploy\deploy.ps1 --token ghp_你的PAT --rt "13800000000:eyJ...:eyJ..." --secret PUSHPLUS_TOKEN=xxxx
```

脚本做的事：建私有仓库 → 上传 14 个文件 → 写入 Secrets → 开启 Actions → 触发首跑 → 盯到出结论。

**PAT 权限**

- Classic：勾 `repo` + `workflow`
- Fine-grained：`Administration`(write) + `Contents`(write) + `Secrets`(write) + `Workflows`(write) + `Actions`(write)

少 `workflow` 权限的典型症状：上传 `.github/workflows/workbuddy.yml` 报 404/422。

**常用参数**

| 参数 | 说明 |
| :--- | :--- |
| `--repo NAME` | 仓库名，默认 `WorkBuddy-Daily` |
| `--public` | 建公开仓库（默认私有） |
| `--update` | 已有仓库时原地更新，可反复执行 |
| `--secret K=V` | 追加 Secret，可重复 |
| `--rt-file rt.txt` | 从文件读 RT（多账号换行） |
| `--no-watch` | 触发后不等结果 |
| `--no-dispatch` | 只部署不跑 |

**以后更新脚本**（幂等，不重建仓库）：

```powershell
.\deploy\deploy.ps1 --token ghp_xxx --rt-file rt.txt --update --no-watch
```

---

## 5. 网页三步（完全不碰 PAT）

### 第 1 步：建仓库 + 传文件

用 GitHub 的 Import 功能（会连提交历史一起搬过来）：

1. 打开 <https://github.com/new/import>
2. *Your old repository's clone URL* 填 `https://github.com/L0NE-6/WorkBuddy-Daily`
3. 仓库名自取，可见性选 **Private**
4. **Begin import**，等它跑完

> ⚠️ 别用 Fork。GitHub 不允许改 Fork 的可见性（*you cannot change the visibility of a fork*），
> Fork 出来的仓库只能是公开的，令牌状态就没法落库。

想把本目录的手工改动也带上，就在导入完成后，把 `.github/workflows/workbuddy.yml` 用本目录同名文件覆盖一遍（网页版直接编辑提交即可）。

### 第 2 步：加 Secrets

仓库 → **Settings → Secrets and variables → Actions → New repository secret**

| Name | 必填 | 值 |
| :--- | :---: | :--- |
| `WORKBUDDY_REFRESH_TOKEN` | ✅ | 第 0 步那几行 `手机号:AT:RT`，多账号换行 |
| `PUSHPLUS_TOKEN` | ⬜ | PushPlus 令牌 |
| `BARK_URL` | ⬜ | `https://api.day.app/xxxx` |
| `WXPUSHER_APP_TOKEN` / `WXPUSHER_UID` | ⬜ | WxPusher 应用令牌 / 用户 UID |
| `WECOM_WEBHOOK` | ⬜ | 企业微信群机器人 webhook |
| `DINGTALK_WEBHOOK` / `DINGTALK_SECRET` | ⬜ | 钉钉机器人（加签时填 secret） |
| `WORKBUDDY_TASKS` | ⬜ | 白名单，如 `checkin,travel,chat_5` |
| `WORKBUDDY_SKIP_TASKS` | ⬜ | 黑名单，如 `lottery,redeem` |
| `WORKBUDDY_MP_GAP` | ⬜ | mp 对话间隔秒，默认 45 |
| `GH_PAT` | ⬜ | 仅公开仓库需要：跑完自动把新 RT 写回 Secret |

### 第 3 步：开 Actions + 跑一次

1. 仓库 **Actions** 标签页 → 若提示，点 *I understand my workflows, go ahead and enable them*
2. 左侧 **🌱 WorkBuddy Daily** → **Run workflow** → 分支 `main` → 运行
3. 看到绿色 ✅ 就部署完成；日志里「运行摘要」有本次结论

---

## 内置定时（北京时间）

| 北京时间 | UTC cron | 用途 |
| :---: | :---: | :--- |
| 07:00 | `0 23 * * *` | 日常全流程 |
| 12:00 | `0 4 * * *` | 日常全流程 |
| 23:30 | `30 15 * * *` | 夜猫子活动窗口 |

改时间就改 `.github/workflows/workbuddy.yml` 里的 cron，记住 **UTC = 北京时间 − 8 小时**。
工作流已设 `TZ: Asia/Shanghai`，否则 runner 默认 UTC，日志时间会偏 8 小时、补签日期会算错一天。

---

## 令牌怎么做到「永续」

脚本每次续期都会轮换 RT 并写进 `wb_refresh_tokens.json`。这个文件必须能被下一轮读回来，否则第二轮就失效。本工作流给了两条兜底：

- **私有仓库（默认）**：跑完把 `wb_refresh_tokens.json` 提交回仓库 → 下一轮 checkout 自带最新 RT。
- **公开仓库 + `GH_PAT`**：跑完用 `gh secret set` 把最新 RT 写回 `WORKBUDDY_REFRESH_TOKEN`（明文不落盘、不进日志），顺手留一次心跳提交防止定时被禁。

两者都没有（公开仓库又没给 `GH_PAT`）时：每轮只能靠 Secret 里那个 RT 起步，**RT 大约 30 天滚动失效，需要每月手动更新一次**。

---

## 常见坑对照表

| 现象 | 原因 | 处理 |
| :--- | :--- | :--- |
| 首跑就红，`::error::没有可用账号` | Secret 没设或名字拼错 | 补 `WORKBUDDY_REFRESH_TOKEN`，注意是全大写 |
| `12153 token format error` | AT/RT 写反、带引号空格、粘的是别的应用的 token | 用 `workbuddy_login.py` 重新拿一行 |
| `凭据体检` 提示签发域不是 CN 站 | 粘了国际版 token | CN 站用 `workbuddy_login.py`，国际版用 `workbuddy_intl_login.py` |
| 上传工作流文件 404/422 | PAT 缺 `workflow` 权限 | 重发 token，勾上 workflow |
| 定时不跑 | 公开仓库 60 天无提交被自动禁用 | 手动 Run 一次，或用 `GH_PAT` 的心跳提交 |
| `git push` 失败 | 分支保护 / 只读 | 关闭分支保护，或改用 `GH_PAT` 模式 |
| 任务跑到一半超时 | 账号多 + mp 任务按真人节奏上报 | 调大 `timeout-minutes`，或 `WORKBUDDY_SKIP_TASKS` 砍掉重的 |
| 签到成功但热力墙没点亮 | 过滤任务后没有「使用类」任务 | `WORKBUDDY_TASKS=checkin,travel,chat_5` 保留一个对话任务 |

---

## 自检（不联网、不碰账号）

```powershell
cd D:\DeepseekWork\workbuddy-actions
.\deploy\deploy.ps1 --token fake --dry-run      # 只打印计划，不联网
& "$env:LOCALAPPDATA\.dsh\dsh-runtimes\dsh-primary-runtime\dependencies\python\python.exe" .\deploy\selfcheck.py
```

`selfcheck.py` 校验：工作流 YAML 结构 / cron 合法性 / Secrets 引用一致性 / 全部脚本可编译 /
preflight 与 export_rt 的行为 / dry-run 不泄露明文。

---

## 安全清单

- `wb_refresh_tokens.json`、`wb_login_result.json`、`WORKBUDDY_ACCESS_TOKEN.txt` 一律别提交（`.gitignore` 已屏蔽）。
- 私有仓库 + `GITHUB_TOKEN`（工作流内置）足以完成持久化，**不需要**把 PAT 写进 Secret；只有公开仓库做 Secret 轮换时才需要 `GH_PAT`。
- `GH_PAT` 建议 fine-grained 且只勾这一个仓库的 Secrets 权限，用完可随时吊销。
- 日志里 RT 全程脱敏（见 `.github/scripts/preflight.py`）。
