from urlparse import urlparse, urlunparse
import re

from bs4 import BeautifulSoup
import requests

from .base import BaseCrawler
from ...models import Entity, Author, AuthorType

class SouthAfricaLatestNewsCrawler(BaseCrawler):
    SALN_RE = re.compile('(www\.)?southafricalatestnews.co.za')

    def offer(self, url):
        """ Can this crawler process this URL? """
        parts = urlparse(url)
        return bool(self.SALN_RE.match(parts.netloc))

    def extract(self, doc, raw_html):
        """ Extract text and other things from the raw_html for this document. """
        super(SouthAfricaLatestNewsCrawler, self).extract(doc, raw_html)

        soup = BeautifulSoup(raw_html)

        doc.title = self.extract_plaintext(soup.select(".ja-content-main .item-page .header-content h2"))

        date = self.extract_plaintext(soup.select(".ja-content-main .item-page .article-info .published")).replace('Published: ', '')
        doc.published_at = self.parse_timestamp(date)

        doc.text = ''.join(soup.select(".ja-content-main .item-page")[0].findAll(text=True, recursive=False))
        
        author = self.extract_plaintext(soup.select(".ja-content-main .item-page .article-info .createdby")).replace("Written by ", '')

        if author:
            doc.author = Author.get_or_create(author.rstrip('Photo').strip(), AuthorType.journalist())
        else:
            doc.author = Author.unknown()
