import argparse,json,sqlite3,pathlib
p=argparse.ArgumentParser(description='Search the complete archive with SQLite FTS5 query syntax; retweets excluded by default.')
p.add_argument('query');p.add_argument('--limit',type=int,default=20);p.add_argument('--include-retweets',action='store_true');p.add_argument('--context',action='store_true')
a=p.parse_args();c=sqlite3.connect(pathlib.Path(__file__).resolve().parent/'archive.sqlite3');c.row_factory=sqlite3.Row
where='' if a.include_retweets else " AND p.text NOT LIKE 'RT @%'"
for row in c.execute('SELECT p.* FROM all_posts p JOIN all_posts_fts f ON p.id=f.id WHERE all_posts_fts MATCH ?'+where+' ORDER BY bm25(all_posts_fts),p.date LIMIT ?',(a.query,a.limit)):
 r=dict(row);r['content_kind']='retweet' if r['text'].startswith('RT @') else 'non-retweet; quotation attribution requires review'
 if a.context:r['context']=[dict(x) for x in c.execute('SELECT a.role,p.id,p.date,p.text,p.source_url FROM appearances a JOIN all_posts p ON p.id=a.post_id WHERE a.page_id=? ORDER BY a.position',(r['id'],))]
 print(json.dumps(r,ensure_ascii=False))
