# Appeal run — before

- Produced by: `run_appeals.py::main`
- Service: `app.py::submit`, `app.py::appeal`, `app.py::get_log`
- 3 trials · 2026-11-04 18:00

| Trial | Appeals under_review in the log | Unknown id status | Log entries before → after |
|---|---|---|---|
| 1 | 5/5 | 404 | 100 → 100 |
| 2 | 5/5 | 404 | 110 → 110 |
| 3 | 5/5 | 404 | 120 → 120 |

---

## What actually came back

**Trial 1**

```json
{
  "appeals": [
    {
      "submit_status": 200,
      "content_id": "c_7b6063c523a4",
      "appeal_status": 200,
      "appeal_response": {
        "content_id": "c_7b6063c523a4",
        "message": "We've received your appeal. A person will review this decision.",
        "status": "under_review"
      },
      "log_statuses": [
        "decided",
        "under_review"
      ],
      "in_log_as_under_review": true
    },
    {
      "submit_status": 200,
      "content_id": "c_df64132ed2d1",
      "appeal_status": 200,
      "appeal_response": {
        "content_id": "c_df64132ed2d1",
        "message": "We've received your appeal. A person will review this decision.",
        "status": "under_review"
      },
      "log_statuses": [
        "decided",
        "under_review"
      ],
      "in_log_as_under_review": true
    },
    {
      "submit_status": 200,
      "content_id": "c_034a69c3c44b",
      "appeal_status": 200,
      "appeal_response": {
        "content_id": "c_034a69c3c44b",
        "message": "We've received your appeal. A person will review this decision.",
        "status": "under_review"
      },
      "log_statuses": [
        "decided",
        "under_review"
      ],
      "in_log_as_under_review": true
    },
    {
      "submit_status": 200,
      "content_id": "c_34acb1da53a4",
      "appeal_status": 200,
      "appeal_response": {
        "content_id": "c_34acb1da53a4",
        "message": "We've received your appeal. A person will review this decision.",
        "status": "under_review"
      },
      "log_statuses": [
        "decided",
        "under_review"
      ],
      "in_log_as_under_review": true
    },
    {
      "submit_status": 200,
      "content_id": "c_a33b41f13289",
      "appeal_status": 200,
      "appeal_response": {
        "content_id": "c_a33b41f13289",
        "message": "We've received your appeal. A person will review this decision.",
        "status": "under_review"
      },
      "log_statuses": [
        "decided",
        "under_review"
      ],
      "in_log_as_under_review": true
    }
  ],
  "appeals_under_review": 5,
  "unknown_id": {
    "status": 404,
    "response": {
      "error": "not_found",
      "message": "No submission found with content_id \"c_unknown_trial1\"."
    },
    "log_entries_before": 100,
    "log_entries_after": 100
  }
}
```

**Trial 2**

```json
{
  "appeals": [
    {
      "submit_status": 200,
      "content_id": "c_cfacf12a0779",
      "appeal_status": 200,
      "appeal_response": {
        "content_id": "c_cfacf12a0779",
        "message": "We've received your appeal. A person will review this decision.",
        "status": "under_review"
      },
      "log_statuses": [
        "decided",
        "under_review"
      ],
      "in_log_as_under_review": true
    },
    {
      "submit_status": 200,
      "content_id": "c_6f3b336452e3",
      "appeal_status": 200,
      "appeal_response": {
        "content_id": "c_6f3b336452e3",
        "message": "We've received your appeal. A person will review this decision.",
        "status": "under_review"
      },
      "log_statuses": [
        "decided",
        "under_review"
      ],
      "in_log_as_under_review": true
    },
    {
      "submit_status": 200,
      "content_id": "c_1d174d3d0760",
      "appeal_status": 200,
      "appeal_response": {
        "content_id": "c_1d174d3d0760",
        "message": "We've received your appeal. A person will review this decision.",
        "status": "under_review"
      },
      "log_statuses": [
        "decided",
        "under_review"
      ],
      "in_log_as_under_review": true
    },
    {
      "submit_status": 200,
      "content_id": "c_47ea6c050379",
      "appeal_status": 200,
      "appeal_response": {
        "content_id": "c_47ea6c050379",
        "message": "We've received your appeal. A person will review this decision.",
        "status": "under_review"
      },
      "log_statuses": [
        "decided",
        "under_review"
      ],
      "in_log_as_under_review": true
    },
    {
      "submit_status": 200,
      "content_id": "c_cf7900c1dc5e",
      "appeal_status": 200,
      "appeal_response": {
        "content_id": "c_cf7900c1dc5e",
        "message": "We've received your appeal. A person will review this decision.",
        "status": "under_review"
      },
      "log_statuses": [
        "decided",
        "under_review"
      ],
      "in_log_as_under_review": true
    }
  ],
  "appeals_under_review": 5,
  "unknown_id": {
    "status": 404,
    "response": {
      "error": "not_found",
      "message": "No submission found with content_id \"c_unknown_trial2\"."
    },
    "log_entries_before": 110,
    "log_entries_after": 110
  }
}
```

**Trial 3**

```json
{
  "appeals": [
    {
      "submit_status": 200,
      "content_id": "c_02cadc3c7590",
      "appeal_status": 200,
      "appeal_response": {
        "content_id": "c_02cadc3c7590",
        "message": "We've received your appeal. A person will review this decision.",
        "status": "under_review"
      },
      "log_statuses": [
        "decided",
        "under_review"
      ],
      "in_log_as_under_review": true
    },
    {
      "submit_status": 200,
      "content_id": "c_3e60b57ce8b3",
      "appeal_status": 200,
      "appeal_response": {
        "content_id": "c_3e60b57ce8b3",
        "message": "We've received your appeal. A person will review this decision.",
        "status": "under_review"
      },
      "log_statuses": [
        "decided",
        "under_review"
      ],
      "in_log_as_under_review": true
    },
    {
      "submit_status": 200,
      "content_id": "c_779216a16ec0",
      "appeal_status": 200,
      "appeal_response": {
        "content_id": "c_779216a16ec0",
        "message": "We've received your appeal. A person will review this decision.",
        "status": "under_review"
      },
      "log_statuses": [
        "decided",
        "under_review"
      ],
      "in_log_as_under_review": true
    },
    {
      "submit_status": 200,
      "content_id": "c_6392add95a98",
      "appeal_status": 200,
      "appeal_response": {
        "content_id": "c_6392add95a98",
        "message": "We've received your appeal. A person will review this decision.",
        "status": "under_review"
      },
      "log_statuses": [
        "decided",
        "under_review"
      ],
      "in_log_as_under_review": true
    },
    {
      "submit_status": 200,
      "content_id": "c_023f4c415a38",
      "appeal_status": 200,
      "appeal_response": {
        "content_id": "c_023f4c415a38",
        "message": "We've received your appeal. A person will review this decision.",
        "status": "under_review"
      },
      "log_statuses": [
        "decided",
        "under_review"
      ],
      "in_log_as_under_review": true
    }
  ],
  "appeals_under_review": 5,
  "unknown_id": {
    "status": 404,
    "response": {
      "error": "not_found",
      "message": "No submission found with content_id \"c_unknown_trial3\"."
    },
    "log_entries_before": 120,
    "log_entries_after": 120
  }
}
```
