Subject: Update on the WMS migration dry run

Hi Rosa,

I wanted to give you an update following our second migration dry run over the
weekend. Before I get into it, I should say up front that the issues we found
originate in the legacy WMS and its historical data quality, and are not caused
by anything on the Northpine side. We inherited fifteen years of inconsistent
date formats.

Dry run 2 completed overnight on Sunday. Our first sample check identified
roughly 40,000 shipment records failing validation out of 2.4 million historical
records, which is a little under 2%. The issues are concentrated in the date
fields: the legacy system stored dd/mm and mm/dd formats interchangeably until
your team standardised in January 2019. The carrier code issues from dry run 1
are closed and signed off.

The team has been discussing how to handle this. There are two possible paths:

Option A would be to cleanse the full history before cutover. Jonas estimates
nine more working days of work, which would move go-live from 5 October to 19
October, and it would come with a change request of approximately EUR 18,400.

Option B would be to go live on 5 October as planned with records from January
2019 onward, with the pre-2019 archive cleansed afterwards and loaded read-only
by 30 November. The change request for this would be roughly EUR 9,000.

Both options have merit and we are happy to talk them through on Thursday's call.

Separately, and while we are looking at data quality anyway, we would love to
show you the ops reporting dashboard redesign we have been working on. Nadia can
send over a short deck.

Whichever option you prefer, we will need a signed change request. We told
Mira's team informally that a decision by the 25th would be fine, so there is a
little time. We will send the paperwork over to Tomasz for signature as we did
last time.

Let us know your thoughts.

Best,
Aylin
