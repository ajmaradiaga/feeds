"""SAP Community Atom feed generators.

Ported from the former feeds-jobs/skills.py. The per-entry build loop, which was
copy-pasted across the three generators, is factored into ``build_feed``. Feed
output (ids, titles, filenames, query strings) is unchanged so existing
subscribers are unaffected.
"""

import os
import random
import time
from datetime import datetime

import requests
from feedgen.feed import FeedGenerator

# Repo-root-relative output dir. Defaults to "scmt" (run from the feeds repo
# root); overridable via env for local testing.
OUTPUT_ROOT = os.environ.get("FEEDS_OUTPUT_ROOT", "scmt")

conversation_styles = {
    "blog": {"description": "blog posts", "file_name": "blog-posts"},
    "qanda": {"description": "Q&A", "file_name": "qa"}
}


def build_feed(items, feed_id, title, link, description):
    """Build a FeedGenerator from SAP Community search ``items``.

    Sets the feed-level metadata and appends one entry per item using the exact
    field mapping the original generators used.
    """
    fg = FeedGenerator()
    fg.id(feed_id)
    fg.title(title)
    fg.link(href=link, rel='alternate')
    fg.description(description)

    for entry in items:
        fe = fg.add_entry()
        fe.id(entry['view_href'])
        fe.title(entry['subject'])
        fe.link(href=entry['view_href'])
        fe.description(entry['search_snippet'])
        fe.content(entry['body'])

        author = entry['author']

        # Handling former members
        if author is not None:
            if 'view_href' in author:
                fe.author(name=author['login'], uri=author['view_href'])
            else:
                fe.author(name=author['login'])

        date_object = datetime.strptime(
            entry['post_time'], "%Y-%m-%dT%H:%M:%S.%f%z")
        fe.pubDate(date_object)
        fe.updated(date_object)

    return fg


def _write(fg, path):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    fg.atom_file(path, extensions=False, pretty=True)


def sap_community_replies():
    url = "https://community.sap.com/api/2.0/search?q=SELECT  id, href, view_href, subject, author, search_snippet, post_time, conversation, body FROM messages"

    # Send a GET request to the URL
    response = requests.get(url)

    # Check if the request was successful
    if response.status_code == 200:
        # Parse the JSON response
        data = response.json()
        items = data['data']['items']

        file_name = "all_replies"

        fg = build_feed(
            items,
            feed_id=f'https://raw.githubusercontent.com/ajmaradiaga/feeds/main/scmt/{file_name}.xml',
            title='SAP Community - All Replies',
            link="https://community.sap.com/",
            description='Replies in SAP Community',
        )

        _write(fg, f'{OUTPUT_ROOT}/{file_name}.xml')


def sap_community_members(members, sub_folder):
    for fullname, username in members.items():

        try:
            print(f"Processing {fullname} - {username}...")

            # Define the URL
            url = "https://community.sap.com/api/2.0/search?q=select%20id,%20view_href,%20author,%20subject,%20body,%20board.id,%20board.view_href,%20search_snippet,%20post_time,%20conversation.style%20from%20messages%20where%20" + \
                f"author.login=%27{username}%27%20LIMIT%2020"
            print(url)

            # Send a GET request to the URL
            response = requests.get(url)

            # Check if the request was successful
            if response.status_code == 200:
                # Parse the JSON response
                data = response.json()
                items = data['data']['items']

                # Setting the user profile as the feed link
                feed_link = items[0]['author']['view_href']

                # Write the RSS feed to a file
                file_name = username.replace(' ', '-').replace(',', '').replace('/', '')

                fg = build_feed(
                    items,
                    feed_id=f'https://raw.githubusercontent.com/ajmaradiaga/feeds/main/scmt/members/{sub_folder}/{file_name}.xml',
                    title=f'SAP Community - {fullname}',
                    link=feed_link,
                    description=f'{fullname} in SAP Community',
                )

                _write(fg, f'{OUTPUT_ROOT}/members/{sub_folder}/{file_name}.xml')
        except Exception as e:
            print(f"Failed to retrieve {fullname} - {username}...{str(e)}")

        # Sleep for a random number between 1 and 5 seconds
        sleep_time = random.randint(1, 2)

        print(f"Sleeping for {sleep_time} seconds...")
        time.sleep(sleep_time)


def sap_community_topics(topics):

    for mt_key, mt_id in topics.items():
        print(f"Processing {mt_key} - {mt_id}...")
        for cs_key, cs_options in conversation_styles.items():

            # Define the URL
            url = "https://community.sap.com/api/2.0/search?q=SELECT%20id,%20href,%20view_href,%20subject,%20body,%20author,search_snippet,%20post_time,conversation.style%20FROM%20messages%20WHERE%20conversation.style = '" + \
                cs_key + "' AND products.id = '" + mt_id + \
                "' AND products.includes = true%20and%20conversation.style%20=%20%27blog%27%20LIMIT%2020"
            print(url)
            # Send a GET request to the URL
            response = requests.get(url)

            # Check if the request was successful
            if response.status_code == 200:
                # Parse the JSON response
                data = response.json()

                feed_link = f"https://community.sap.com/t5/c-khhcw49343/{mt_key}/pd-p/{mt_id}"

                # Write the RSS feed to a file
                file_name = mt_key.replace(' ', '-').replace(',', '').replace('/', '') + '-' + cs_options["file_name"]

                fg = build_feed(
                    data['data']['items'],
                    feed_id=f'https://raw.githubusercontent.com/ajmaradiaga/feeds/main/scmt/topics/{file_name}.xml',
                    title=f'SAP Community - {mt_key}',
                    link=feed_link,
                    description=f'{mt_key} {cs_options["description"]} in SAP Community',
                )

                _write(fg, f'{OUTPUT_ROOT}/topics/{file_name}.xml')
            else:
                print(
                    f"Failed to retrieve data from URL. Status code: {response.status_code}")

        # Sleep for a random number between 1 and 5 seconds
        sleep_time = random.randint(1, 2)

        print(f"Sleeping for {sleep_time} seconds...")
        time.sleep(sleep_time)
