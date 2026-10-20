# feeds

Generated **Atom** feeds for [SAP Community](https://community.sap.com) content.
The SAP Community platform does not expose native RSS/Atom feeds for topics
(Managed Tags) or for individual members, so this repo generates them.

Feeds are produced by the Python code in [`jobs/`](jobs/) and refreshed on a
schedule by GitHub Actions ([`.github/workflows/generate-feeds.yml`](.github/workflows/generate-feeds.yml)),
which commits the updated XML back into this repo. Subscribers consume the files
directly over `raw.githubusercontent.com`.

## Feeds generated

All feeds live under [`scmt/`](scmt/) and are Atom 1.0 XML. Base URL:

```text
https://raw.githubusercontent.com/ajmaradiaga/feeds/main/scmt/
```

| Feed | Path | Contents | Refresh |
| --- | --- | --- | --- |
| **Topic — blog posts** | `topics/<Topic>-blog-posts.xml` | Latest blog posts for a topic | Priority topics every 3h; the long tail twice daily |
| **Topic — Q&A** | `topics/<Topic>-qa.xml` | Latest Q&A for a topic | same as above |
| **Member** | `members/<group>/<username>.xml` | A member's latest posts (max 20) | Developer advocates every 12h; mentors & champions daily |
| **All replies** | `all_replies.xml` | Recent replies across the whole community | Hourly |

- **Topics** are defined in [`jobs/config.py`](jobs/config.py) as `PRIORITY_TOPICS`
  (every 3h) and `DAILY_TOPICS` (twice daily). Filenames derive from the topic
  name (spaces → `-`, commas/slashes stripped, parentheses kept), e.g.
  `SAP-Fiori-blog-posts.xml`, `FIN-(Finance)-qa.xml`.
- **Members** are grouped into `developer-advocates`, `sap-mentors`,
  `sap-champions`, and `sap-community-members` (also in `jobs/config.py`).
  Filenames use the SAP Community username and preserve case, e.g.
  `members/developer-advocates/qmacro.xml`.
- Browse the full lists: [topics](scmt/topics/README.md) ·
  [members](scmt/members/README.md). The Markdown tables can be regenerated with
  the `markdown` job (see below) — output lands in `jobs/markdown/`.

> ⚠️ Paths, filenames, the `main` branch, and the `scmt/` prefix are the public
> contract. Changing any of them breaks existing subscribers.

## Testing locally

Requires Python 3.12+.

```bash
# 1. Create a virtual environment and install the pinned dependencies
python3 -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt

# 2. Run a job. By default feeds are written into ./scmt (the real tree),
#    so point FEEDS_OUTPUT_ROOT at a scratch dir to avoid touching tracked files.
FEEDS_OUTPUT_ROOT=/tmp/feeds-test/scmt python -m jobs.generate --job topics-priority

# 3. Inspect the output
ls /tmp/feeds-test/scmt/topics/
```

Available `--job` values:

| Job | What it generates |
| --- | --- |
| `replies` | `scmt/all_replies.xml` |
| `topics-priority` | blog + Q&A feeds for `PRIORITY_TOPICS` |
| `topics-daily` | blog + Q&A feeds for `DAILY_TOPICS` |
| `members-advocates` | `scmt/members/developer-advocates/*.xml` |
| `members-champions` | `scmt/members/sap-champions/*.xml` |
| `members-mentors` | `scmt/members/sap-mentors/*.xml` |
| `members-community` | `scmt/members/sap-community-members/*.xml` |
| `markdown` | Regenerates the topic/member tables into `jobs/markdown/` |

Tips:

- `markdown` makes no network calls — handy for a quick smoke test.
- To verify a change is non-breaking, generate into a scratch dir and diff a
  known feed against the committed one; only `<updated>` and entry content
  should differ:

  ```bash
  FEEDS_OUTPUT_ROOT=/tmp/feeds-test/scmt python -m jobs.generate --job topics-priority
  diff /tmp/feeds-test/scmt/topics/SAP-Fiori-blog-posts.xml scmt/topics/SAP-Fiori-blog-posts.xml
  ```

## Scheduling (production)

GitHub Actions runs each job on a cron schedule (UTC) and commits any changed
XML. You can also trigger a single job manually from the **Actions → Generate
feeds → Run workflow** menu (choose the job from the dropdown). See
[`.github/workflows/generate-feeds.yml`](.github/workflows/generate-feeds.yml).

## Adding a topic (pull request)

Topics are defined in [`jobs/config.py`](jobs/config.py). A topic is a
`'<Topic name>': '<Managed Tag GUID>'` entry in one of two dicts:

- **`PRIORITY_TOPICS`** — refreshed every 3 hours. Use for high-traffic topics.
- **`DAILY_TOPICS`** — refreshed twice daily. Use for the long tail.

Each entry produces two feeds automatically: `topics/<Topic>-blog-posts.xml` and
`topics/<Topic>-qa.xml`.

### Steps

1. **Find the Managed Tag GUID** for the topic. The GUID is the `products.id`
   used by the SAP Community search API. The helper scripts in
   [`scmt/products-processing/`](scmt/products-processing/) (e.g.
   `managed-tags.py`, `get-products.py`, and `sample-requests.http`) dump and
   search the available tags/products to locate it.
2. **Add the entry** to the right dict in `jobs/config.py`, keeping the existing
   alphabetical-ish ordering, for example:

   ```python
   PRIORITY_TOPICS = {
       ...
       'SAP Integration Suite': '73554900100800003241',
   }
   ```

   The feed filename is derived from the name (spaces → `-`, commas/slashes
   stripped, parentheses kept), so `SAP Integration Suite` →
   `SAP-Integration-Suite-blog-posts.xml`.
3. **(Optional) Regenerate the Markdown tables** so the docs stay in sync:

   ```bash
   python -m jobs.generate --job markdown
   ```

4. **Smoke-test locally** against a scratch dir (see *Testing locally*) to
   confirm the GUID returns results:

   ```bash
   FEEDS_OUTPUT_ROOT=/tmp/feeds-test/scmt python -m jobs.generate --job topics-priority
   ```

5. **Open a pull request** with the `jobs/config.py` change. You do **not** need
   to commit the generated XML — the scheduled workflow creates it on the next
   run after the PR is merged.

> Prefer not to edit code? Open a
> [New topic suggestion issue](.github/ISSUE_TEMPLATE/new-topic.yml) with the
> topic name and URL instead.
