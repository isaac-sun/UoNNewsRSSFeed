# UoNNewsRSSFeed

An unofficial RSS 2.0 feed for [University of Nottingham Current Students news](https://www.nottingham.ac.uk/currentstudents/news/news.aspx).

The university's student news page has no RSS feed. This project scrapes it, builds `feed.xml`, and publishes the file to GitHub Pages every hour using GitHub Actions.

## Subscribe

Add this URL to any RSS reader:

```text
https://isaac-sun.github.io/UoNNewsRSSFeed/feed.xml
```

## Run locally

Requires Python 3.9+.

```bash
pip install requests beautifulsoup4
python uon_news_rss.py
```

This writes `feed.xml` to the current directory.

### Options

| Flag         | Default    | Description                         |
| ------------ | ---------- | ----------------------------------- |
| `--category` | `all`      | News category to fetch (see below)  |
| `--pages`    | `1`        | Number of listing pages to scrape   |
| `--out`      | `feed.xml` | Output file path                    |

Example:

```bash
python uon_news_rss.py --category academic --pages 2 --out academic.xml
```

### Categories

`all`, `academic`, `events`, `opportunities`, `research`, `sport`, `celebrations`, `support`, `uniNews`, `other`

## How it works

1. [`uon_news_rss.py`](uon_news_rss.py) downloads the news listing page and finds every news card that contains a date.
2. It extracts each item's title, link, summary and publication date. The source page only gives a date, so every item's time is set to 09:00 UTC.
3. It writes the items as an RSS 2.0 document.

The workflow in [`.github/workflows/rss.yml`](.github/workflows/rss.yml) runs the script at 17 minutes past every hour and pushes the result to the `gh-pages` branch.

## Host your own copy

1. Fork this repository.
2. Go to **Actions** and enable workflows for the fork.
3. Run the **Build UoN news RSS** workflow once by hand (**Run workflow**). This creates the `gh-pages` branch.
4. Go to **Settings → Pages**, set **Source** to **Deploy from a branch**, and pick `gh-pages`.
5. Your feed will be at `https://<username>.github.io/<repo>/feed.xml`.

To publish a single category, change the run step in the workflow, for example:

```yaml
- run: mkdir -p public && python uon_news_rss.py --category events --out public/feed.xml
```

## Troubleshooting

If the script exits with `No news items found - the page layout may have changed.`, the university has probably changed the page's HTML. The scraping logic in `scrape()` will need updating.

## Disclaimer

This project is not affiliated with or endorsed by the University of Nottingham. All news content belongs to the university.
