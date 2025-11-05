# Normalization Issue Analysis

**Date**: November 4, 2025  
**Status**: 🔍 **Debugging Test Failures**

---

## 🔍 Problem Analysis

Based on the test failures and code review, I've identified the issue:

### Issue 1: "classes" Detection

The test expects:

- `"classes"` → `"classes"` (keep as-is)

But the code might be:

1. Detecting "classes" as ambiguous (because it ends with "ses")
2. Calling LLM for "classes"
3. LLM might return "class" (wrong) or "classes" (correct)

**Root Cause**: The `_is_ambiguous_token` function checks special list BEFORE checking for longer patterns, which is correct. But "classes" ends with "ses", so it should NOT be ambiguous.

Wait - let me trace through the logic:

```python
def _is_ambiguous_token(self, token: str) -> bool:
    if len(token) <= 3:
        return False

    if token.endswith("ing") or token.endswith("ies"):
        return False

    # Special plurals are clear cases - MUST check before suffix patterns
    if token in ["classes", "phases", "bases", "cases"]:
        return False  # ← "classes" should return False here

    # ... rest of function
```

So "classes" should return False (not ambiguous), and then `_normalize_with_logic` should handle it.

But in `_normalize_with_logic`:

```python
elif token in ["classes", "phases", "bases", "cases"]:
    return token  # Keep as-is
```

So "classes" should work correctly. But the test is failing, which means either:

1. The special list check isn't working
2. The logic path isn't being used
3. There's a bug in the logic flow

### Issue 2: "teaches" and "includes" Detection

The test expects:

- `"teaches"` → `"teach"`
- `"includes"` → `"include"`

These should be detected as ambiguous:

- "teaches" ends with "es" AND "ches" ✓
- "includes" ends with "es" AND "ses" ✓

So they should go through LLM. But the test might be failing because:

1. LLM isn't being called (mock client issue)
2. LLM returns wrong result
3. Logic path is being used instead of LLM

---

## 🐛 Potential Bugs

### Bug 1: Mock Client Issue

The test uses `MagicMock(spec=OpenAI)` which might not properly mock the `chat.completions.create` method. When `_normalize_predicate_with_llm` is called, it tries to call:

```python
response = self.llm_client.chat.completions.create(...)
```

But `MagicMock` might not have the nested `chat.completions.create` structure properly mocked.

### Bug 2: Logic Path Still Used

Even if "teaches" is detected as ambiguous, the code might still be using the logic path if there's an issue with the flow.

---

## 🔧 Solution

### Fix 1: Better Mock Client

The test needs to properly mock the OpenAI client:

```python
from unittest.mock import MagicMock, Mock

mock_client = MagicMock(spec=OpenAI)
mock_response = MagicMock()
mock_response.choices = [MagicMock()]
mock_response.choices[0].message = MagicMock()
mock_response.choices[0].message.content = "teach"  # or "include", etc.

mock_client.chat = MagicMock()
mock_client.chat.completions = MagicMock()
mock_client.chat.completions.create = MagicMock(return_value=mock_response)
```

### Fix 2: Check Actual Behavior

I need to verify:

1. Is `_is_ambiguous_token` correctly identifying ambiguous tokens?
2. Is the LLM path being called?
3. Is the fallback logic being used?

---

## 📋 Next Steps

1. **Fix Mock Client**: Update test to properly mock OpenAI client
2. **Add Debug Logging**: Add logging to see which path is taken
3. **Test Individual Cases**: Test each case separately to isolate issues
4. **Verify LLM Calls**: Ensure LLM is actually being called for ambiguous cases

---

**Status**: ⏳ **AWAITING DEBUGGING** - Need to verify actual behavior
