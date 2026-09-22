# Cap tables, option pools and SAFEs

Source: 1984 Ventures Founders Handbook, chapters "Cap Table 101"
(https://1984.vc/docs/founders-handbook/cap-table-101) and "Introduction to SAFEs" (https://1984.vc/docs/founders-handbook/intro-to-safes), by Ramy Adeeb.
Model your own numbers in 1984's open-source Cap Table Worksheet: https://startup-finance.1984.vc This file
is a derived work; credit 1984 Ventures and the author, and do not present it as
original. The handbook's own disclaimer applies: this is general education, not legal
advice.

## The frame

The cap table has exactly 100 points, no more, no less. When new shares are granted to
employees or investors, the resulting ownership must come from elsewhere in the cap
table. First time founders focus on valuation; more experienced founders care about
ownership. Work in percentage points so the tradeoffs stay visible.

## Priced round mechanics

Definitions from the handbook:

- Pre-money and post-money describe the valuation before and after the financing. A
  company valued at X receiving Y has pre-money X and post-money X + Y.
- Price Per Share (PPS) = pre-money valuation / pre-money capitalization (the number of
  shares before the round, often called Company Capitalization).
- Dilution = new shares issued in the transaction / fully diluted shares (FDS) after the
  transaction. A founder at 50% who experiences 20% dilution ends at 50% * 0.8 = 40%.
- A more accurate post-money definition: FDS after the round * PPS.

Steps:

1. Compute pre-money capitalization: shares in the business before the round.
2. PPS = pre-money valuation / pre-money capitalization.
3. New shares to the investor = investment / PPS.

Handbook example: two founders with 1,000,000 shares each (50/50), a $2M investment at
$8M pre-money, $10M post-money.

- Pre-money capitalization: 2,000,000 shares.
- PPS = 8,000,000 / 2,000,000 = $4.
- New shares = 2,000,000 / $4 = 500,000.

Resulting cap table:

| Holder | Starting shares | Starting % | New shares | Shares after | % after |
| --- | --- | --- | --- | --- | --- |
| Founder A | 1,000,000 | 50% | | 1,000,000 | 40% |
| Founder B | 1,000,000 | 50% | | 1,000,000 | 40% |
| Seed Investor | | | 500,000 | 500,000 | 20% |
| Total | 2,000,000 | 100% | | 2,500,000 | 100% |

Check: post-money = 2,500,000 FDS * $4 = $10M. Dilution = 500,000 / 2,500,000 = 20%.

## Option pool mechanics

Without a pool, granting an employee 5% after the round means issuing 131,578 new shares
and diluting everyone equally, pushing the investor from 20% to 19%. Investors do not
expect to be diluted by each hire, so in a priced round they typically request a
reserved option pool, often around 10%, as part of the round. The pool comes out of the
founders' side in the same negotiation, so the structure becomes 20% investor, 10% pool,
35% per founder:

| Holder | Starting shares | Starting % | New shares | Shares after | % after |
| --- | --- | --- | --- | --- | --- |
| Founder A | 1,000,000 | 50% | | 1,000,000 | 35% |
| Founder B | 1,000,000 | 50% | | 1,000,000 | 35% |
| Seed Investor | | | 571,428 | 571,428 | 20% |
| Option Pool | | | 285,714 | 285,714 | 10% |
| Total | | 100% | | 2,857,142 | 100% |

An employee grant then moves shares out of the pool instead of issuing new ones, so
nobody else dilutes. A 5% grant moves 142,857 shares from the pool to the employee,
leaving the pool at 5% and the investor at 20%.

Two handbook warnings:

- Employee shares are not granted at the offer letter. They require board approval,
  which typically happens at the first board meeting after the employee joins, and the
  delay can affect the price of the shares or options granted.
- If the company is acquired before exhausting unissued options, those options are
  effectively wiped off and everyone's ownership increases proportionally (in the
  example, by 5%).

## SAFE background and terms

