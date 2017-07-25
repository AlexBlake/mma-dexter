from urlparse import urlparse, urlunparse
import re

from bs4 import BeautifulSoup
import requests

from .base import BaseCrawler
from ...models import Entity, Author, AuthorType

class LiveMonitorCrawler(BaseCrawler):
    LM_RE = re.compile('(www\.)?livemonitor.co.za')

    def offer(self, url):
        """ Can this crawler process this URL? """
        parts = urlparse(url)
        return bool(self.LM_RE.match(parts.netloc))


    def extract(self, doc, raw_html):
        """ Extract text and other things from the raw_html for this document. """
        super(LiveMonitorCrawler, self).extract(doc, raw_html)

        soup = BeautifulSoup(raw_html)
        
        doc.title = soup.find(attrs={"property":"og:title"})['content']

        #gather publish date
        date = soup.find(attrs={"property":"article:published_time"})['content']
        doc.published_at = self.parse_timestamp(date)
        
        #gather text and summary
        nodes = soup.select("#main-content .entry-content p")
        if len(nodes) > 1:
            doc.summary = self.extract_plaintext(nodes[0:1])
        doc.text = "\n\n".join(p.text.strip() for p in nodes[2:])

        # gather author 
        author = self.extract_plaintext(soup.select('.entry-meta-author a.fn'))
        if author:
            doc.author = Author.get_or_create(author.strip(), AuthorType.journalist())
        else:
            doc.author = Author.unknown()
