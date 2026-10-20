# Twitter archive research

Start with the [ideas map](ideas-map.md) and [citation ledger](citation-ledger.md). The ledger contains 32 selected posts with dates, exact text, source links, archived context, and editorial notes. Portable versions are [CSV](citation-ledger.csv) and [JSONL](citation-ledger.jsonl).

The full archive contains 20,684 unique posts: 18,114 non-retweet entries and 2,570 retweets. Search excludes retweets by default. Non-retweet entries can still quote other writers; review attribution before reuse. The archive omits some replies and is not a complete conversation history. See [coverage.json](coverage.json) and the ideas map for extraction limitations.

## Rebuild and search

Requires Python 3.9 or newer with SQLite FTS5, timezone data, and `lxml`. From the repository root:

```sh
python3 -m venv research/.venv
research/.venv/bin/python -m pip install -r research/requirements.txt
research/.venv/bin/python research/index_archive.py
research/.venv/bin/python research/expand_archive.py
research/.venv/bin/python research/build_ledger.py
research/.venv/bin/python research/search.py '"service design"' --context --limit 20
```

If your Python environment already supplies these prerequisites, use `python3` for the commands. Script paths are resolved relative to the scripts, so execution does not depend on the working directory. Rebuilding replaces generated research indexes and exports; it does not edit archive source pages.

Queries support SQLite FTS5 phrases, AND, OR, NOT, and prefix terms such as `design*`. Use `--include-retweets` to include shared posts and `--context` for archived parent/child appearances. Results are ranked by text relevance, not editorial importance.

Generated `archive.sqlite3`, `posts.jsonl`, and `all-posts.jsonl` are ignored because they can be rebuilt from the archive. The database retains the original search data in `posts` and the complete archive in `all_posts`, with `appearances` preserving thread presentation without double-counting posts. Corpus and ledger `archive_path` fields are relative to the repository root; Markdown links are relative to their document.

The original static website remains usable independently of these research tools. The research does not change its browser search dataset.

## Editorial use

The ideas map is a selected thematic reading, not an exhaustive analysis of every post. Citation notes distinguish direct evidence from proposed connections. Before publication, review external articles, quoted tweets, images, and whether a historical statement still reflects your position. Retweets record sharing, not authorship or necessarily agreement.
