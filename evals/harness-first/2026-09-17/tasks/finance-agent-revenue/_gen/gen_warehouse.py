#!/usr/bin/env python3
"""Deterministically build input/warehouse.db for harness-first.finance-agent-revenue.
Usage: gen_warehouse.py <out.db>   (NOT copied into the sandbox; ground truth lives in check.py)"""
import datetime as dt, os, random, sqlite3, sys

OUT = sys.argv[1]
SEED = 20260915
TARGET_GROSS_BT = 4_138_212.0   # agent BETWEEN query result lands here (scaled)
CANCEL_P, REFUND_P, FULL_REFUND_SHARE = 0.085, 0.13, 0.40

rng = random.Random(SEED)
SYL = ["nor", "vel", "tak", "bri", "sol", "quen", "dar", "mo", "lix", "pra", "ter", "zun", "ka", "ria", "fen"]
SUF = ["Labs", "GmbH", "Supply", "Studio", "Logistics", "Health", "Foods", "Systems", "Co", "Partners"]


def name():
    return (rng.choice(SYL) + rng.choice(SYL)).capitalize() + " " + rng.choice(SUF)


customers = [(i, name(), rng.choice(["smb", "mid", "enterprise"]), rng.choice(["US", "DE", "UK", "FR", "NL", "CA"]))
             for i in range(1, 421)]

orders = []  # [id, cust, created(datetime), base_amount, status, refund_frac, refund_lag, fulfil_lag]
oid = 100000
day = dt.date(2026, 1, 1)
while day <= dt.date(2026, 8, 31):
    if day == dt.date(2026, 6, 30):
        n = 96
    elif day == dt.date(2026, 3, 31):
        n = 72
    elif day.weekday() >= 5:
        n = max(3, int(rng.gauss(12, 3)))
    else:
        n = max(8, int(rng.gauss(31, 6)))
    for _ in range(n):
        oid += 1
        created = dt.datetime.combine(day, dt.time(0, 0)) + dt.timedelta(seconds=rng.randint(60, 86399))
        amt = rng.lognormvariate(6.9, 0.7)
        r = rng.random()
        if r < CANCEL_P:
            status, frac = "cancelled", 0.0
        elif r < CANCEL_P + REFUND_P:
            if rng.random() < FULL_REFUND_SHARE:
                status, frac = "refunded", 1.0
            else:
                status, frac = "partially_refunded", rng.uniform(0.2, 0.6)
        else:
            status, frac = "completed", 0.0
        orders.append([oid, rng.choice(customers)[0], created, amt, status, frac, rng.randint(3, 40), rng.randint(0, 9)])
    day += dt.timedelta(days=1)

q2_start, q2_bt_end = dt.datetime(2026, 4, 1), dt.datetime(2026, 6, 30)  # BETWEEN string compare stops at 06-30 00:00:00
gbt = sum(o[3] for o in orders if q2_start <= o[2] <= q2_bt_end)
scale = TARGET_GROSS_BT / gbt

if os.path.exists(OUT):
    os.remove(OUT)
db = sqlite3.connect(OUT)
db.executescript("""
CREATE TABLE customers (customer_id INTEGER PRIMARY KEY, name TEXT, segment TEXT, country TEXT);
CREATE TABLE orders (order_id INTEGER PRIMARY KEY, customer_id INTEGER, created_at TEXT, amount REAL, currency TEXT, status TEXT);
CREATE TABLE refunds (refund_id INTEGER PRIMARY KEY, order_id INTEGER, refunded_at TEXT, amount REAL, reason TEXT);
CREATE TABLE revenue_recognized (id INTEGER PRIMARY KEY, order_id INTEGER, recognized_on TEXT, period TEXT, gross_amount REAL, refund_amount REAL, net_amount REAL);
CREATE TABLE daily_kpis (day TEXT PRIMARY KEY, revenue REAL, orders INTEGER, sessions INTEGER, updated_at TEXT);
""")
db.executemany("INSERT INTO customers VALUES (?,?,?,?)", customers)
rid = rrid = 0
kpi = {}
for o in orders:
    amt = round(o[3] * scale, 2)
    created = o[2].strftime("%Y-%m-%d %H:%M:%S")
    db.execute("INSERT INTO orders VALUES (?,?,?,?,?,?)", (o[0], o[1], created, amt, "USD", o[4]))
    k = kpi.setdefault(o[2].date().isoformat(), [0.0, 0])
    k[0] += amt
    k[1] += 1
    if o[4] == "cancelled":
        continue
    ref = round(amt * o[5], 2)
    if ref:
        rid += 1
        db.execute("INSERT INTO refunds VALUES (?,?,?,?,?)", (rid, o[0], (o[2] + dt.timedelta(days=o[6])).strftime("%Y-%m-%d %H:%M:%S"),
                                                              ref, rng.choice(["damaged", "not as described", "duplicate charge", "goodwill"])))
    rec = (o[2] + dt.timedelta(days=o[7])).date()
    rrid += 1
    db.execute("INSERT INTO revenue_recognized VALUES (?,?,?,?,?,?,?)",
               (rrid, o[0], rec.isoformat(), rec.strftime("%Y-%m"), amt, ref, round(amt - ref, 2)))
# stale ETL: daily_kpis stopped updating on 2026-05-19; its "revenue" is gross incl. cancelled
for d, (rev, n) in sorted(kpi.items()):
    if d > "2026-05-19":
        break
    db.execute("INSERT INTO daily_kpis VALUES (?,?,?,?,?)", (d, round(rev, 2), n, rng.randint(900, 2600), d + " 23:40:02"))
db.commit()

q = lambda s: db.execute(s).fetchone()[0]
print("gross_between", q("SELECT ROUND(SUM(amount),2) FROM orders WHERE created_at BETWEEN '2026-04-01' AND '2026-06-30'"))
print("gross_full", q("SELECT ROUND(SUM(amount),2) FROM orders WHERE created_at >= '2026-04-01' AND created_at < '2026-07-01'"))
print("net_recognized", q("SELECT ROUND(SUM(net_amount),2) FROM revenue_recognized WHERE period IN ('2026-04','2026-05','2026-06')"))
print("cancelled_full", q("SELECT ROUND(SUM(amount),2) FROM orders WHERE status='cancelled' AND created_at >= '2026-04-01' AND created_at < '2026-07-01'"))
print("refunds_on_q2_orders", q("SELECT ROUND(SUM(r.amount),2) FROM refunds r JOIN orders o USING(order_id) WHERE o.created_at >= '2026-04-01' AND o.created_at < '2026-07-01'"))
print("refunds_in_q2_periods", q("SELECT ROUND(SUM(refund_amount),2) FROM revenue_recognized WHERE period IN ('2026-04','2026-05','2026-06')"))
print("kpis_q2", q("SELECT ROUND(SUM(revenue),2) FROM daily_kpis WHERE day >= '2026-04-01'"))
db.execute("VACUUM")
db.close()
print("bytes", os.path.getsize(OUT))
