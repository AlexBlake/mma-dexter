from urlparse import urlparse, urlunparse
import re

from bs4 import BeautifulSoup
import requests
import logging

from .base import BaseCrawler
from ...models import Entity, Author, AuthorType

class PoliticsWebCrawler(BaseCrawler):
    PWeb = re.compile('(www\.)?politicsweb.co.za')
    log = logging.getLogger(__name__)


    def offer(self, url):
        """ Can this crawler process this URL? """
        parts = urlparse(url)
        return bool(self.PWeb.match(parts.netloc))

        
    # def fetch(self, url):
    #     """
    #     Fetch and return the raw HTML for this url.
    #     The return content is a unicode string.
    #     """
    #     headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}
    #     r = requests.get(url, timeout=10, headers=headers, verify=False)
    #     # raise an HTTPError on badness
    #     r.raise_for_status()

    #     # this decodes r.content using a guessed encoding
    #     return r.text


    def extract(self, doc, raw_html):
        """ Extract text and other things from the raw_html for this document. """
        raw_html = raw_html.encode("utf-8")
        raw_html = unicode(raw_html, errors='ignore')

        super(PoliticsWebCrawler, self).extract(doc, raw_html)

        soup = BeautifulSoup(raw_html)

        # gather title
        doc.title = self.extract_plaintext(soup.select("#DailyNewsHeadline"))

        #gather text and summary
        nodes = soup.select(".main-content .top-stories section > article p")
        if len(nodes) > 1:
            doc.summary = self.extract_plaintext(nodes[:1])
        else:
            doc.summary = self.extract_plaintext(nodes)
        doc.text = "\n\n".join(p.text.strip() for p in nodes[1:])
        
        meta = soup.select(".main-content .top-stories .article-date")
        #gather publish date
        doc.published_at = self.parse_timestamp(self.extract_plaintext(meta[1:]))

        # gather author
        author = self.extract_plaintext(meta[:1]).replace("|", "").strip()

        if author:
            doc.author = Author.get_or_create(author, AuthorType.journalist())
        else:
            doc.author = Author.unknown()
