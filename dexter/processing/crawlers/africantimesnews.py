from urlparse import urlparse, urlunparse
import re

from bs4 import BeautifulSoup
import requests
import logging

from .base import BaseCrawler
from ...models import Entity, Author, AuthorType

import datetime

class AfricanTimesCrawler(BaseCrawler):
    AfricanTimes = re.compile('(www\.)?africantimesnews.co.za')
    log = logging.getLogger(__name__)


    def offer(self, url):
        """ Can this crawler process this URL? """
        parts = urlparse(url)
        return bool(self.AfricanTimes.match(parts.netloc))


    def extract(self, doc, raw_html):
        """ Extract text and other things from the raw_html for this document. """
        raw_html = raw_html.encode("utf-8")
        raw_html = unicode(raw_html, errors='ignore')

        super(AfricanTimesCrawler, self).extract(doc, raw_html)

        soup = BeautifulSoup(raw_html)

        # gather title
        doc.title = self.extract_plaintext(soup.select("#rd_module_signle .rd-single-item .post .rd-details .rd-title"))

        #gather text and summary
        nodes = soup.select("#rd_module_signle .post .rd-post-content > *")

        if len(nodes) > 1:
            doc.summary = self.extract_plaintext(nodes[:1])
        else:
            doc.summary = self.extract_plaintext(nodes)

        doc.text = "\n\n".join(p.text.strip() for p in nodes[1:])
        
        #gather publish date
        time_dif = self.extract_plaintext(soup.select("#rd_module_signle .rd-single-item .post .rd-details .rd-meta .rd-date")).split()
        time_qty = int(time_dif[0])
        time_unit = time_dif[1]
        if bool(re.compile('Day(s)?').match(time_unit)):
            doc.published_at = ( datetime.date.today() - datetime.timedelta(days=time_qty) )
        elif bool(re.compile('Hour(s)?').match(time_unit)):
            doc.published_at = ( datetime.date.today() - datetime.timedelta(hours=time_qty) )
        elif bool(re.compile('Months(s)?').match(time_unit)):
            doc.published_at = ( datetime.date.today() - datetime.timedelta(months=time_qty) )

        # gather author
        author = self.extract_plaintext(soup.select("#rd_module_signle .rd-single-item .post .rd-details .rd-meta .rd-author")).replace("by ", "").strip()

        if author:
            doc.author = Author.get_or_create(author, AuthorType.journalist())
        else:
            doc.author = Author.unknown()
