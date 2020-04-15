from typing import Optional
from unittest import TestCase

from .base import NavigationTestCase
from ...meta import Meta
from ...navigation import NavigationMeta
from ...options import Options
from ...utils import normpath


class TestCommonDirname(TestCase):
    def test_all_match(self):
        self.assertEqual(
            NavigationMeta._common_dirname(["a/1.md", "a/2.md"]), "a"
        )

    def test_some_match(self):
        self.assertEqual(
            NavigationMeta._common_dirname(["a/1.md", "a/2.md", "b/3.md"]), None
        )

    def test_none_match(self):
        self.assertEqual(
            NavigationMeta._common_dirname(["a/1.md", "b/2.md"]), None
        )

    def test_empty(self):
        self.assertEqual(NavigationMeta._common_dirname([]), None)

    def test_some_none_entries(self):
        self.assertEqual(
            NavigationMeta._common_dirname(["section/page.md", None]), None
        )

    def test_all_none_entries(self):
        self.assertEqual(NavigationMeta._common_dirname([None, None]), None)


class TestMeta(NavigationTestCase):
    def assertMeta(
        self,
        actual: Meta,
        expected: Optional[Meta] = None,
        *,
        path: Optional[str] = None
    ):
        if expected is None:
            expected = Meta(path=path)

        self.assertEqual(
            actual.collapse_single_pages, expected.collapse_single_pages
        )
        self.assertEqual(actual.collapse, expected.collapse)
        self.assertEqual(actual.arrange, expected.arrange)
        self.assertEqual(actual.title, expected.title)
        self.assertEqual(normpath(actual.path), normpath(expected.path))

    def assertEmptyMeta(self, meta: Meta):
        self.assertMeta(meta)

    def setUp(self):
        super(TestMeta, self).setUp()
        self.options = Options(
            filename=".pages", collapse_single_pages=False, strict=True
        )

    def test_empty(self):
        meta = NavigationMeta([], self.options)

        self.assertEqual(len(meta.sections), 0)
        self.assertEmptyMeta(meta.root)

    def test_page_in_root(self):
        meta = NavigationMeta([self.page("Page", "page.md")], self.options)

        self.assertEqual(len(meta.sections), 0)
        self.assertMeta(meta.root, path=".pages")

    def test_empty_section(self):
        section = self.section("Section", [])
        meta = NavigationMeta([section], self.options)

        self.assertEqual(len(meta.sections), 1)
        self.assertEmptyMeta(meta.sections[section])
        self.assertEmptyMeta(meta.root)

    def test_section(self):
        section = self.section(
            "Section", [self.page("Page", "section/page.md")]
        )
        meta = NavigationMeta([section], self.options)

        self.assertEqual(len(meta.sections), 1)
        self.assertMeta(meta.sections[section], path="section/.pages")
        self.assertMeta(meta.root, path=".pages")

    def test_multiple_sections(self):
        b = self.section("B", [self.page("1", "a/b/1.md")])
        a = self.section("A", [b])

        d = self.section("D", [])
        e = self.section("E", [self.page("2", "c/e/2.md")])
        c = self.section("C", [d, e])

        meta = NavigationMeta([a, c], self.options)

        self.assertEqual(len(meta.sections), 5)

        self.assertMeta(meta.sections[a], path="a/.pages")
        self.assertMeta(meta.sections[b], path="a/b/.pages")

        self.assertEmptyMeta(meta.sections[c])
        self.assertEmptyMeta(meta.sections[d])
        self.assertMeta(meta.sections[e], path="c/e/.pages")

        self.assertEmptyMeta(meta.root)

    def test_filename_option(self):
        section = self.section(
            "Section", [self.page("Page", "section/page.md")]
        )
        meta = NavigationMeta(
            [section],
            Options(
                filename=".index", collapse_single_pages=False, strict=True
            ),
        )

        self.assertEqual(len(meta.sections), 1)
        self.assertMeta(meta.sections[section], path="section/.index")
        self.assertMeta(meta.root, path=".index")

    def test_links(self):
        meta = NavigationMeta(
            [self.page("Page", "page.md"), self.link("Link")], self.options
        )

        self.assertEqual(len(meta.sections), 0)
        self.assertMeta(meta.root, path=".pages")

    def test_no_common_dirname(self):
        section = self.section(
            "Section", [self.page("1", "a/1.md"), self.page("2", "b/2.md")]
        )
        meta = NavigationMeta([section], self.options)

        self.assertEqual(len(meta.sections), 1)
        self.assertEmptyMeta(meta.sections[section])
        self.assertEmptyMeta(meta.root)
