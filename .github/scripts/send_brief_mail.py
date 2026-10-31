#!/usr/bin/env python3
"""
데일리 브리프를 메일로 보낸다 (GitHub Actions에서 실행).

본문: 최신 reports/univ_bids_*.md 를 HTML로 변환
첨부: 같은 날짜의 .csv

환경변수 (모두 저장소 Secret으로 등록)
  MAIL_USERNAME  보내는 계정 (네이버면 아이디 또는 아이디@naver.com)
  MAIL_PASSWORD  메일 비밀번호 또는 앱 비밀번호
  MAIL_TO        받는 주소, 여러 명이면 쉼표로 구분 (없으면 보내는 계정으로)
  SMTP_HOST      기본 smtp.naver.com (Gmail이면 smtp.gmail.com)
  SMTP_PORT      기본 465 (SSL)

사용: python send_brief_mail.py reports [--dry-run out.eml]
"""
from __future__ import annotations

import os
import re
import smtplib
import ssl
import sys
from email.message import EmailMessage
from pathlib import Path

try:
    import markdown  # pip install markdown
except ImportError:  # 없으면 <pre>로 보냄
    markdown = None

STYLE = """
<style>
 body{font-family:-apple-system,'Apple SD Gothic Neo','Malgun Gothic',sans-serif;
      font-size:14px;color:#1f2328;line-height:1.55;max-width:960px}
 h1{font-size:20px;margin:0 0 8px} h2{font-size:16px;margin:24px 0 8px;
      border-bottom:1px solid #d0d7de;padding-bottom:4px}
 table{border-collapse:collapse;width:100%;margin:8px 0}
 th,td{border:1px solid #d0d7de;padding:5px 8px;vertical-align:top;font-size:13px}
 th{background:#f6f8fa;text-align:left} td:nth-child(3),td:nth-child(4){white-space:nowrap}
 a{color:#0969da;text-decoration:none}
</style>"""


def latest(folder: Path) -> tuple[Path, Path | None]:
    mds = sorted(folder.glob("univ_bids_*.md"))
    if not mds:
        sys.exit("브리프 파일이 없습니다.")
    md = mds[-1]
    csv = md.with_suffix(".csv")
    return md, csv if csv.exists() else None


def subject_of(md_text: str, md: Path) -> str:
    date = re.search(r"(\d{8})", md.name).group(1)
    d = f"{date[:4]}-{date[4:6]}-{date[6:]}"
    m = re.search(r"\(A (\d+) / B (\d+) / C \d+\)", md_text)
    ax = re.search(r"AX·DX 관련 공고 \((\d+)건", md_text)
    a, b = (m.group(1), m.group(2)) if m else ("?", "?")
    return f"[나라장터 대학 브리프] {d} · A {a}건 · B {b}건 · AX·DX {ax.group(1) if ax else 0}건"


def build(md: Path, csv: Path | None, sender: str, to: list[str]) -> EmailMessage:
    text = md.read_text(encoding="utf-8")
    if markdown:
        body = markdown.markdown(text, extensions=["tables"])
    else:
        body = "<pre>" + text.replace("&", "&amp;").replace("<", "&lt;") + "</pre>"
    repo = os.environ.get("GITHUB_REPOSITORY")
    footer = (f"<p style='color:#656d76;font-size:12px;margin-top:24px'>"
              f"자동 발송: GitHub Actions · <a href='https://github.com/{repo}/tree/main/reports'>"
              f"지난 브리프 보기</a></p>") if repo else ""

    msg = EmailMessage()
    msg["Subject"] = subject_of(text, md)
    msg["From"] = sender
    msg["To"] = ", ".join(to)
    msg.set_content(text)  # HTML을 못 여는 메일앱용
    msg.add_alternative(f"<html><head>{STYLE}</head><body>{body}{footer}</body></html>",
                        subtype="html")
    if csv:
        msg.add_attachment(csv.read_bytes(), maintype="text", subtype="csv",
                           filename=csv.name)
    return msg


def main() -> int:
    folder = Path(sys.argv[1] if len(sys.argv) > 1 else "reports")
    dry = sys.argv[3] if len(sys.argv) > 3 and sys.argv[2] == "--dry-run" else None

    user = os.environ.get("MAIL_USERNAME", "").strip()
    pw = os.environ.get("MAIL_PASSWORD", "").strip()
    host = os.environ.get("SMTP_HOST", "").strip() or "smtp.naver.com"
    port = int(os.environ.get("SMTP_PORT", "").strip() or 465)
    sender = user if "@" in user else (f"{user}@naver.com" if user else "brief@example.com")
    to = [t.strip() for t in (os.environ.get("MAIL_TO") or sender).split(",") if t.strip()]

    md, csv = latest(folder)
    msg = build(md, csv, sender, to)

    if dry:
        Path(dry).write_bytes(bytes(msg))
        print(f"dry-run: {dry} ({msg['Subject']})")
        return 0
    if not user or not pw:
        print("::warning::MAIL_USERNAME / MAIL_PASSWORD Secret이 없어 메일 발송을 건너뜁니다.")
        return 0

    ctx = ssl.create_default_context()
    if port == 465:
        with smtplib.SMTP_SSL(host, port, context=ctx, timeout=30) as s:
            s.login(user, pw)
            s.send_message(msg)
    else:
        with smtplib.SMTP(host, port, timeout=30) as s:
            s.starttls(context=ctx)
            s.login(user, pw)
            s.send_message(msg)
    print(f"메일 발송 완료 → {len(to)}명 ({msg['Subject']})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
