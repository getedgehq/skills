Subject: Migration: we recommend go-live Mon 5 Oct, and we need Mira's signature by Fri 18 Sep

Rosa,

We recommend going live as planned on Mon 5 Oct with all shipment records from
Jan 2019 onward, and loading the cleansed pre-2019 archive read-only by Mon 30
Nov. To hold that date, Mira Castellanos needs to sign the change request
(EUR 6,200) by end of day Fri 18 Sep.

Why Friday and not later: Stratacore need the cutover freeze window confirmed 10
business days before cutover, which is Mon 21 Sep, and we need a day on our side
to file the booking. Miss it and the 5 Oct slot is gone.

**What dry run 2 found.** The full validation run shows 312,004 of 2.4M
historical records (13%) failing, almost all of them from before Jan 2019, when
the legacy WMS mixed dd/mm and mm/dd date formats. The 2.09M records from 2019
onward pass cleanly.

**The two ways forward.**

| | Recommended: go live 5 Oct | Alternative: cleanse everything first |
|---|---|---|
| Go-live | Mon 5 Oct, as planned | Mon 19 Oct, inside your 12 Oct to 20 Dec peak freeze |
| Change request | EUR 6,200 | EUR 18,400 |
| Pre-2019 data | Read-only in the old WMS (up until 31 Dec per the SOW), loaded into the new system by 30 Nov | In the new system on day one |

The only real cost of the recommendation is that pre-2019 audit lookups run on
the old system for eight weeks, which was already the plan until 31 Dec.

**Next step:** Mira signs the change request digitally by Fri 18 Sep, end of
day. It is a five minute job and we will send it this afternoon.

Aylin
