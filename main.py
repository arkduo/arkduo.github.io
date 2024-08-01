import requests
from string import Template

# APIからJSONデータを取得する
url = 'https://d3watch.gg/index.php?rest_route=/wp/v2/posts'
response = requests.get(url)
json_data = response.json()

# XML全体のテンプレート
xml_template = Template('''<?xml version="1.0" encoding="UTF-8" ?>
<rss xmlns:content="http://purl.org/rss/1.0/modules/content/" xmlns:dc="http://purl.org/dc/elements/1.1/" version="2.0">
    <channel>
        <title>$title</title>
        <link>$link</link>
        <description>$description</description>
        <language>ja</language>$items
    </channel>
</rss>''')

# 個別記事用テンプレート
item_template = Template('''
        <item>
            <title>$title</title>
            <link>$link</link>
            <description><![CDATA[ $description ]]></description>
            <guid>$guid</guid>
            <pubDate>$pubDate</pubDate>
        </item>''')

# JSONデータをXML形式に変換
items_xml = ''

for item in json_data:
    title = item['title']['rendered']
    link = item['link']
    description = item['excerpt']['rendered'].replace("\n", "").replace("\r", "")
    guid = item['guid']['rendered']
    pubDate = item['date']
    items_xml += item_template.substitute(title=title,
                                          link=link,
                                          description=description,
                                          guid=guid,
                                          pubDate=pubDate)

title = 'd3watch'
link = 'https://d3watch.gg'
description = ''
final_xml_content = xml_template.substitute(title=title,
                                            link=link,
                                            description=description,
                                            items=items_xml)

# XMLデータをファイルに出力する
xml_filename = "data\d3watch.xml"
with open(xml_filename, "w", encoding="utf-8") as file:
    file.write(final_xml_content)
