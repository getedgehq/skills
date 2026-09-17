# Data dictionary: finance metrics

## revenue (default meaning of "revenue", "sales", "turnover")
- Definition: recognized net revenue for a period.
- Source: `revenue_recognized.net_amount`, filter on `period` ('YYYY-MM'). Q2 2026 = periods 2026-04, 2026-05, 2026-06.
- Excludes: cancelled orders (never recognized), refunds (net_amount = gross_amount − refund_amount).
- Q2 2026 reference value: 3,638,335.79.

## gross_bookings
- Definition: value of orders placed, regardless of cancellation or refund. Not revenue; never report it as revenue.
- Source: `orders.amount`, filter `created_at >= start AND created_at < next_period_start` (timestamps, don't use BETWEEN with a date end).

## refunds
- Source: `refunds.amount` (by `refunded_at`) or `revenue_recognized.refund_amount` (by recognition period).

## do not use
- `daily_kpis.revenue`: stale (last load 2026-05-19) and gross incl. cancelled orders.
