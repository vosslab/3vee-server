#!/usr/bin/env python3
"""Download the UCSF Chimera installer by accepting the license form headlessly."""

import argparse
import os
import sys
import urllib.parse
import urllib.request
import urllib.error
import http.cookiejar
import re
import html
import hashlib
import shutil
from pathlib import Path
from http.client import HTTPMessage


CHIMERA_FORM_URL = "https://www.cgl.ucsf.edu/chimera/cgi-bin/secure/chimera-get.py"
DEFAULT_USER_AGENT = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:109.0) Gecko/20100101 Firefox/117.0"
)


def build_opener(user_agent):
    cookies = http.cookiejar.CookieJar()
    opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cookies))
    opener.addheaders = [
        ("User-Agent", user_agent),
        ("Accept", "*/*"),
    ]
    opener.cookie_jar = cookies  # type: ignore[attr-defined]
    return opener


def log_cookies(opener):
    jar = getattr(opener, "cookie_jar", None)
    if not jar:
        return
    entries = [f"{cookie.name}={cookie.value}" for cookie in jar]
    print(
        "[download_chimera] cookies "
        + (", ".join(entries) if entries else "(empty jar)")
    )


def summarize_headers(headers: HTTPMessage):
    tracked = {
        key: headers.get_all(key)
        for key in [
            "Content-Type",
            "Location",
            "Refresh",
            "Set-Cookie",
            "Content-Location",
        ]
        if headers.get_all(key)
    }
    if not tracked:
        return "(no tracked headers)"
    parts = []
    for key, values in tracked.items():
        joined = " | ".join(values)
        parts.append(f"{key}={joined}")
    return "; ".join(parts)


def http_request(opener, url, data=None):
    method = "POST" if data is not None else "GET"
    print(f"[download_chimera] {method} {url}")
    if data is not None and not isinstance(data, bytes):
        data = urllib.parse.urlencode(data).encode("utf-8")
    try:
        with opener.open(url, data=data) as response:
            payload = response.read()
            status = getattr(response, "status", "?")
            reason = getattr(response, "reason", "")
            print(
                f"[download_chimera] status={status} reason={reason} bytes={len(payload)}"
            )
            if isinstance(response.headers, HTTPMessage):
                print(
                    "[download_chimera] headers "
                    + summarize_headers(response.headers)
                )
            log_cookies(opener)
            return payload
    except urllib.error.HTTPError as exc:
        body = exc.read() if exc.fp else b""
        snippet = body[:200].decode("utf-8", errors="ignore")
        headers = (
            summarize_headers(exc.headers)
            if isinstance(exc.headers, HTTPMessage)
            else "(no headers)"
        )
        log_cookies(opener)
        raise RuntimeError(
            f"{method} {url} failed with HTTP {exc.code}: {snippet or exc.reason}\n"
            f"[download_chimera] error headers {headers}"
        ) from exc


def extract_redirect(html_text):
    pattern = re.compile(r'(?:url|href)=\s*["\']?([^"\'\s>]+)', re.IGNORECASE)
    matches = pattern.findall(html_text)
    if not matches:
        raise RuntimeError("Failed to locate Chimera redirect target")
    for candidate in matches:
        target = html.unescape(candidate)
        if "chimera-get.py" in target:
            print(f"[download_chimera] redirect candidate {target}")
            return target
    chosen = html.unescape(matches[0])
    print(
        "[download_chimera] falling back to first redirect candidate "
        + chosen
    )
    return chosen


def resolve_cache_path(cache_dir, file_param):
    cache_root = Path(cache_dir).expanduser()
    cache_root.mkdir(parents=True, exist_ok=True)
    basename = os.path.basename(file_param) or "chimera-installer.bin"
    digest = hashlib.sha256(file_param.encode("utf-8")).hexdigest()[:12]
    filename = f"{basename}.{digest}"
    return cache_root / filename


def copy_file(src, dest):
    shutil.copyfile(src, dest)


def download_installer(file_param, output_path, user_agent, cache_dir):
    opener = build_opener(user_agent)
    cache_path = None
    if cache_dir:
        cache_path = resolve_cache_path(cache_dir, file_param)
        if cache_path.is_file() and cache_path.stat().st_size > 0:
            print(f"[download_chimera] using cached installer {cache_path}")
            copy_file(cache_path, output_path)
            return

    # Load license page to establish cookies/session
    http_request(opener, f"{CHIMERA_FORM_URL}?{urllib.parse.urlencode({'file': file_param})}")

    # Submit the Accept form
    redirect_html = http_request(
        opener,
        CHIMERA_FORM_URL,
        data={"file": file_param, "choice": "Accept"},
    ).decode("utf-8", errors="ignore")
    print("[download_chimera] accept form snippet:\n" + redirect_html[:500])

    redirect_target = extract_redirect(redirect_html)
    download_url = urllib.parse.urljoin(CHIMERA_FORM_URL, redirect_target)
    print(
        f"[download_chimera] redirect target={redirect_target} -> {download_url}"
    )

    binary = http_request(opener, download_url)
    with open(output_path, "wb") as outfile:
        outfile.write(binary)
    print(f"[download_chimera] wrote {len(binary)} bytes to {output_path}")

    if cache_path:
        copy_file(output_path, cache_path)
        print(f"[download_chimera] cached installer at {cache_path}")


def parse_args(argv):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--file",
        default="linux_x86_64_osmesa/chimera-1.19-linux_x86_64_osmesa.bin",
        help="Installer path parameter expected by chimera-get.py",
    )
    parser.add_argument(
        "--output",
        default="/tmp/chimera.bin",
        help="Destination path for the downloaded installer",
    )
    parser.add_argument(
        "--user-agent",
        default=DEFAULT_USER_AGENT,
        help="Override the User-Agent header sent to cgl.ucsf.edu",
    )
    parser.add_argument(
        "--cache-dir",
        default=os.environ.get("CHIMERA_CACHE_DIR"),
        help="Directory to reuse previously downloaded installers",
    )
    return parser.parse_args(argv)


def main(argv=None):
    args = parse_args(argv or sys.argv[1:])
    try:
        download_installer(args.file, args.output, args.user_agent, args.cache_dir)
    except Exception as exc:  # pylint: disable=broad-except
        print(f"Failed to download Chimera installer: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
