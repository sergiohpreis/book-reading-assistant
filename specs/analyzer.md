# Core Analysis Logic

## Purpose

Define the analysis engine that compares reading notes against reference techniques using Claude API. Handles token estimation, message construction, API calls, and result processing.

## Analysis Flow

### Workflow Steps

1. **Load Reference PDFs**: Retrieve all PDFs from reference library
2. **Load Book PDF**: Read and prepare target book PDF for analysis
3. **Load Notes**: Read the Markdown notes file provided by user
4. **Estimate Tokens**: Calculate total token count for the API call
5. **Validate Budget**: Check if token count exceeds max_tokens limit
6. **Build Message**: Construct Claude API message with:
   - System prompt with analysis instructions
   - Reference PDFs as content blocks (last one with cache control)
   - Book PDF as content block
   - Reading notes as text content
7. **Call Claude API**: Send message to Claude with specified model
8. **Return Response**: Return analysis result with metadata

### Handling Token Overflow

If estimated tokens exceed max_tokens budget:
1. Display error message with current estimate
2. Suggest solutions:
   - Use `--pages` flag to limit book pages analyzed
   - Extract text from book using `extract_text()` utility
   - Remove reference PDFs from library
   - Increase max_tokens configuration
3. Abort analysis without calling API

## Message Structure

### System Prompt

System prompt instructs Claude to:
- Analyze reading notes using fichamento techniques
- Compare notes structure, completeness, and methodology
- Provide feedback on note quality and areas for improvement
- Suggest enhancements based on reference techniques
- Format feedback in clear, actionable sections

See `prompts.md` for complete system prompt template.

### User Content Blocks

Structured message content in order:

1. **Reference PDFs** (if available)
   - Each reference PDF as document content block
   - Format: `{"type": "document", "source": {"type": "base64", "media_type": "application/pdf", "data": "..."}}`
   - Last reference PDF includes cache control: `"cache_control": {"type": "ephemeral"}`

2. **Book PDF**
   - Target book PDF as document content block
   - Optional: Limited to specified page range via `--pages`
   - Same format as reference PDFs, no cache control

3. **Notes Text**
   - Reading notes as text content block
   - Format: `{"type": "text", "text": "..."}`

See `prompts.md` for helper function that builds this structure.

## Token Estimation

**Formula**: `pages × 2250 tokens/page`

### Estimation Algorithm

1. Use `pdf_utils.estimate_tokens()` for:
   - Each reference PDF in library
   - Target book PDF (or filtered pages if `--pages` specified)

2. Add base overhead: ~500 tokens (system prompt, metadata)

3. For notes text:
   - Estimate as words/150 (rough token ratio)
   - Add buffer: estimate × 1.2

4. **Total**: (ref PDFs tokens) + (book PDF tokens) + (overhead) + (notes tokens)

### Token Budget

Default max_tokens: 200,000 tokens

If estimated > max_tokens:
- Do not proceed with API call
- Display friendly error with breakdown
- Suggest mitigation strategies

## API Integration

### Request Details

- **Endpoint**: Claude API (via anthropic Python SDK)
- **Method**: Send message with specified model
- **Timeout**: 30 seconds (configurable)
- **Retry**: Exponential backoff for transient errors (max 3 retries)

### Parameters Sent

```python
{
    "model": str,                    # From config or --model flag
    "max_tokens": int,               # 4096 (output tokens)
    "system": str,                   # System prompt from build_system_prompt()
    "messages": [
        {
            "role": "user",
            "content": [...]         # Content blocks from build_user_content()
        }
    ]
}
```

### Response Processing

- Extract text content from Claude response
- Preserve metadata (usage, model, timestamp)
- Return structured result with content and metadata

## Result Format

Analysis result includes:

```python
{
    "content": str,              # Claude's analysis text
    "model": str,                # Model used
    "usage": {
        "input_tokens": int,
        "output_tokens": int,
        "cache_creation_input_tokens": int,
        "cache_read_input_tokens": int
    },
    "timestamp": datetime,
    "book_file": str,
    "notes_file": str,
    "references_used": [str],    # List of reference PDF names
    "pages_analyzed": str,       # Page range analyzed or "all"
}
```

## Error Handling

### API Errors

- **Authentication**: Missing or invalid ANTHROPIC_API_KEY → suggest adding to .env
- **Rate limit**: Retry with exponential backoff → inform user if still failing
- **Model not found**: Suggest valid model via `notes config show`
- **Timeout**: Increase timeout or reduce page range

### Data Errors

- **Invalid PDF**: Corrupt or unreadable PDF → suggest verifying file integrity
- **Empty notes**: No content in notes file → request non-empty file
- **Missing files**: Book or notes file not found → provide clear path hints

### Configuration Errors

- **Missing API key**: Friendly message with setup instructions
- **Invalid library**: Library directory doesn't exist → offer to create
- **Invalid output dir**: Path issues → verify or create directory

## Acceptance Criteria

- [x] Analysis completes in < 5 seconds for typical inputs
- [x] Token estimation is accurate (within ±10% of actual)
- [x] Cache control applied correctly to last reference PDF
- [x] All content blocks properly formatted for Claude API
- [x] Error messages are actionable and helpful
- [x] Results include complete metadata for output formatting
- [x] API calls respect rate limits and implement retry logic
- [x] Page range filtering works correctly
- [x] Analysis succeeds with zero, one, or multiple reference PDFs
- [x] Token overflow prevention prevents failed API calls
