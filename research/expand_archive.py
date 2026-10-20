import collections,datetime,json,pathlib,re,sqlite3
from lxml import html
OUT=pathlib.Path(__file__).resolve().parent; ROOT=OUT.parent
c=sqlite3.connect(OUT/'archive.sqlite3');c.row_factory=sqlite3.Row
base={r['id']:dict(r) for r in c.execute('SELECT * FROM posts')}
posts={}; appearances=[]; errors=[]; conflicts=[]
def field(a,cls):
 x=a.xpath('.//*[contains(concat(" ",normalize-space(@class)," ")," '+cls+' ")]');return x[0] if x else None
def plain(e):
 if e is None:return ''
 for br in e.xpath('.//br'):br.tail='\n'+(br.tail or '')
 return e.text_content().strip()
for path in sorted((ROOT/'ronbronson/status').glob('*/index.html')):
 doc=html.fromstring(path.read_bytes()); pageid=path.parent.name
 articles=doc.xpath('//article');main=0
 for i,a in enumerate(articles):
  link=field(a,'permalink');m=re.search(r'(\d+)',link.get('href','')) if link is not None else None
  if not m:errors.append([str(path),'no permalink']);continue
  id=m.group(1); role='main' if a.get('id')=='main' else ('parent' if 'parent' in a.get('class','').split() else 'child')
  if role=='main':main+=1
  e=field(a,'full_text'); raw=html.tostring(e,encoding='unicode') if e is not None else '';text=plain(e)
  date_display=plain(field(a,'created_at'));author=plain(field(a,'user_name'))
  if id in base:date=base[id]['date'];date_basis='searchDocuments.created_at'
  elif int(id)>=29700859247:
   date=datetime.datetime.fromtimestamp(((int(id)>>22)+1288834974657)/1000,datetime.timezone.utc).isoformat();date_basis='snowflake ID timestamp'
  else:date=None;date_basis='archive display only; timezone unspecified'
  def count(cls):
   s=plain(field(a,cls));m=re.search(r'\d+',s);return int(m.group()) if m else None
  r=dict(id=id,date=date,text=text,html=raw,favorites=count('favorite_count'),retweets=count('retweet_count'),source_url=f'https://twitter.com/{author.lstrip("@")}/status/{id}',archive_path=str(pathlib.Path('ronbronson/status')/id/'index.html'),author=author,date_display=date_display,date_basis=date_basis,in_search_index=id in base)
  if id in posts and posts[id]['text']!=text:conflicts.append(id)
  if id not in posts or role=='main':posts[id]=r
  appearances.append(dict(page_id=pageid,post_id=id,role=role,position=i))
 if main!=1:errors.append([str(path),f'main count {main}'])
assert not errors,errors[:10]
# Preserve canonical main-page text and report differing thread renderings.
assert set(base)<=set(posts)
c.execute('DROP TABLE IF EXISTS all_posts');c.execute('DROP TABLE IF EXISTS all_posts_fts');c.execute('DROP TABLE IF EXISTS appearances')
c.execute('CREATE TABLE all_posts(id TEXT PRIMARY KEY,date TEXT,text TEXT,html TEXT,favorites INTEGER,retweets INTEGER,source_url TEXT,archive_path TEXT,author TEXT,date_display TEXT,date_basis TEXT,in_search_index INTEGER)')
c.execute('CREATE VIRTUAL TABLE all_posts_fts USING fts5(id UNINDEXED,text)')
c.execute('CREATE TABLE appearances(page_id TEXT,post_id TEXT,role TEXT,position INTEGER)')
for r in posts.values():c.execute('INSERT INTO all_posts VALUES(?,?,?,?,?,?,?,?,?,?,?,?)',tuple(r.values()));c.execute('INSERT INTO all_posts_fts VALUES(?,?)',(r['id'],r['text']))
c.executemany('INSERT INTO appearances VALUES(:page_id,:post_id,:role,:position)',appearances);c.commit()
with (OUT/'all-posts.jsonl').open('w') as f:
 for r in sorted(posts.values(),key=lambda r:(r['date'] or '',r['id'])):f.write(json.dumps(r,ensure_ascii=False)+'\n')
report=dict(unique_posts=len(posts),original_index=len(base),added=len(set(posts)-set(base)),article_appearances=len(appearances),authors=dict(collections.Counter(r['author'] for r in posts.values())),roles=dict(collections.Counter(r['role'] for r in appearances)),date_basis=dict(collections.Counter(r['date_basis'] for r in posts.values())),errors=errors,text_conflicts=sorted(set(conflicts)))
(OUT/'coverage.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
