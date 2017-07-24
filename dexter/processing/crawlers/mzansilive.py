from urlparse import urlparse, urlunparse
import re

from bs4 import BeautifulSoup
import requests

from .base import BaseCrawler
from ...models import Entity, Author, AuthorType

class MzansiLiveCrawler(BaseCrawler):
    MZL_RE = re.compile('(www\.)?mzansilive.co.za')

    def offer(self, url):
        """ Can this crawler process this URL? """
        parts = urlparse(url)
        return bool(self.MZL_RE.match(parts.netloc))


    def extract(self, doc, raw_html):
        """ Extract text and other things from the raw_html for this document. """
        super(MzansiLiveCrawler, self).extract(doc, raw_html)

        soup = BeautifulSoup(raw_html)

        # gather title
        doc.title = soup.find(attrs={"property":"og:title"})['content']

        #gather publish date
        date = soup.find(attrs={"property":"article:published_time"})['content']
        doc.published_at = self.parse_timestamp(date)
        
        #gather text and summary
        nodes = soup.select(".post .td-post-content p")
        if len(nodes) > 1:
            doc.summary = self.extract_plaintext(nodes[0:1])
        doc.text = "\n\n".join(p.text.strip() for p in nodes[2:])

        # gather author 
        author = soup.find(attrs={"itemprop":"author"}).find(attrs={"itemprop":"name"})["content"]
        if author:
            doc.author = Author.get_or_create(author.strip(), AuthorType.journalist())
        else:
            doc.author = Author.unknown()
