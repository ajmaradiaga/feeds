"""Regenerate the member/topic feed tables in Markdown.

Merged from the former feeds-jobs/members_markdown_generator.py and
topics_markdown_generator.py. Output is written to jobs/markdown/ (same table
content as before); the curated scmt/*/README.md files are left untouched.
"""

import os

from jobs import config

RAW_BASE = "https://raw.githubusercontent.com/ajmaradiaga/feeds/main/scmt"
OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "markdown")


def _slug(name):
    return name.replace(' ', '-').replace(',', '').replace('/', '')


def members_markdown():
    contents = []

    def group(title, members, folder, frequency):
        contents.extend([f"| **{title}** | **Username** | **Feed** | **Frequency** |",
                         "| --- | --- | --- | --- |"])
        for fullname, username in members.items():
            file_name = _slug(username)
            contents.append(
                f"| {fullname} | {username} | [URL]({RAW_BASE}/members/{folder}/{file_name}.xml) | {frequency} |")
        contents.extend(["", ""])

    group("Developer Advocates", config.DEVELOPER_ADVOCATES, "developer-advocates", "12 hours")
    group("SAP Mentors", config.SAP_MENTORS, "sap-mentors", "24 hours")
    group("SAP Champions", config.SAP_CHAMPIONS, "sap-champions", "24 hours")

    return "\n".join(contents)


def topics_markdown():
    topics = ["| **Topic** | **Blog posts feed** | **Q&A feed** | **Frequency** |",
              "| --- | --- | --- | --- |"]

    for key in config.PRIORITY_TOPICS:
        file_name = _slug(key)
        topics.append(
            f"| {key} | [URL]({RAW_BASE}/topics/{file_name}-blog-posts.xml) | [URL]({RAW_BASE}/topics/{file_name}-qa.xml) | 3 hours |")

    topics.append("| ------------ | --------------- | ------ | ------ | ------ |")

    for key in config.DAILY_TOPICS:
        file_name = _slug(key)
        topics.append(
            f"| {key} | [URL]({RAW_BASE}/topics/{file_name}-blog-posts.xml) | [URL]({RAW_BASE}/topics/{file_name}-qa.xml) | Twice daily |")

    return "\n".join(topics)


def generate_markdown():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    with open(os.path.join(OUTPUT_DIR, "members.md"), "w") as f:
        f.write(members_markdown() + "\n")
    with open(os.path.join(OUTPUT_DIR, "topics.md"), "w") as f:
        f.write(topics_markdown() + "\n")
    print(f"Wrote markdown tables to {OUTPUT_DIR}")


if __name__ == "__main__":
    generate_markdown()
