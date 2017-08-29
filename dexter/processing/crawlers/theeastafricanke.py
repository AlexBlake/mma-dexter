from urlparse import urlparse, urlunparse
import re

from bs4 import BeautifulSoup
import requests

from .base import BaseCrawler
from ...models import Entity, Author, AuthorType

class TheEastAfricanKECrawler(BaseCrawler):
    TEAKE_RE = re.compile('(www\.)?theeastafrican.co.ke')

    def offer(self, url):
        """ Can this crawler process this URL? """
        parts = urlparse(url)
        return bool(self.TEAKE_RE.match(parts.netloc))

    def extract(self, doc, raw_html):
        """ Extract text and other things from the raw_html for this document. """
        raw_html = raw_html.encode("utf-8")
        raw_html = unicode(raw_html, errors='ignore')

        super(TheEastAfricanKECrawler, self).extract(doc, raw_html)

        soup = BeautifulSoup(raw_html)

        # gather title
        doc.title = self.extract_plaintext(soup.select(".main .story-view header h1"))

        #gather publish date
        published_text = self.extract_plaintext(soup.select(".main .story-view header h5"))
        doc.published_at = self.parse_timestamp(published_text)
        
        #gather text and summary
        nodes = soup.select(".main .article .body-copy p")
        if len(nodes) > 1:
            doc.summary = self.extract_plaintext(nodes[0:1])
        doc.text = "\n\n".join(p.text.strip() for p in nodes)

        # gather author 
        author = soup.select(".main .article .body-copy .author strong")
        if len(author) == 0:
            author = soup.select(".main .article .body-copy .author")
        author = self.extract_plaintext(author)
        if author[:2] == "By":
            author = author[2:].strip()

        if author:
            doc.author = Author.get_or_create(author.strip(), AuthorType.journalist())
        else:
            doc.author = Author.unknown()


