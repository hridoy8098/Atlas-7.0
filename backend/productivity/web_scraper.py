import re
import time
from urllib.parse import urljoin, urlparse

import requests
from bs4 import BeautifulSoup


class WebScraper:
    def __init__(self, user_agent=None, timeout=30, delay=1):
        self.user_agent = user_agent or (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/120.0.0.0 Safari/537.36"
        )
        self.timeout = timeout
        self.delay = delay
        self._session = requests.Session()
        self._session.headers.update({"User-Agent": self.user_agent})

    def _respect_delay(self):
        if self.delay > 0:
            time.sleep(self.delay)

    def fetch_page(self, url):
        self._respect_delay()
        try:
            resp = self._session.get(url, timeout=self.timeout)
            resp.raise_for_status()
            resp.encoding = resp.apparent_encoding or resp.encoding
            return resp.text
        except requests.RequestException as e:
            raise ConnectionError(f"Failed to fetch {url}: {e}")

    def fetch_soup(self, url):
        html = self.fetch_page(url)
        return BeautifulSoup(html, "html.parser")

    def extract_text(self, url):
        soup = self.fetch_soup(url)
        for tag in soup(["script", "style", "nav", "footer", "header", "aside"]):
            tag.decompose()
        text = soup.get_text(separator="\n")
        text = re.sub(r"\n\s*\n", "\n\n", text).strip()
        return text

    def extract_links(self, url, base_url=None):
        soup = self.fetch_soup(url)
        base = base_url or url
        links = set()
        for a_tag in soup.find_all("a", href=True):
            href = a_tag["href"]
            absolute = urljoin(base, href)
            parsed = urlparse(absolute)
            if parsed.scheme in ("http", "https"):
                links.add(absolute)
        return sorted(links)

    def extract_images(self, url):
        soup = self.fetch_soup(url)
        images = []
        for img in soup.find_all("img", src=True):
            src = urljoin(url, img["src"])
            alt = img.get("alt", "")
            images.append({"src": src, "alt": alt})
        return images

    def extract_headings(self, url):
        soup = self.fetch_soup(url)
        headings = []
        for tag in ("h1", "h2", "h3", "h4", "h5", "h6"):
            for elem in soup.find_all(tag):
                headings.append({"level": tag, "text": elem.get_text(strip=True)})
        return headings

    def extract_metadata(self, url):
        soup = self.fetch_soup(url)
        meta = {}
        for tag in soup.find_all("meta"):
            name = tag.get("name") or tag.get("property") or ""
            content = tag.get("content", "")
            if name and content:
                meta[name] = content
        title_tag = soup.find("title")
        if title_tag:
            meta["title"] = title_tag.get_text(strip=True)
        return meta

    def search_text(self, url, query):
        text = self.extract_text(url)
        results = []
        for i, line in enumerate(text.split("\n"), 1):
            if query.lower() in line.lower():
                results.append({"line": i, "text": line.strip()})
        return results

    def crawl_links(self, start_url, max_pages=10, same_domain=True):
        visited = set()
        to_visit = {start_url}
        pages = {}
        base_domain = urlparse(start_url).netloc

        while to_visit and len(visited) < max_pages:
            url = to_visit.pop()
            if url in visited:
                continue
            try:
                text = self.extract_text(url)
                visited.add(url)
                pages[url] = text[:2000]
                links = self.extract_links(url)
                for link in links:
                    if link not in visited:
                        if same_domain and urlparse(link).netloc != base_domain:
                            continue
                        to_visit.add(link)
            except (ConnectionError, Exception):
                visited.add(url)
                continue

        return {"pages": pages, "visited_count": len(visited)}
