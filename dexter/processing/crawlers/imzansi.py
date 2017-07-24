from urlparse import urlparse, urlunparse
import re

from bs4 import BeautifulSoup
import requests

from .base import BaseCrawler
from ...models import Entity, Author, AuthorType

class ImzansiCrawler(BaseCrawler):
    IM_RE = re.compile('(www\.)?imzansi.com')

    def offer(self, url):
        """ Can this crawler process this URL? """
        parts = urlparse(url)
        return bool(self.IM_RE.match(parts.netloc))


    def extract(self, doc, raw_html):
        """ Extract text and other things from the raw_html for this document. """
        super(ImzansiCrawler, self).extract(doc, raw_html)

        soup = BeautifulSoup(raw_html)

        # gather title
        doc.title = self.extract_plaintext(soup.select(".content .post h1.post-title"))

        #gather publish date
        date = self.extract_plaintext(soup.select(".content .post .post-byline .published"))
        doc.published_at = self.parse_timestamp(date)
        
        #gather text and summary
        nodes = soup.select(".content .post .entry-inner p")
        if len(nodes) > 1:
            doc.summary = self.extract_plaintext(nodes[0:1])
        doc.text = "\n\n".join(p.text.strip() for p in nodes[2:])

        # gather author 
        author = self.extract_plaintext(soup.select(".content .post .post-byline .author .fn a"))
        if author:
            doc.author = Author.get_or_create(author.strip(), AuthorType.journalist())
        else:
            doc.author = Author.unknown()
