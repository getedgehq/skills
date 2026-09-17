# Action Checklist - Stop the Bleeding & Save $577/Year

## Phase 1: Stop the Bleeding (TODAY - Before Month End)
**Time: 30 minutes | Savings: $37/month**

- [ ] **Review the analysis**
  - [ ] Read `output/EXECUTIVE_SUMMARY.md`
  - [ ] Run `python output/cost_comparison.py` to see the numbers
  - [ ] Review `output/trace_example.md` to understand the mechanism

- [ ] **Apply harness fixes**
  ```bash
  cd /home/user/work
  cp output/fixed_agent_code/*.py agent/
  ```

- [ ] **Test manually (2-3 leads)**
  ```bash
  # Enable draft mode so you don't send real emails during testing
  export EMAIL_DRAFT_MODE=true
  
  # Test with a known lead from logs
  python -c "from agent.loop import run_conversation; print(run_conversation('L-4440'))"
  ```

- [ ] **Verify fixes in logs**
  - [ ] Check conversations finish in 3-4 turns (not 16+)
  - [ ] Check no repeated `crm_get_account` calls
  - [ ] Check total cost per lead < $0.30
  - [ ] Check no 422 retry loops

- [ ] **Deploy to production**
  - [ ] Commit fixed code
  - [ ] Run next batch (monitor logs closely)
  - [ ] Verify cost drops to ~$0.50/day

**Expected result:** Sept 16-30 costs drop from $26 to ~$8 (70% reduction)

---

## Phase 2: Build Golden Set (Week of Sept 16)
**Time: 2-3 hours | Prevents future incidents**

- [ ] **Expand golden_starter.jsonl to 20+ cases**
  - [ ] 5 normal qualified leads (score 50-100, email sent)
  - [ ] 5 unqualified leads (score 0-49, no email)
  - [ ] 3 edge cases (missing data, timeout, merged accounts)
  - [ ] 2 high-score but no email address
  - [ ] 5 regression cases from incidents (the 5 leads that burned $18.77)

- [ ] **Document expected outcomes for each case**
  ```json
  {
    "case_id": "golden-004",
    "description": "High score lead with complete data",
    "lead_id": "L-...",
    "expected_outcome": {
      "score_range": [80, 90],
      "email_sent": true,
      "turns": [3, 4],
      "cost_max": 0.30
    },
    "source": "typical_qualified_lead"
  }
  ```

- [ ] **Test the eval script**
  ```bash
  python output/run_eval.py
  ```
  Should show 100% pass with fixed code

---

## Phase 3: Switch to Haiku (Week of Sept 23)
**Time: 1 hour | Additional savings: $11/month**

- [ ] **Run baseline eval with Sonnet**
  ```bash
  python output/run_eval.py > results_sonnet.txt
  ```

- [ ] **Switch to Haiku**
  ```bash
  cp output/config_haiku.json config.json
  # Or manually edit config.json:
  # - model: "claude-haiku-4-5"
  # - price_per_mtok_in: 1.0
  # - price_per_mtok_out: 5.0
  ```

- [ ] **Run eval with Haiku**
  ```bash
  python output/run_eval.py > results_haiku.txt
  ```

- [ ] **Compare results**
  ```bash
  diff results_sonnet.txt results_haiku.txt
  ```
  - [ ] Check pass rates are equivalent
  - [ ] Review any quality differences
  - [ ] Check email bodies still sound good

- [ ] **Deploy if quality is good**
  - [ ] Run 5-10 leads in production
  - [ ] Spot-check email quality manually
  - [ ] Monitor logs for issues
  - [ ] If all good after 24hrs → done!

**Expected result:** Monthly cost drops from $16 to $5 (67% additional reduction)

---

## Phase 4: Ongoing Discipline
**Time: 15 min per change | Prevents regressions**

- [ ] **Make evaluation mandatory before shipping**
  - [ ] Add to PR checklist: "Golden set eval passed"
  - [ ] Block deploys without eval results
  - [ ] Review failures before merging prompt changes

- [ ] **Add monitoring alerts**
  - [ ] Alert if any conversation exceeds 6 turns
  - [ ] Alert if daily cost > $1.00
  - [ ] Alert if any lead costs > $0.50

- [ ] **Monthly review**
  - [ ] Check cost trends
  - [ ] Add new test cases for any incidents
  - [ ] Update golden set with real traffic patterns

---

## Success Criteria

### After Phase 1 (Fixes)
✅ No conversations exceed 6 turns  
✅ No 422 retry loops in logs  
✅ Daily cost < $0.60 (vs $1.80 current)  
✅ Average cost per lead ~$0.17  

### After Phase 3 (Haiku)
✅ Email quality maintained (spot-check 10 examples)  
✅ Daily cost < $0.20  
✅ Annual savings: $577 vs current trajectory  

### Ongoing
✅ Zero production incidents from prompt changes  
✅ Every change validated by golden set  
✅ Costs stable and predictable  

---

## Rollback Plan

If something breaks after Phase 1 fixes:
```bash
cd /home/user/work
git checkout agent/loop.py agent/prompts.py agent/tools.py
# But: investigate WHY it broke - the fixes are solid
```

If Haiku quality is bad (Phase 3):
```bash
# Edit config.json back to Sonnet:
{
  "model": "claude-sonnet-4-5",
  "price_per_mtok_in": 3.0,
  "price_per_mtok_out": 15.0
}
# You still keep the $37/mo savings from Phase 1
```

---

## Questions During Implementation?

**Logs show a different error:**
- Check `output/trace_example.md` for pattern matching
- Verify field names match `crm_schema.json`
- If 4xx: should fail fast, not retry
- If 5xx: retry is OK (transient)

**Eval script failing:**
- Check test cases have valid lead IDs
- Verify fixed code is in `agent/` directory
- Run with `python -v` for debug output

**Cost not dropping as expected:**
- Check no new retry patterns emerged
- Verify MAX_TURNS circuit breaker is active
- Review logs for >4 turn conversations

**Haiku email quality concerns:**
- Run side-by-side comparison (10 leads each)
- Review with sales team
- Consider prompt tuning before model switch
- Keep Sonnet if quality drop is real

---

## Files You Need

```
output/
├── EXECUTIVE_SUMMARY.md     ← Read this first
├── README.md                ← Quick start guide
├── cost_analysis.md         ← Full analysis
├── trace_example.md         ← How the bug works
├── cost_comparison.py       ← Run for numbers
├── fixed_agent_code/
│   ├── loop.py             ← Copy to agent/
│   ├── prompts.py          ← Copy to agent/
│   └── tools.py            ← Copy to agent/
├── run_eval.py             ← Golden set runner
├── golden_starter.jsonl    ← Expand to 20+ cases
└── config_haiku.json       ← For Phase 3
```

**Start here:** Read EXECUTIVE_SUMMARY.md, then run cost_comparison.py, then copy the fixed code.
