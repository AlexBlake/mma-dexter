from urlparse import urlparse, urlunparse
import re

from bs4 import BeautifulSoup
import requests
import logging

from .base import BaseCrawler
from ...models import Entity, Author, AuthorType

class NewsNowCrawler(BaseCrawler):
    NewsNow = re.compile('(www\.)?newsnow.co.za')
    log = logging.getLogger(__name__)


    def offer(self, url):
        """ Can this crawler process this URL? """
        parts = urlparse(url)
        return bool(self.NewsNow.match(parts.netloc))


    def extract(self, doc, raw_html):
        """ Extract text and other things from the raw_html for this document. """
        raw_html = raw_html.encode("utf-8")
        raw_html = unicode(raw_html, errors='ignore')

        super(NewsNowCrawler, self).extract(doc, raw_html)

        soup = BeautifulSoup(raw_html)

        # gather title
        doc.title = self.extract_plaintext(soup.find(attrs={"property":"og:title"})['content'])

        #gather text and summary
        nodes = soup.select("#main-content .entry-content > p")
        if len(nodes) > 1:
            doc.summary = self.extract_plaintext(nodes[:1])
        else:
            doc.summary = self.extract_plaintext(nodes)
        doc.text = "\n\n".join(p.text.strip() for p in nodes[1:])
        
        #gather publish date
        doc.published_at = self.parse_timestamp(soup.find(attrs={"property":"article:published_time"})['content'])

        # gather author
        author = self.extract_plaintext(self.select("#main-content .post .entry-header .entry-meta-author a.fn"))

        if author:
            doc.author = Author.get_or_create(author, AuthorType.journalist())
        else:
            doc.author = Author.unknown()
