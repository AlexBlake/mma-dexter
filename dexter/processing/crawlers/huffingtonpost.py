from urlparse import urlparse, urlunparse
import re

from bs4 import BeautifulSoup
import requests
import logging

from .base import BaseCrawler
from ...models import Entity, Author, AuthorType

class HuffingtonPostCrawler(BaseCrawler):
    HuffingtonPost = re.compile('(www\.)?huffingtonpost.co.za')
    log = logging.getLogger(__name__)


    def offer(self, url):
        """ Can this crawler process this URL? """
        parts = urlparse(url)
        return bool(self.HuffingtonPost.match(parts.netloc))


    def extract(self, doc, raw_html):
        """ Extract text and other things from the raw_html for this document. """
        raw_html = raw_html.encode("utf-8")
        raw_html = unicode(raw_html, errors='ignore')

        super(HuffingtonPostCrawler, self).extract(doc, raw_html)

        soup = BeautifulSoup(raw_html)

        # gather title
        doc.title = self.extract_plaintext(soup.select(".entry-page-content .headline .headline__title"))

        #gather text and summary
        nodes = soup.select(".page__content .entry__content .post-contents p")
        if len(nodes) > 1:
            doc.summary = self.extract_plaintext(nodes[:1])
        else:
            doc.summary = self.extract_plaintext(nodes)
        doc.text = "\n\n".join(p.text.strip() for p in nodes[1:])
        
        #gather publish date
        doc.published_at = self.parse_timestamp(self.extract_plaintext(soup.select(".entry-page-content .timestamp .timestamp__date--published")))

        # gather author
        author = self.extract_plaintext(soup.select(".entry-page-content .author-byline .author-card .author-card__details .author-card__details__name"))

        if author:
            doc.author = Author.get_or_create(author, AuthorType.journalist())
        else:
            doc.author = Author.unknown()
