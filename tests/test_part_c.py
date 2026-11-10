"""Focused regression tests for the Part C agent."""
import tempfile,unittest
from pathlib import Path
from agent.run_agent import Agent
from agent.understand import understand

ROOT=Path(__file__).resolve().parents[1]
class PartCTests(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory(); self.log=str(Path(self.tmp.name)/'runs.jsonl')
  self.agent=Agent(str(ROOT/'data'),self.log)
 def tearDown(self): self.tmp.cleanup()
 def test_alias_and_lowest(self):
  self.assertEqual(understand('Bangalore revenue on 2026-04-01')['store'],'Bengaluru')
  self.assertEqual(understand('Which store has the lowest revenue?')['intent'],'comparison')
 def test_ambiguous_lookup_clarifies(self): self.assertEqual(self.agent.handle('What was the revenue?')['status'],'Clarification Needed')
 def test_prohibited_metric_rejected_before_query(self):
  r=self.agent.handle('Show marketing_spend_inr for Pune'); self.assertEqual(r['status'],'Safe Failure'); self.assertEqual(r['attempt_count'],0)
 def test_comparison_lowest(self):
  r=self.agent.handle('Which store had the lowest average revenue?'); self.assertEqual(r['status'],'Answered'); self.assertIn('Lowest: Pune',r['answer_text'])
 def test_weather_part_d_boundary(self): self.assertIn('Part D',self.agent.handle('What was the weather in Pune?')['answer_text'])
 def test_diagnostic_non_causal(self):
  r=self.agent.handle('Why is Pune performing poorly?'); self.assertEqual(r['status'],'Answered'); self.assertIn('does not establish',r['answer_text'])
 def test_inventory_snapshot_disclosed(self): self.assertIn('undated',self.agent.handle('Which products are below reorder threshold?')['answer_text'])
 def test_feedback_missing_values(self): self.assertIn('excluded',self.agent.handle('Summarize customer feedback for Pune')['answer_text'])
if __name__=='__main__': unittest.main()
