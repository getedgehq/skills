## 🚨 URGENT ISSUE DISCOVERED: CRM Update Retry Loops

### Problem
5 conversations (11% of total) are stuck in endless retry loops, accounting for **70% of costs ($18.77 of $26.66)**.

### Root Cause
- Agent calls `crm_get_account` at every turn (per system prompt requirement)
- CRM update (`crm_update_contact`) is failing repeatedly
- Agent retries 15-17 times until hitting the 200K token context limit
- Each retry adds another massive CRM dump to context

### Example: Conversation cv_488aab (Lead L-3419)
```
Turn 1:  crm_get_account                      ✓
Turn 2:  crm_get_account, crm_update_contact  (fails, retries)
Turn 3:  crm_get_account, crm_update_contact  (fails, retries)
...
Turn 16: crm_get_account, crm_update_contact  (fails, retries)
Turn 17: ERROR: prompt is too long: 206,428 tokens > 200,000 maximum
```

**Cost:** $4.73 for ONE lead (vs avg $0.58)

### Impact
| Metric | Problem Convs | Normal Convs |
|--------|---------------|--------------|
| Count | 5 (11%) | 41 (89%) |
| Avg turns | 18.6 | 3.9 |
| Avg cost | $3.75 | $0.19 |
| Total cost | $18.77 (70%) | $7.89 (30%) |

### Solution Options

#### Immediate (Today):
1. **Switch to Haiku** - Reduces these problem conversations from $18.77 to $6.25
   - Still expensive but 67% cheaper
   - Buys time to fix the real issue
   
#### Short-term (This Week):
2. **Fix the CRM update failures**
   - Check CRM client logs at `logs/crm_client.log`
   - Likely schema validation or permission issues
   - Fix this and these conversations drop to ~$0.50 each
   
3. **Add max turn limit**
   - Modify `agent/loop.py` to bail after 8-10 turns
   - Prevents runaway costs from retry loops
   
#### Long-term (Q4):
4. **Optimize system prompt**
   - Don't call `crm_get_account` every turn
   - Cache CRM data per conversation
   - Could reduce ALL conversation tokens by 40-50%

### Cost Projection

**If we DON'T fix CRM retries:**
- Sept 1-15: $26.66 (5 problem convs)
- Rest of Sept (extrapolate): ~$27 more
- **September total: ~$54**

**If we switch to Haiku + fix CRM:**
- Problem convs fixed → ~$2.50 for 5 convs (vs $18.77)
- Normal convs on Haiku → ~$5 for 41 convs (vs $7.89)
- **September projected: ~$11-12** (78% savings vs current trajectory)

### Action Plan
1. ✅ **Deploy Haiku immediately** (config already updated in repo)
2. 🔍 **Investigate CRM failures** - Check logs/crm_client.log for error patterns
3. 🛡️ **Add turn limit** - Modify loop.py to prevent runaway costs
4. 📊 **Monitor** - Watch for similar patterns after deployment

---

### Files to Check
- `logs/crm_client.log` - CRM API errors
- `agent/loop.py` - Add max_turns=10 parameter
- `agent/prompts.py` - Consider removing "EVERY turn" requirement for crm_get_account
