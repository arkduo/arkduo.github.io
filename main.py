from urllib.parse import urljoin

import requests
from string import Template
from bs4 import BeautifulSoup

# --- サイトごとの記事取得関数 ---
def fetch_articles_d3watch():
    url = 'https://d3watch.gg/index.php?rest_route=/wp/v2/posts'
    response = requests.get(url)
    json_data = response.json()
    articles = []
    for item in json_data:
        title = item['title']['rendered']
        link = item['link']
        description = BeautifulSoup(
            item['excerpt']['rendered'].replace("\n", "").replace("\r", ""),
            'html.parser'
        ).get_text()
        guid = item['guid']['rendered']
        pubDate = item['date']
        articles.append({
            'title': title,
            'link': link,
            'description': description,
            'guid': guid,
            'pubDate': pubDate
        })
    return articles

def fetch_articles_over_hub():
    url = 'https://over-hub.com/'
    response = requests.get(url)
    response.raise_for_status()
    response.encoding = response.apparent_encoding
    soup = BeautifulSoup(response.text, 'html.parser')
    items = soup.find_all("div", class_="entry-card-content") or \
            [a for a in soup.find_all("article") if "group/card" not in a.get("class", [])] or \
            soup.select(".entry-card-wrap")
    articles = []
    for item in items:
        title_el = item.find("h3")
        title = title_el.get_text(strip=True) if title_el else "No Title"
        link_el = item.find("a")
        link = link_el.get("href") if link_el else ""
        desc_el = item.find("p")
        description = desc_el.get_text(strip=True) if desc_el else ""
        date_el = item.find("time") or item.find("span")
        pub_date = date_el.get_text(strip=True) if date_el else ""
        articles.append({
            'title': title,
            'link': urljoin(url, link),
            'description': description,
            'guid': '',
            'pubDate': pub_date
        })
    return articles

# --- RSS生成処理 ---
xml_template = Template('''<?xml version="1.0" encoding="UTF-8" ?>
<rss xmlns:content="http://purl.org/rss/1.0/modules/content/" xmlns:dc="http://purl.org/dc/elements/1.1/" version="2.0">
    <channel>
        <title>$title</title>
        <link>$link</link>
        <description>$description</description>
        <language>ja</language>$items
    </channel>
</rss>''')

item_template = Template('''
        <item>
            <title>$title</title>
            <link>$link</link>
            <description><![CDATA[ $description ]]></description>
            <guid>$guid</guid>
            <pubDate>$pubDate</pubDate>
        </item>''')

def generate_rss_xml(articles, title, link, description, xml_filename):
    items_xml = ''
    for item in articles:
        items_xml += item_template.substitute(
            title=item['title'],
            link=item['link'],
            description=item['description'],
            guid=item['guid'],
            pubDate=item['pubDate']
        )
    final_xml_content = xml_template.substitute(
        title=title,
        link=link,
        description=description,
        items=items_xml
    )
    with open(xml_filename, "w", encoding="utf-8") as file:
        file.write(final_xml_content)

# --- メイン処理 ---
if __name__ == "__main__":
    # サイトごとに記事取得
    articles_d3watch = fetch_articles_d3watch()
    articles_over_hub = fetch_articles_over_hub()

    # サイトごとに個別RSS生成
    generate_rss_xml(
        articles_d3watch,
        title='d3watch',
        link='https://d3watch.gg',
        description='',
        xml_filename="data/d3watch.xml"
    )
    generate_rss_xml(
        articles_over_hub,
        title='over-hub',
        link='https://over-hub.com/',
        description='',
        xml_filename="data/over-hub.xml"
    )
