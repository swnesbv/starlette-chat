import asyncio
from datetime import datetime
from urllib.parse import urljoin, urlparse
from urllib.request import urlopen
from urllib.error import HTTPError
from bs4 import BeautifulSoup


async def generate_sitemap(url):

    root = url.rstrip("/")
    sitemap = set()
    visited = set()
    original_domain = urlparse(root).netloc

    async def add_url(root, path):
        if not path.startswith("http"):
            path = urljoin(root, path)
        sitemap.add(path)

    async def extract_urls(soup, root):
        for link in soup.find_all("a", href=True):
            url = link["href"]
            parsed_url = urlparse(url)
            if parsed_url.netloc == original_domain or not parsed_url.netloc:
                await add_url(root, url)

    stack = [url]

    while stack:
        current_url = stack.pop()
        if current_url in visited:
            continue
        visited.add(current_url)

        if not current_url.startswith(root):
            continue
        try:
            response = urlopen(current_url.replace(' ', '%20'))
        except HTTPError as e:
            print(f" err sitemap.. {current_url}: {e}")
            continue

        if response.status == 200:
            soup = BeautifulSoup(response, "html.parser")
            await extract_urls(soup, root)

            for link in soup.find_all("a", href=True):
                next_url = link["href"]
                if not next_url.startswith("http"):
                    next_url = urljoin(root, next_url)
                stack.append(next_url)

    xml_content = '<?xml version="1.0" encoding="UTF-8"?>\n'
    xml_content += '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'

    for i in sitemap:
        xml_content += "    <url>\n"
        xml_content += f"       <loc>{i}</loc>\n"
        xml_content += f"       <lastmod>{datetime.now().date().isoformat()}</lastmod>\n"
        xml_content += "        <changefreq>weekly</changefreq>\n"
        xml_content += "        <priority>0.8</priority>\n"
        xml_content += "    </url>\n"

    xml_content += "</urlset>"

    with open("./static/sitemap.xml", "w", encoding="utf-8") as f:
        f.write(xml_content)
        print(" sitemap write..")
    print(" sitemap generated successfully..")

asyncio.run(generate_sitemap("http://localhost:8000/"))
