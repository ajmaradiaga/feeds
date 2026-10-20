"""CLI entrypoint for feed generation.

Usage:
    python -m jobs.generate --job <name>

Jobs map one-to-one onto the cron entries in
.github/workflows/generate-feeds.yml.
"""

import argparse

from jobs import config
from jobs.feeds import (
    sap_community_members,
    sap_community_replies,
    sap_community_topics,
)
from jobs.markdown import generate_markdown

# job name -> callable
JOBS = {
    "replies": sap_community_replies,
    "topics-priority": lambda: sap_community_topics(config.PRIORITY_TOPICS),
    "topics-daily": lambda: sap_community_topics(config.DAILY_TOPICS),
    "members-advocates": lambda: sap_community_members(config.DEVELOPER_ADVOCATES, "developer-advocates"),
    "members-champions": lambda: sap_community_members(config.SAP_CHAMPIONS, "sap-champions"),
    "members-mentors": lambda: sap_community_members(config.SAP_MENTORS, "sap-mentors"),
    "members-community": lambda: sap_community_members(config.SAP_COMMUNITY_MEMBERS, "sap-community-members"),
    "markdown": generate_markdown,
}


def main():
    parser = argparse.ArgumentParser(description="SAP Community feed generator")
    parser.add_argument("--job", required=True, choices=sorted(JOBS), help="Which job to run")
    args = parser.parse_args()

    print(f"Running job: {args.job}")
    JOBS[args.job]()
    print(f"Done: {args.job}")


if __name__ == "__main__":
    main()