Convertible notes were quicker than equity but carried expiration dates, accrued
interest, and converted on a pre-money basis that made ownership hard to understand.
Y Combinator introduced the SAFE (Simple Agreement for Future Equity) in 2013 as a
promise of future equity, neither debt nor equity, with only two negotiated terms, the
Conversion Cap and the Discount, and today only the Conversion Cap. In 2018 YC
introduced the post-money SAFE, shifting conversion from a pre-money to a post-money
basis, granting investors more equity-like rights in M&A, removing pro-rata by default,
and streamlining the payout. The current version for "Valuation Cap, no Discount", the
most common form, is 1.2, downloadable from YC's website.

High level terms of today's post-money SAFE:

- Promise of future equity: a right to future shares, not immediate equity or debt.
- Converts at the lesser of the next round's pre-money or the Valuation Cap,
  irrespective of how many other SAFEs are issued. That ownership still gets diluted by
  the financing round itself and by any increase to the option pool. Conversion uses the
  PPS implied by the cap, not the cap per se.
- Automatic conversion: the holder has no choice in an equity financing; the SAFE is
  intended to turn holders into stockholders.
- Option pool definition in SAFE 1.2: the Post-Money Valuation Cap is "post" the options
  and pool existing prior to the equity financing, but not "post" the new or increased
  pool adopted as part of that financing (e.g. the Series A).
- No concept of a round: a SAFE is a bilateral agreement with no minimum or maximum
  round size. Founders can stack SAFEs and raise the valuation over time.
- Liquidity in M&A: functions like standard non-participating preferred stock, junior to
  debt (including outstanding notes), on par with shareholders and other SAFE holders.
- No interest, no maturity date.

## SAFE conversion mechanics

Steps:

1. Compute the priced round's pre-money capitalization: all shares issued and
   outstanding + unissued options + shares from converting securities, including SAFEs.
2. Compute two PPS values: the SAFE PPS (from its cap) and the priced round PPS. A
   post-money SAFE with a cap converts at the lower of the two. If the round's pre-money
   is lower than the SAFE cap, the SAFE converts at the round's PPS.
3. Issue shares for SAFE holders and for the priced round investors.

The wrinkle: pre-money capitalization includes the SAFE shares, but the SAFE shares
depend on pre-money capitalization. This is the first recursive calculation in cap
tables, and it is why 1984 built a worksheet model instead of circular Excel references.

Handbook worked example: a $2M post-money SAFE at a $10M cap, then a Series A of $8M at
$32M pre / $40M post, on 2,000,000 founder shares. The SAFE investor owns at least
2 / (8 + 2) = 20% of equity before the priced round.

Company Capitalization = capital stock issued and outstanding + unissued options +
converting securities from the SAFE. Because the investor owns at least 20%:

- Company Capitalization = 2,000,000 + 0 + (0.2 * Company Capitalization)
- Company Capitalization = 2,000,000 / (1 - 0.2) = 2,500,000
- PPS for SAFE conversion = 10,000,000 / 2,500,000 = $4
- PPS for priced round = 32,000,000 / 2,500,000 = $12.8
- Shares for the SAFE investor = 2,000,000 / $4 = 500,000
- Shares for the Series A investor = 8,000,000 / $12.8 = 625,000

| Holder | Starting shares | Starting % | Shares in priced round | FDS shares | FDS % |
| --- | --- | --- | --- | --- | --- |
| Founder A | 1,000,000 | 50% | | 1,000,000 | 32% |
| Founder B | 1,000,000 | 50% | | 1,000,000 | 32% |
| Seed Investor | | | 500,000 | 500,000 | 16% |
| Series A Investor | | | 625,000 | 625,000 | 20% |
| Total | 2,000,000 | 100% | | 3,125,000 | 100% |

Because the PPS at the cap is lower than the round PPS, the SAFE converts at the cap.
The Series A owns 20%. The SAFE investors owned 20% and were diluted by the Series A's
20%, landing at 16%. Overall founder dilution is 36% (20% + 16%, or
1,125,000 / 3,125,000).

The handbook notes one more complication: the Series A investor will also demand a new
option pool for future hires, which adds more recursive iterations to the calculation.
