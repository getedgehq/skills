# CRM Field Dictionary

Valid fields for `crm_update_contact` tool. Last updated: 2026-09-15

## Lead Scoring Fields

### `lead_score`
- **Type:** Integer (0-100)
- **Description:** Standard lead qualification score
- **Usage:** Use for leads scoring 0-79
- **Added:** 2024-01-01 (original scoring system)

### `lead_score_v2`
- **Type:** Integer (0-100)
- **Description:** Enhanced lead qualification score with additional weighting
- **Usage:** REQUIRED for leads scoring 80 or higher
- **Added:** 2026-09-06
- **Notes:** This field was added Sept 6 but not provisioned in all accounts until Sept 12, causing 422 validation errors during rollout

## Contact Fields

### `first_name`
- **Type:** String (max 100 chars)
- **Description:** Contact first name

### `last_name`
- **Type:** String (max 100 chars)
- **Description:** Contact last name

### `email`
- **Type:** String (email format)
- **Description:** Primary email address

### `phone`
- **Type:** String
- **Description:** Primary phone number

### `title`
- **Type:** String
- **Description:** Job title

### `status`
- **Type:** Enum
- **Valid values:** "new", "contacted", "qualified", "opportunity", "customer", "lost"
- **Description:** Current status in the sales pipeline

### `notes`
- **Type:** Text
- **Description:** Free-form notes about the contact

## Schema Changes Log

| Date | Field | Change | Impact |
|---|---|---|---|
| 2026-09-06 | `lead_score_v2` | Added | New field required for high-scoring leads (≥80) |
| 2026-09-12 | `lead_score_v2` | Provisioned | Field now available in all accounts |
| 2025-06-10 | `lead_temperature` | Deprecated | Replaced by `lead_score`, no longer writable |

## Common Errors

### 422 "unknown field"
- **Cause:** Field name doesn't exist in the schema
- **Fix:** Check this document for valid field names
- **Don't:** Retry indefinitely - this is a deterministic error

### 404 "account_merged"
- **Cause:** Account was merged into another account
- **Fix:** Use the parent account ID instead
- **Don't:** Keep trying the old ID - it's permanently gone

### 422 "validation_failed"
- **Cause:** Field value doesn't match type/format requirements
- **Fix:** Check field type requirements above
- **Don't:** Retry with the same value - it will keep failing
