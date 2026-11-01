#!/usr/bin/env python3
"""Validate local references and basic accessibility metadata in index.html."""

from __future__ import annotations

from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlsplit


ROOT = Path(__file__).resolve().parent.parent
INDEX = ROOT / "index.html"


class SiteParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.ids: set[str] = set()
        self.duplicate_ids: set[str] = set()
        self.label_references: set[str] = set()
        self.local_paths: set[str] = set()
        self.h1_count = 0
        self.missing_image_alt = 0
        self.html_language: str | None = None

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attributes = dict(attrs)
        element_id = attributes.get("id")
        if element_id:
            if element_id in self.ids:
                self.duplicate_ids.add(element_id)
            self.ids.add(element_id)

        labelled_by = attributes.get("aria-labelledby")
        if labelled_by:
            self.label_references.update(labelled_by.split())

        if tag == "html":
            self.html_language = attributes.get("lang")
        elif tag == "h1":
            self.h1_count += 1
        elif tag == "img" and "alt" not in attributes:
            self.missing_image_alt += 1

        for name in ("href", "src"):
            value = attributes.get(name)
            if not value or not value.startswith("/") or value.startswith("//"):
                continue
            path = urlsplit(value).path.lstrip("/")
            if path:
                self.local_paths.add(path)


def main() -> int:
    parser = SiteParser()
    parser.feed(INDEX.read_text(encoding="utf-8"))

    errors: list[str] = []
    missing_paths = sorted(path for path in parser.local_paths if not (ROOT / path).is_file())
    if missing_paths:
        errors.append(f"missing local files: {', '.join(missing_paths)}")
    if parser.duplicate_ids:
        errors.append(f"duplicate ids: {', '.join(sorted(parser.duplicate_ids))}")
    missing_labels = sorted(parser.label_references - parser.ids)
    if missing_labels:
        errors.append(f"missing aria-labelledby targets: {', '.join(missing_labels)}")
    if parser.h1_count != 1:
        errors.append(f"expected one h1, found {parser.h1_count}")
    if parser.missing_image_alt:
        errors.append(f"images missing alt attributes: {parser.missing_image_alt}")
    if not parser.html_language:
        errors.append("html element is missing a lang attribute")

    if errors:
        for error in errors:
            print(f"error: {error}")
        return 1
    print(f"site check passed: {len(parser.local_paths)} local references validated")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
