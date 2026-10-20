#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""把 wb_refresh_tokens.json 还原成 WORKBUDDY_REFRESH_TOKEN 的变量格式。

输出格式（每行一个账号）：手机号:AT:RT
    · AT 为空时写 手机号::RT（脚本支持这种形态）
    · 只输出带 refresh_token 的账号，保证续期链不断
    · 不打印任何密钥到日志，由调用方直接管道给 `gh secret set`
"""
import json
import os
import sys

STORE = os.environ.get("WB_TOKEN_STORE") or os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
    "wb_refresh_tokens.json",
)


def main() -> int:
    if not os.path.exists(STORE):
        print("", end="")
        return 0
    try:
        store = json.load(open(STORE, encoding="utf-8"))
    except Exception as exc:                       # 文件坏了就当没有
        sys.stderr.write("读取令牌库失败: %s\n" % exc)
        print("", end="")
        return 0

    lines = []
    for user, ent in store.items():
        if not isinstance(ent, dict):
            continue
        rt = str(ent.get("refresh_token") or "").strip()
        at = str(ent.get("access_token") or "").strip()
        if not rt:
            continue
        user = str(user).strip()
        lines.append("%s:%s:%s" % (user, at, rt))

    out = "\n".join(lines)
    sys.stderr.write("导出 %d 个账号的凭据\n" % len(lines))
    print(out, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
