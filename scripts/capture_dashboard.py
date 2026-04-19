#!/usr/bin/env python3
"""Capture dashboard screenshots for manuscript Figure 5.

Uses Playwright to screenshot the deployed dashboard at
https://olatechie.github.io/dropout/. Saves two panels side-by-side
(story hero + policy dashboard) to manuscript/figures/fig5_dashboard.png.

Requires: playwright installed + `playwright install chromium` run once.
"""
from __future__ import annotations

import argparse
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "manuscript" / "figures"
URL = "https://olatechie.github.io/dropout/"


def _screenshot(path: str, out_file: Path) -> None:
    from playwright.sync_api import sync_playwright
    with sync_playwright() as pw:
        browser = pw.chromium.launch()
        ctx = browser.new_context(viewport={"width": 1440, "height": 900})
        page = ctx.new_page()
        page.goto(f"{URL}{path}", wait_until="networkidle", timeout=60_000)
        page.wait_for_timeout(3_000)  # allow animations
        page.screenshot(path=str(out_file), full_page=False)
        browser.close()


def build_fig5(offline_fallback: Path | None = None) -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    story_path = OUT / "fig5_story.png"
    policy_path = OUT / "fig5_policy.png"
    try:
        _screenshot("#/story", story_path)
        _screenshot("#/policy", policy_path)
    except Exception as exc:
        print(f"Playwright failed ({exc}); using offline fallback if provided.")
        if offline_fallback and offline_fallback.exists():
            story_path = offline_fallback
            policy_path = offline_fallback
        else:
            raise

    story = Image.open(story_path)
    policy = Image.open(policy_path)
    h = min(story.height, policy.height)

    def _fit(img, h):
        w = int(img.width * h / img.height)
        return img.resize((w, h))

    story_r, policy_r = _fit(story, h), _fit(policy, h)
    combined = Image.new("RGB", (story_r.width + policy_r.width + 20, h), "white")
    combined.paste(story_r, (0, 0))
    combined.paste(policy_r, (story_r.width + 20, 0))
    combined.save(OUT / "fig5_dashboard.png", dpi=(300, 300))
    print(f"  → manuscript/figures/fig5_dashboard.png")


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--fallback", type=Path, default=None,
                   help="Offline PNG to use if Playwright fails")
    args = p.parse_args()
    build_fig5(args.fallback)


if __name__ == "__main__":
    main()
