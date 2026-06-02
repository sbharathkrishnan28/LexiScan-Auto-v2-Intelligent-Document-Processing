# API Reference Documentation

## Base URL
`http://localhost:8000/api/v1`

---

## 1. Extract Contract Entities
Uploads a PDF contract, processes it through the NLP pipeline, and returns structured data.

*   **Endpoint**: `/extract`
*   **Method**: `POST`
*   **Content-Type**: `multipart/form-data`

### Request Parameters
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `file` | `file` | Yes | The PDF contract to be analyzed |

### Successful Response (200 OK)
```json
{
  "status": "success",
  "filename": "sample_contract.pdf",
  "analysis": {
    "raw_text": "...",
    "redacted_text": "...",
    "entities": {
      "dates": ["December 31, 2026"],
      "parties": ["Google LLC", "Jane Doe"],
      "amounts": ["$150,500.00", "$5,000.00"],
      "termination_clauses": ["terminate this agreement with 30 days"]
    },
    "clean_amounts": [150500.0, 5000.0],
    "human_review_required": false,
    "flags": []
  }
}
```

---

## 2. Error Handling
The API uses standard HTTP response codes to indicate the success or failure of an API request.

*   **200**: Successful request.
*   **400**: Bad Request (e.g., file is not a valid PDF).
*   **422**: Validation Error (missing file parameter).
*   **500**: Internal Server Error (NLP pipeline failure).
