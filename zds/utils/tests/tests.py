# coding: utf-8

from django.test import TestCase

from zds.article.factories import ArticleFactory, LicenceFactory
from zds.member.factories import ProfileFactory
from zds.tutorial.factories import BigTutorialFactory, ChapterFactory, PartFactory, ExtractFactory
from zds.gallery.factories import GalleryFactory

from zds.utils.articles import export_article
from zds.utils.tutorials import export_chapter

class ArticleTest(TestCase):

    def test_export_article(self):
        user_author = ProfileFactory().user
        licence = LicenceFactory()

        article = ArticleFactory()
        article.authors.add(user_author)
        article.licence = licence
        
        result = export_article(article)

        self.assertEqual(result["title"], article.title)
        self.assertEqual(result["description"], article.description)
        self.assertEqual(result["type"], "article")
        self.assertEqual(result["text"], article.text)
        self.assertEqual(result["licence"], article.licence.code)

class TutorialTest(TestCase):

    def setUp(self):
        self.user_author = ProfileFactory().user
        
        self.bigtuto = BigTutorialFactory(light=True)
        self.bigtuto.authors.add(self.user_author)
        self.bigtuto.gallery = GalleryFactory()
        self.bigtuto.licence = LicenceFactory()
        self.bigtuto.save()

        self.part1 = PartFactory(tutorial=self.bigtuto, position_in_tutorial=1)

        self.chapter1 = ChapterFactory(
            part=self.part1,
            position_in_part=1,
            position_in_tutorial=1)

        self.extract1 = ExtractFactory(
            chapter=self.chapter1,
            position_in_chapter=1)

    def test_export_chapter(self):
        result = export_chapter(self.chapter1)

        self.assertEqual(result["pk"], self.chapter1.pk)
        self.assertEqual(result["title"], self.chapter1.title)
        self.assertEqual(result["introduction"], self.chapter1.introduction)
        self.assertEqual(result["conclusion"], self.chapter1.conclusion)
        self.assertEqual(len(result["extracts"]), 1)
        self.assertEqual(result["extracts"][0]["pk"], self.extract.pk)
        self.assertEqual(result["extracts"][0]["title"], self.extract.title)
        self.assertEqual(result["extracts"][0]["text"], self.extract.text)

    def test_export_part(self):
        result = export_part(self.extract1) 

        self.assertEqual(result["pk"], self.extract1.pk)
        self.assertEqual(result["title"], self.extract1.title)
        self.assertEqual(result["introduction"], self.extract1.introduction)
        self.assertEqual(result["conclusion"], self.extract1.conclusion)

    def test_export_tutorial(self):
        result = export_tutorial(self.bigtuto)
