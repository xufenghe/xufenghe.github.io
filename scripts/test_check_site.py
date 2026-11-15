import unittest

from check_site import SiteParser


class SiteParserTests(unittest.TestCase):
    def test_collects_relative_and_root_relative_files(self) -> None:
        parser = SiteParser()
        parser.feed(
            '<link href="./styles.css?v=2">'
            '<img src="/assets/../seal.svg" alt="">'
            '<a href="notes%20and%20figures.pdf#page=2"></a>'
        )
        self.assertEqual(parser.local_paths, {"styles.css", "seal.svg", "notes and figures.pdf"})

    def test_ignores_nonlocal_and_same_page_references(self) -> None:
        parser = SiteParser()
        parser.feed(
            '<a href="https://example.com/file"></a>'
            '<img src="//example.com/logo.svg" alt="">'
            '<a href="mailto:hello@example.com"></a>'
            '<a href="#about"></a><a href="?view=full"></a><a href="/"></a>'
        )
        self.assertEqual(parser.local_paths, set())
