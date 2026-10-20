import collections, datetime, html, json, pathlib, re, sqlite3
from html.parser import HTMLParser
out=pathlib.Path(__file__).resolve().parent
root=out.parent
class Plain(HTMLParser):
 def __init__(self): super().__init__(); self.parts=[]
 def handle_data(self,s): self.parts.append(s)
def clean(s):
 p=Plain(); p.feed(re.sub(r'<br\s*/?>','\n',s)); return ''.join(p.parts).strip()
s=(root/'searchDocuments.js').read_text(); docs=json.JSONDecoder().raw_decode(s[s.index('['):])[0]
conn=sqlite3.connect(out/'archive.sqlite3')
conn.execute('DROP TABLE IF EXISTS posts'); conn.execute('DROP TABLE IF EXISTS posts_fts')
conn.execute('CREATE TABLE posts(id TEXT PRIMARY KEY,date TEXT,text TEXT,html TEXT,favorites INTEGER,retweets INTEGER,source_url TEXT,archive_path TEXT)')
conn.execute("CREATE VIRTUAL TABLE posts_fts USING fts5(id UNINDEXED,text,tokenize='unicode61')")
records=[]
for d in docs:
 id=d['id_str']; dt=datetime.datetime.strptime(d['created_at'],'%a %b %d %H:%M:%S %z %Y').isoformat(); text=clean(d['full_text'])
 r=dict(id=id,date=dt,text=text,html=d['full_text'],favorites=int(d['favorite_count']),retweets=int(d['retweet_count']),source_url=f'https://twitter.com/ronbronson/status/{id}',archive_path=str(pathlib.Path('ronbronson/status')/id/'index.html'))
 records.append(r); conn.execute('INSERT INTO posts VALUES(?,?,?,?,?,?,?,?)',tuple(r.values())); conn.execute('INSERT INTO posts_fts VALUES(?,?)',(id,text))
conn.commit()
with (out/'posts.jsonl').open('w') as f:
 for r in records: f.write(json.dumps(r,ensure_ascii=False)+'\n')
print('Indexed',len(records),'records; unique IDs',len(set(r['id'] for r in records)))
print('Date range',min(r['date'] for r in records),max(r['date'] for r in records))
print('Missing local post pages',sum(not (root/r['archive_path']).exists() for r in records))
print('All archived post pages',sum(1 for x in (root/'ronbronson/status').glob('*/index.html')))
print('Search design:',conn.execute("SELECT count(*) FROM posts_fts WHERE posts_fts MATCH 'design'").fetchone()[0])
