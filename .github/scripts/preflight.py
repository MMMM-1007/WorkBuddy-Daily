#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Actions 运行前的凭据自检：不泄露明文，只打印脱敏摘要。

检查项
  1. WORKBUDDY_REFRESH_TOKEN / wb_refresh_tokens.json 是否至少有一个可用账号
  2. 每行是否 手机号:AT:RT（AT 可空）形态、RT 是否 eyJ 三段式 JWT
  3. RT 的 typ 是否 Offline、签发域是否 CN 站（写反/粘错文件会在这里暴露）
  4. AT 的 exp 是否已过期（过期不算失败，脚本会自动续期）
  5. 配了哪些推送渠道

退出码：0 = 可继续；1 = 没有任何可用账号（让工作流红在第一步，而不是跑到一半才报错）
"""
import base64
import json
import os
import sys

ENV_RT = "WORKBUDDY_REFRESH_TOKEN"
STORE = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
                     "wb_refresh_tokens.json")


def jwt_payload(tok: str) -> dict:
    try:
        seg = tok.split(".")
        if len(seg) != 3:
            return {}
        body = seg[1]
        body += "=" * (-len(body) % 4)
        data = json.loads(base64.urlsafe_b64decode(body))
        return data if isinstance(data, dict) else {}
    except Exception:
        return {}


def mask(user: str) -> str:
    user = user or "?"
    if len(user) >= 7:
        return "%s****%s" % (user[:3], user[-2:])
    return user[:1] + "***"


def collect():
    """返回 [(手机号, AT, RT, 来源)]"""
    items = []
    raw = (os.environ.get(ENV_RT) or "").strip()
    for line in raw.replace("@", "\n").splitlines():
        line = line.strip().strip('"').strip("'").strip()
        if not line or "$wbEncrypted" in line:
            continue
        parts = line.split(":", 2)
        if len(parts) == 3:
            items.append((parts[0].strip(), parts[1].strip(), parts[2].strip(), "Secret"))
        elif len(parts) == 2:
            items.append((parts[0].strip(), "", parts[1].strip(), "Secret"))
        else:
            items.append(("", "", line, "Secret"))

    if os.path.exists(STORE):
        try:
            store = json.load(open(STORE, encoding="utf-8"))
            for user, ent in store.items():
                if isinstance(ent, dict) and (ent.get("refresh_token") or ent.get("access_token")):
                    items.append((str(user), str(ent.get("access_token") or ""),
                                  str(ent.get("refresh_token") or ""), "wb_refresh_tokens.json"))
        except Exception as exc:
            print("⚠️ 读取 wb_refresh_tokens.json 失败: %s" % exc)
    return items


def main() -> int:
    print("=" * 60)
    print("🩺 凭据自检")
    items = collect()

    usable, seen = [], set()
    for user, at, rt, src in items:
        if not (at or rt):
            continue
        key = (user, rt[:24] if rt else at[:24])
        if key in seen:
            continue
        seen.add(key)

        problems = []
        for name, tok, want in (("RT", rt, "Offline"), ("AT", at, "Bearer")):
            if not tok:
                continue
            if not tok.startswith("eyJ") or tok.count(".") != 2:
                problems.append("%s 不是 eyJ 三段式 JWT（长度 %d，可能被截断/带了引号）" % (name, len(tok)))
                continue
            pay = jwt_payload(tok)
            typ = str(pay.get("typ") or "")
            iss = str(pay.get("iss") or "")
            if typ and want and typ != want:
                problems.append("%s 的 typ=%s（应为 %s）——AT/RT 可能写反了" % (name, typ, want))
            if iss and "codebuddy.cn" not in iss:
                problems.append("%s 的签发域不是 CN 站：%s" % (name, iss[:60]))
            if name == "AT":
                exp = pay.get("exp") or 0
                if exp:
                    import datetime
                    when = datetime.datetime.fromtimestamp(exp).strftime("%Y-%m-%d %H:%M")
                    print("   · AT 有效期至 %s" % when)

        ok = bool(rt or at)
        if rt:
            usable.append((user, rt))
        print("   %s %s | 来源=%s | RT=%s | AT=%s"
              % ("✅" if ok and not problems else "⚠️",
                 mask(user), src,
                 ("有(%d)" % len(rt)) if rt else "无",
                 ("有(%d)" % len(at)) if at else "无"))
        for p in problems[:4]:
            print("        · %s" % p)

    print("-" * 60)
    channels = [k for k in ("PUSHPLUS_TOKEN", "BARK_URL", "WECOM_WEBHOOK",
                            "DINGTALK_WEBHOOK", "WXPUSHER_APP_TOKEN")
                if (os.environ.get(k) or "").strip()]
    print("📢 推送渠道: %s" % (", ".join(channels) if channels else "无（仅写日志）"))
    print("🔑 可用账号数: %d（变量行数 %d）" % (len(usable), len(items)))
    print("=" * 60)

    if not usable:
        print("::error::没有可用账号：请在仓库 Settings → Secrets and variables → Actions 里设置 "
              "WORKBUDDY_REFRESH_TOKEN（每行一个 手机号:AT:RT）")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
