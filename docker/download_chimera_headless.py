#!/usr/bin/env python3
"""Download UCSF Chimera/ChimeraX installers by accepting the license form headlessly."""

import argparse
import sys
import urllib.parse
import urllib.request
import urllib.error
import http.cookiejar
import re
import html
from pathlib import Path
from http.client import HTTPMessage


CHIMERA_FORM_URL = "https://www.cgl.ucsf.edu/chimera/cgi-bin/secure/chimera-get.py"
CHIMERAX_FORM_URL = "https://www.rbvi.ucsf.edu/chimerax/cgi-bin/secure/chimerax-get.py"
DEFAULT_CHIMERA_FILE = "linux_x86_64_osmesa/chimera-1.19-linux_x86_64_osmesa.bin"
DEFAULT_CHIMERAX_FILE = "1.11/flatpak/ChimeraX-1.11.flatpak"
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
        if "chimera-get.py" in target or "chimerax-get.py" in target:
            print(f"[download_chimera] redirect candidate {target}")
            return target
    chosen = html.unescape(matches[0])
    print(
        "[download_chimera] falling back to first redirect candidate "
        + chosen
    )
    return chosen


def download_installer(form_url, file_param, output_path, user_agent, force):
    destination = Path(output_path).expanduser()
    if destination.is_file() and destination.stat().st_size > 0 and not force:
        print(
            f"[download_chimera] existing installer found at {destination}, skipping"
        )
        return
    destination.parent.mkdir(parents=True, exist_ok=True)
    opener = build_opener(user_agent)

    # Load license page to establish cookies/session
    http_request(opener, f"{form_url}?{urllib.parse.urlencode({'file': file_param})}")

    # Submit the Accept form
    redirect_html = http_request(
        opener,
        form_url,
        data={"file": file_param, "choice": "Accept"},
    ).decode("utf-8", errors="ignore")
    print("[download_chimera] accept form snippet:\n" + redirect_html[:500])

    redirect_target = extract_redirect(redirect_html)
    download_url = urllib.parse.urljoin(form_url, redirect_target)
    print(
        f"[download_chimera] redirect target={redirect_target} -> {download_url}"
    )

    binary = http_request(opener, download_url)
    with destination.open("wb") as outfile:
        outfile.write(binary)
    print(f"[download_chimera] wrote {len(binary)} bytes to {destination}")


def parse_args(argv):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--product",
        choices=("chimera", "chimerax"),
        default="chimerax",
        help="Which UCSF download form to use",
    )
    parser.add_argument(
        "--file",
        default=None,
        help="Installer path parameter expected by the download form",
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
        "--force",
        action="store_true",
        help="Always download a fresh copy even if the output file exists",
    )
    return parser.parse_args(argv)


def main(argv=None):
    args = parse_args(argv or sys.argv[1:])
    form_url = CHIMERAX_FORM_URL if args.product == "chimerax" else CHIMERA_FORM_URL
    if args.file is None:
        file_param = DEFAULT_CHIMERAX_FILE if args.product == "chimerax" else DEFAULT_CHIMERA_FILE
    else:
        file_param = args.file
    try:
        download_installer(form_url, file_param, args.output, args.user_agent, args.force)
    except Exception as exc:  # pylint: disable=broad-except
        print(f"Failed to download Chimera installer: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
