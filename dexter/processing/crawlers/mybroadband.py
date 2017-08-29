from urlparse import urlparse, urlunparse
import re

from bs4 import BeautifulSoup
import requests

from .base import BaseCrawler
from ...models import Entity, Author, AuthorType

class MyBroadbandCrawler(BaseCrawler):
    MB_RE = re.compile('(www\.)?mybradband.co.za')

    def offer(self, url):
        """ Can this crawler process this URL? """
        parts = urlparse(url)
        return bool(self.MB_RE.match(parts.netloc))

    def extract(self, doc, raw_html):
        """ Extract text and other things from the raw_html for this document. """
        super(MyBroadbandCrawler, self).extract(doc, raw_html)

        soup = BeautifulSoup(raw_html)

        doc.title = self.extract_plaintext(soup.select("#main .the-post .entry-header .entry-title"))

        date = self.extract_plaintext(soup.select("#main .the-post .entry-header .post-date"))
        doc.published_at = self.parse_timestamp(date)

        doc.text = '\n\n'.join(item.text.strip() for item in soup.select("#main .the-post .entry-content p"))
        
        author = self.extract_plaintext(soup.select("#main .the-post .entry-header .article-meta .post-author"))

        if author:
            doc.author = Author.get_or_create(author, AuthorType.journalist())
        else:
            doc.author = Author.unknown()
