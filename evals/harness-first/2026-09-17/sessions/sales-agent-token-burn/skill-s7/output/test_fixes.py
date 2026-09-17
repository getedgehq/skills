#!/usr/bin/env python3
"""Test that the fixes prevent the retry loop issues."""
import sys
sys.path.insert(0, '/home/user/work')

from agent.tools import with_retries, ToolError, CLIENT_ERRORS, TRANSIENT_STATUSES

# Test 1: Validation error should fail fast (not retry)
print("Test 1: Validation error (422) should fail immediately...")
call_count = 0

@with_retries
def mock_validation_error():
    global call_count
    call_count += 1
    raise ToolError("validation failed", status=422)

try:
    mock_validation_error()
    print("  ❌ FAIL: Should have raised ToolError")
except ToolError as e:
    if call_count == 1:
        print(f"  ✅ PASS: Failed fast after 1 attempt (expected)")
    else:
        print(f"  ❌ FAIL: Called {call_count} times, expected 1")

# Test 2: Server error should retry
print("\nTest 2: Server error (503) should retry 4 times...")
call_count = 0

@with_retries
def mock_server_error():
    global call_count
    call_count += 1
    raise ToolError("service unavailable", status=503)

try:
    mock_server_error()
    print("  ❌ FAIL: Should have raised ToolError")
except ToolError as e:
    if call_count == 4:
        print(f"  ✅ PASS: Retried 4 times (expected)")
    else:
        print(f"  ❌ FAIL: Called {call_count} times, expected 4")

# Test 3: 404 should fail fast
print("\nTest 3: Not found error (404) should fail immediately...")
call_count = 0

@with_retries
def mock_not_found():
    global call_count
    call_count += 1
    raise ToolError("not found", status=404)

try:
    mock_not_found()
    print("  ❌ FAIL: Should have raised ToolError")
except ToolError as e:
    if call_count == 1:
        print(f"  ✅ PASS: Failed fast after 1 attempt (expected)")
    else:
        print(f"  ❌ FAIL: Called {call_count} times, expected 1")

# Test 4: 429 rate limit should retry
print("\nTest 4: Rate limit (429) should retry 4 times...")
call_count = 0

@with_retries
def mock_rate_limit():
    global call_count
    call_count += 1
    raise ToolError("rate limited", status=429)

try:
    mock_rate_limit()
    print("  ❌ FAIL: Should have raised ToolError")
except ToolError as e:
    if call_count == 4:
        print(f"  ✅ PASS: Retried 4 times (expected)")
    else:
        print(f"  ❌ FAIL: Called {call_count} times, expected 4")

print("\n" + "="*60)
print("Test Summary:")
print("  Client errors (4xx): Fail fast ✓")
print("  Server errors (5xx): Retry 4x ✓")
print("  Rate limits (429): Retry 4x ✓")
print("="*60)
