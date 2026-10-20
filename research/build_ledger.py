import csv,datetime,json,pathlib,sqlite3
from zoneinfo import ZoneInfo
O=pathlib.Path(__file__).resolve().parent;c=sqlite3.connect(O/'archive.sqlite3');c.row_factory=sqlite3.Row
selection={
'Consequence Design':{
'1175215272526876673':'Explicitly seeks a broader framing beyond hostile patterns. Parent posts concern deceptive subscription and insurance interfaces.',
'1288540346444476417':'A practical starting question: interrogate the assumptions inside an ideal state. Archive links it to the later Consequence Frame posts.',
'1296506516267307009':'Explains the speculative dimension and reframes edge cases as people on the margins. Parent of the policy-book post.',
'1291735713487044608':'Describes an early collaborative exercise. Do not present the prototype as a finalized method.',
'1331275523608088576':'Direct articulation of Consequence Design as a stance and a policy project. Particularly strong for a project history or introduction.',
'1328862395138072577':'Locates harm beyond UI/content and resists multiplying terminology. Useful qualification to a method-focused account.'},
'Burden, recourse, and service failure':{
'966179303514951681':'Distinguishes brand voice from policy and frontline responsibility. Useful early evidence of the later burden-shifting argument.',
'1479181499689627649':'Frames digital interactions as a way companies can evade responsibility; parent of the user-frustration and trust posts.',
'1479204259908390914':'Names a memorable mechanism: dead-end feedback can drive users to give up. Cite as an argument, not an empirically proven universal law.',
'1480007119466229765':'Links the service-failure thread to a longer essay about trust. Recover and read that essay before borrowing its argument.',
'1480007121072582656':'Identifies frontline workers as another party absorbing system failure. Explicitly marks an unwritten follow-up.',
'1536812787132837888':'Extends the argument to municipal rules and burdens. Its archive shows the April consequence-design/service-design posts as parents.'},
'Access and participation':{
'991147063143534592':'Cashless restaurants expose tension between personal convenience and public access.',
'1315355489237041152':'Argues that service consequences vary by audience and point of access. Child posts give concrete unequal-treatment examples.',
'1485997523105988620':'Says technical mechanisms cannot by themselves undo intentional exclusion. Parent explicitly rejects web3 as a solution to service-design problems.',
'1517575431368568832':'A firsthand observation about meeting schedules and who can participate. Avoid claiming it proves the composition of all public hearings.'},
'Discovery and sustaining communities':{
'1345144260429955072':'Treats hashtags as an inherited workaround rather than a satisfactory discovery design.',
'1361064187921768448':'Challenges products that require users to import an existing social network. Archive includes Peach and Rdio follow-ups.',
'1364387982459867136':'Coins bycatch discovery for advertising closed-app activity on Twitter. Preserve the specific meaning.',
'1361067242436186115':'Connects the argument to a 2017 essay and Rdio. A bridge to longer writing rather than a standalone definition.',
'1475858156584583169':'Names moderation as a condition of sustainable communities, informed by forum participation/leadership.',
'1477279567811256325':'Warns that active platform users may not represent the actual constituency.'},
'Place, belonging, and professional opportunity':{
'676881438722031616':'Links an essay challenging cheapness as the main pitch for small cities.',
'1073108148154585088':'Shifts from attracting residents to giving them participation and reasons to remain.',
'1073118363302354944':'Confirmed child of the preceding small-cities post; adds social connection and use of residents’ expertise.',
'996077053303820291':'Defines welcome through treatment of outsiders and whether newcomers return.',
'854680062712479745':'Part of a mentorship thread that distinguishes advice from support and protection. The parent sharing HBR is another author’s title.',
'854684935243915264':'The thread’s practical leadership claim: being a firewall. Useful alongside, not detached from, the mentorship critique.',
'901065540176883713':'Memorable critique of advice without jobs. Use as supporting rhetoric, with the mentorship thread supplying substance.'},
'Sport as a design practice':{
'1081716569640583168':'Reflects on tactical infractions: people can rationally exploit rules. The link to institutional incentives is an editorial synthesis.',
'1196655184467779584':'Explicitly distinguishes sport design from board/video games through rule fluidity over time.',
'1488668110517194755':'Prioritizes playtesting over premature monetization. Parent posts discuss barriers to new sports gaining adoption.'}}
records=[];md=['# Citation ledger\n','Selected passages with archive context. Dates below use America/Los_Angeles; exact UTC timestamps remain in the database. Quotes reproduce parsed archive text, with HTML decoded and line breaks preserved. Editorial notes are interpretation. Linked external articles, images, and quoted tweets have not been independently reviewed. Parent/child labels describe the archive presentation, not a reconstructed reply API.\n']
for theme,items in selection.items():
 md+=['## '+theme+'\n']
 for id,note in items.items():
  r=dict(c.execute('SELECT * FROM all_posts WHERE id=?',(id,)).fetchone());assert not r['text'].startswith('RT @')
  context=[dict(x) for x in c.execute('SELECT a.role,p.id,p.text,p.source_url FROM appearances a JOIN all_posts p ON p.id=a.post_id WHERE a.page_id=? ORDER BY position',(id,))]
  r.update(theme=theme,editorial_note=note,archive_context=context,review_status='text and archived context reviewed; external/media context unverified')
  local=datetime.datetime.fromisoformat(r['date']).astimezone(ZoneInfo('America/Los_Angeles')).strftime('%Y-%m-%d')
  records.append(r);md += [f'### {local} · {id}\n', '\n'.join(('> '+s).rstrip() for s in r['text'].splitlines())+'\n',f'[Original]({r["source_url"]}) · [Archived page](../{r["archive_path"]})\n',note+'\n']
  others=[x for x in context if x['role']!='main']
  if others:md+=['Archived context: '+', '.join(f'{x["role"]} [{x["id"]}](../ronbronson/status/{x["id"]}/index.html)' for x in others)+'.\n']
(O/'citation-ledger.md').write_text('\n'.join(md))
with (O/'citation-ledger.jsonl').open('w') as f:
 for r in records:f.write(json.dumps(r,ensure_ascii=False)+'\n')
with (O/'citation-ledger.csv').open('w',newline='') as f:
 keys=['theme','id','date','text','source_url','archive_path','editorial_note','review_status'];w=csv.DictWriter(f,fieldnames=keys,extrasaction='ignore',lineterminator='\n');w.writeheader();w.writerows(records)
print('Ledger entries:',len(records))
