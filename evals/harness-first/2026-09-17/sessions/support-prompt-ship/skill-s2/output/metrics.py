import json
from datetime import datetime

# Load all data
with open('tickets.jsonl') as f:
    tickets = {json.loads(line)['ticket_id']: json.loads(line) for line in f}

with open('outputs_old.jsonl') as f:
    old_outputs = {json.loads(line)['ticket_id']: json.loads(line)['reply'] for line in f}

with open('outputs_new.jsonl') as f:
    new_outputs = {json.loads(line)['ticket_id']: json.loads(line)['reply'] for line in f}

# Calculate metrics
metrics = {
    'old': {
        'total_chars': 0,
        'total_words': 0,
        'emoji_count': 0,
        'first_name_usage': 0,
        'apology_count': 0,
        'empathy_phrases': 0,
        'replies': []
    },
    'new': {
        'total_chars': 0,
        'total_words': 0,
        'emoji_count': 0,
        'first_name_usage': 0,
        'apology_count': 0,
        'empathy_phrases': 0,
        'replies': []
    }
}

empathy_words = ['sorry', 'understand', 'frustrat', 'disappoint', 'excited', 'exciting', 
                 'letdown', 'worry', 'care', 'apologize', 'apologise']

for ticket_id in sorted(tickets.keys()):
    ticket = tickets[ticket_id]
    customer_first_name = ticket['customer_name'].split()[0]
    
    for version, outputs in [('old', old_outputs), ('new', new_outputs)]:
        if ticket_id not in outputs:
            continue
        
        reply = outputs[ticket_id]
        m = metrics[version]
        
        m['total_chars'] += len(reply)
        m['total_words'] += len(reply.split())
        m['emoji_count'] += sum(1 for c in reply if ord(c) > 0x1F300)
        m['replies'].append(len(reply))
        
        reply_lower = reply.lower()
        
        # Check for first name usage (not just in greeting)
        if customer_first_name.lower() in reply_lower:
            m['first_name_usage'] += 1
        
        # Count empathy/apology phrases
        for word in empathy_words:
            if word in reply_lower:
                m['empathy_phrases'] += 1
                if 'sorry' in word or 'apolog' in word:
                    m['apology_count'] += 1
                break

# Print comparison
print("="*80)
print("QUANTITATIVE METRICS COMPARISON")
print("="*80)
print()

total = len(old_outputs)

for label, key in [('OLD PROMPT', 'old'), ('NEW PROMPT', 'new')]:
    m = metrics[key]
    print(f"{label}:")
    print(f"  Avg reply length: {m['total_chars']//total} chars, {m['total_words']//total} words")
    print(f"  Uses customer first name: {m['first_name_usage']}/{total} ({m['first_name_usage']*100//total}%)")
    print(f"  Contains empathy/apology: {m['empathy_phrases']}/{total} ({m['empathy_phrases']*100//total}%)")
    print(f"  Emoji usage: {m['emoji_count']} total")
    print()

print("="*80)
print("KEY DIFFERENCES:")
print("="*80)
old_avg = metrics['old']['total_words'] // total
new_avg = metrics['new']['total_words'] // total
increase = ((new_avg - old_avg) / old_avg) * 100
print(f"Reply length: +{increase:.0f}% (old: {old_avg} words → new: {new_avg} words)")
print(f"First name usage: +{metrics['new']['first_name_usage'] - metrics['old']['first_name_usage']} replies")
print(f"Empathy phrases: +{metrics['new']['empathy_phrases'] - metrics['old']['empathy_phrases']} replies")
print()
