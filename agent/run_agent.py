"""Grounded read-only analytics agent. Run from repository root: python -m agent.run_agent."""
import json,time,uuid
from pathlib import Path
from .understand import understand,STORES
from .fetch import connect,safe_query,fetch_one,fetch_target,APPROVED,ValidationError,DataAccessError
from .answer import money,lookup,target

class Agent:
 def __init__(self,data_dir='data',log_path='logs/runs.jsonl'):
  self.con=connect(data_dir); self.sessions={}; self.log_path=Path(log_path); self.log_path.parent.mkdir(parents=True,exist_ok=True)
 def handle(self,question,session_id='default',simulate_failures=0):
  started=time.perf_counter(); context=self.sessions.setdefault(session_id,{ }); p=understand(question,context); intent=p['intent']
  status='Answered'; answer=''; values={}; evidence=[]; attempts=0; error=None; route='python'
  if intent=='unsupported_metric': status='Safe Failure'; answer='Requested metric is prohibited or unapproved. No data query was run.'
  elif intent=='out_of_scope': status='Escalated'; answer='This request is outside the read-only store analytics scope.'
  elif intent=='weather': status='Safe Failure'; answer='Weather data is not available in Part C; it belongs to Part D. No weather claim was made.'
  elif p['date_error']: status='Clarification Needed'; answer=p['date_error']
  elif p['required_entities'] or p['confidence']<0.70:
   status='Clarification Needed'; answer='Please clarify: '+', '.join(p['required_entities'] or ['the store, metric or date'])+'. Supported stores: '+', '.join(STORES)+'.'
  else:
   try:
    if p['store']: context['store']=p['store']
    if p['metric']: context['metric']=p['metric']
    if p['date']: context['date']=p['date']
    if intent=='lookup':
     if p['metric'] not in APPROVED['store_daily']: status='Safe Failure'; answer='This metric is not approved for daily store data.'
     else:
      value,attempts=fetch_one(self.con,p['store'],p['date'],p['metric'],simulate_failures)
      status,answer,values,evidence=lookup(value,p,'store_daily_clean.csv')
    elif intent=='target_vs_actual':
     data,attempts=fetch_target(self.con,p['store'],p['date'],simulate_failures); status,answer,values,evidence=target(data,p)
    elif intent=='comparison':
     route='sql'; metric=p['metric'] or 'revenue_inr'
     if metric not in APPROVED['store_daily']: raise ValidationError('Comparison metric is not approved.')
     where=''; params=[]
     if p['date']: where=' WHERE date=?'; params=[p['date']]
     elif p['date_range']: where=' WHERE date BETWEEN ? AND ?'; params=list(p['date_range'])
     df=safe_query(self.con,'SELECT store, AVG("'+metric+'") AS metric_value FROM store_daily'+where+' GROUP BY store ORDER BY metric_value',params,'store_daily',['store',metric])
     if df.empty: status='Safe Failure'; answer='No records matched the comparison.'
     else:
      rows=['{}: {:.2f}'.format(r['store'],float(r['metric_value'])) for _,r in df.iterrows()]
      answer='Average {} by store: {}.'.format(metric.replace('_',' '),'; '.join(rows))
      if 'lowest' in question.lower() or 'least' in question.lower(): answer+=' Lowest: {} ({:.2f}).'.format(df.iloc[0]['store'],float(df.iloc[0]['metric_value']))
      elif 'highest' in question.lower() or 'most' in question.lower(): answer+=' Highest: {} ({:.2f}).'.format(df.iloc[-1]['store'],float(df.iloc[-1]['metric_value']))
      values={str(r['store']):float(r['metric_value']) for _,r in df.iterrows()}; evidence=[{'source':'store_daily_clean.csv','fields':['store',metric],'aggregation':'average by store'}]; attempts=1
    elif intent=='inventory':
     route='sql'; sql='SELECT store,product,stock_units,reorder_threshold FROM inventory WHERE stock_units<reorder_threshold'; params=[]
     if p['product']: sql+=' AND product LIKE ?'; params=['%'+p['product'].split()[0]+'%']
     df=safe_query(self.con,sql+' ORDER BY (reorder_threshold-stock_units) DESC',params,'inventory',['store','product','stock_units','reorder_threshold'])
     answer='Below-threshold inventory snapshot: '+('; '.join('{} — {}: {} units (threshold {})'.format(r['store'],r['product'],int(r['stock_units']),int(r['reorder_threshold'])) for _,r in df.iterrows()) if not df.empty else 'no matching records')+'. Inventory is undated; this is not historical stock data.'
     values=df.to_dict(orient='records'); evidence=[{'source':'inventory.csv','fields':['store','product','stock_units','reorder_threshold']}]; attempts=1
    elif intent=='feedback':
     route='sql'; store=p['store']; where=' WHERE store=?' if store else ''; params=[store] if store else []
     agg=safe_query(self.con,'SELECT AVG(rating) avg_rating,COUNT(rating) rated_count,COUNT(*) total_count FROM feedback'+where,params,'feedback',['rating','store']).iloc[0]
     themes=safe_query(self.con,'SELECT theme,COUNT(*) n FROM feedback'+where+' GROUP BY theme ORDER BY n DESC LIMIT 5',params,'feedback',['theme','store'])
     avg='not available' if agg['avg_rating'] is None else '{:.2f}'.format(float(agg['avg_rating']))
     answer='Feedback for {}: average rating {}; {} rated records of {}. Frequent themes: {}. Missing ratings are excluded, not treated as zero.'.format(store or 'all stores',avg,int(agg['rated_count']),int(agg['total_count']),', '.join('{} ({})'.format(r['theme'],int(r['n'])) for _,r in themes.iterrows()))
     values={'average_rating':avg,'rated_count':int(agg['rated_count']),'total_count':int(agg['total_count'])}; evidence=[{'source':'feedback.csv','fields':['rating','theme']}]; attempts=1
    elif intent=='diagnostic':
     route='multi_dataset'
     daily=safe_query(self.con,'SELECT store,AVG(revenue_inr) revenue,AVG(daily_target_inr) target,AVG(footfall) footfall,AVG(stockout_hours) stockout,AVG(discount_pct) discount,AVG(achievement_pct) achievement FROM store_daily GROUP BY store ORDER BY revenue',[],'store_daily',['store','revenue_inr','daily_target_inr','footfall','stockout_hours','discount_pct','achievement_pct'])
     inv=safe_query(self.con,'SELECT store,SUM(CASE WHEN stock_units<reorder_threshold THEN 1 ELSE 0 END) below_count,COUNT(*) n FROM inventory GROUP BY store',[],'inventory',['store','stock_units','reorder_threshold'])
     fb=safe_query(self.con,'SELECT store,AVG(rating) rating,COUNT(rating) rated,COUNT(*) n FROM feedback GROUP BY store',[],'feedback',['store','rating'])
     rows=[]
     for _,r in daily.iterrows():
      i=inv[inv.store==r.store].iloc[0]; f=fb[fb.store==r.store].iloc[0]
      rows.append({'store':r.store,'avg_revenue':float(r.revenue),'avg_target':float(r.target),'avg_footfall':float(r.footfall),'avg_stockout_hours':float(r.stockout),'avg_discount_pct':float(r.discount),'avg_achievement_pct':float(r.achievement),'below_threshold_records':int(i.below_count),'inventory_records':int(i.n),'avg_rating':None if f.rating is None else float(f.rating),'rated_feedback':int(f.rated),'feedback_records':int(f.n)})
     pune=next(r for r in rows if r['store']=='Pune'); rank=1+next(i for i,r in enumerate(rows) if r['store']=='Pune')
     rating='not available' if pune['avg_rating'] is None else '{:.2f}'.format(pune['avg_rating'])
     answer='Pune diagnosis over the full available daily period: average revenue {}; rank {} of 5 (lowest to highest); average footfall {:.1f}; average stockout hours {:.2f}; average target achievement {:.2f}%; inventory records below threshold {}/{} (undated snapshot); average customer rating {} from {} rated feedback records. These are descriptive signals only; co-occurrence does not establish that stockouts caused lower revenue.'.format(money(pune['avg_revenue']),rank,pune['avg_footfall'],pune['avg_stockout_hours'],pune['avg_achievement_pct'],pune['below_threshold_records'],pune['inventory_records'],rating,pune['rated_feedback'])
     values={'store_diagnostics':rows}; evidence=[{'source':'store_daily_clean.csv','fields':['revenue_inr','daily_target_inr','footfall','stockout_hours','discount_pct','achievement_pct']},{'source':'inventory.csv','fields':['stock_units','reorder_threshold'],'note':'undated snapshot'},{'source':'feedback.csv','fields':['rating']}]; attempts=1
    else: status='Safe Failure'; answer='Unsupported request type.'
   except (ValidationError,ValueError) as exc: status='Safe Failure'; error=str(exc); answer='Data validation failed; no unapproved metric was queried.'
   except (DataAccessError,FileNotFoundError,OSError) as exc: status='Escalated'; error=str(exc); answer='A data access failure prevented a reliable answer.'; attempts=min(max(attempts,1),3)
  record={'timestamp':time.strftime('%Y-%m-%dT%H:%M:%S'),'request_id':str(uuid.uuid4()),'question':question,'intent':intent,'confidence':p['confidence'],'route':route,'dataset':evidence,'approved_metrics':p['metric'],'filters':{'store':p['store'],'date':p['date'],'date_range':p['date_range'],'product':p['product']},'attempt_count':attempts,'validation':'passed' if status=='Answered' else 'not_run_or_not_passed','grounded_values':values,'status':status,'answer_text':answer,'error_or_limitations':error,'latency_ms':round((time.perf_counter()-started)*1000,2)}
  with self.log_path.open('a',encoding='utf-8') as f: f.write(json.dumps(record,ensure_ascii=False,default=str)+'\n')
  return record

if __name__=='__main__':
 agent=Agent(); print('DMart practice-data assistant. Type exit to stop.')
 while True:
  q=input('You: ').strip()
  if q.lower() in ('exit','quit'): break
  r=agent.handle(q); print(r['status']+': '+r['answer_text'])
