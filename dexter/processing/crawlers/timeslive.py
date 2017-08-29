from urlparse import urlparse, urlunparse
import re

from bs4 import BeautifulSoup
import requests

from .base import BaseCrawler
from ...models import Entity, Author, AuthorType

class TimesLiveCrawler(BaseCrawler):
    TL_RE = re.compile('(www\.)?timeslive.co.za')
    TLA_RE = re.compile('archive.timeslive.co.za')

    def offer(self, url):
        """ Can this crawler process this URL? """
        parts = urlparse(url)
        return bool(self.TL_RE.match(parts.netloc))

    def fetch(self, url):
        url = url + '?service=print'
        return super(TimesLiveCrawler, self).fetch(url)

    def extract_archive(self, doc, raw_html):
        """ Extract text and other things from the raw_html for this document. """
        super(TimesLiveCrawler, self).extract(doc, raw_html)

        soup = BeautifulSoup(raw_html)

        doc.title = self.extract_plaintext(soup.select(".articleheader h1"))
        doc.summary = self.extract_plaintext(soup.select(".articleheader h3"))
        doc.text = doc.summary + "\n\n" + "\n\n".join(p.text for p in soup.select(".column > p"))

        extra = self.extract_plaintext(soup.select(".articleheader div"))
        if "|" in extra:
            date, author = [s.strip() for s in extra.split("|", 1)]
        else:
            date = extra
            author = None

        doc.published_at = self.parse_timestamp(date)

        if author:
            doc.author = Author.get_or_create(author, AuthorType.journalist())
        else:
            doc.author = Author.unknown()

    def extract(self, doc, raw_html):
        # need to handle the old site being moved to archive.timeslive.co.za
        if bool(self.TLA_RE.match(urlparse(doc.url).netloc)):
            self.extract_archive(doc, raw_html)
        else:
            self.log.info(raw_html)
            """ Extract text and other things from the raw_html for this document. """
            super(TimesLiveCrawler, self).extract(doc, raw_html)
            soup = BeautifulSoup(raw_html)

            doc.title = self.extract_plaintext(soup.select(".primary-title h1.article-title-primary"))
            nodes = soup.select(".article-widget-text .text p")
            if len(nodes) > 1:
                doc.summary = self.extract_plaintext(nodes[:1])
            else:
                doc.summary = self.extract_plaintext(nodes)
            doc.text = "\n\n".join(p.text.strip() for p in nodes[1:])

            date = self.extract_plaintext(soup.select(".article-pub-date"))
            author = self.extract_plaintext(soup.select(".article-pub-date .heading-author"))

            doc.published_at = self.parse_timestamp(date)

            if author:
                doc.author = Author.get_or_create(author, AuthorType.journalist())
            else:
                doc.author = Author.unknown()
