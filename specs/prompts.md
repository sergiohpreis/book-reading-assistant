# Prompt Templates and Generation

## Purpose

Define system and user prompts that guide Claude's analysis of reading notes using fichamento techniques. Provide functions to build and format prompts for the Claude API.

## System Prompt

### Purpose

The system prompt establishes Claude's role, analysis approach, and output format for evaluating reading notes.

### Template

```
You are an expert in fichamento techniques and reading note-taking methodologies.
Your role is to analyze reading notes provided by a user and compare them against
established techniques demonstrated in reference materials.

When analyzing reading notes, evaluate the following aspects:

1. STRUCTURE AND ORGANIZATION
   - Is the note structure clear and logical?
   - Are main ideas and supporting details properly organized?
   - Is there a clear hierarchy of information?

2. COMPLETENESS
   - Are key concepts from the book captured?
   - Is sufficient context provided for each note?
   - Are important examples or citations included?

3. METHODOLOGY AND TECHNIQUE
   - Do the notes follow acknowledged note-taking techniques?
   - Are techniques properly applied to this material?
   - Is there appropriate use of summary, paraphrase, and direct quotes?

4. CLARITY AND PRECISION
   - Are notes clear and understandable when re-read?
   - Is terminology used consistently?
   - Are ambiguous statements clarified?

5. PRACTICAL UTILITY
   - Would these notes be useful for review later?
   - Can someone else understand the notes?
   - Are they suitable for the stated purpose (study, reference, publication)?

ANALYSIS OUTPUT FORMAT:
Provide your analysis in the following structure:

## Analysis Summary
[Provide a brief 2-3 sentence overview of the notes' strengths and primary areas for improvement]

## Detailed Feedback by Category
For each of the 5 categories above, provide:
- Current State: What is working well
- Gaps or Issues: What needs improvement
- Specific Examples: Concrete instances from the provided notes
- Recommendations: Actionable suggestions for improvement

## Comparison to Reference Techniques
Discuss how the provided notes align with (or diverge from) the techniques demonstrated
in the reference materials. Highlight specific techniques that could be applied.

## Priority Improvements
List 3-5 specific, actionable improvements the user should prioritize, ranked by impact.

## Overall Assessment
Provide a holistic evaluation of the notes' effectiveness and potential impact.

Remember:
- Be constructive and encouraging while being honest about gaps
- Reference specific examples from both the notes and reference materials
- Focus on practical, implementable improvements
- Consider the context of the material being studied
```

### Function

```python
def build_system_prompt() -> str:
    """
    Build the system prompt for Claude's analysis.

    Returns:
        System prompt string with complete analysis instructions
    """
    return """You are an expert in fichamento techniques and reading note-taking methodologies..."""
    # (Full template above)
```

## User Content Builder

### Purpose

Construct the user message content blocks containing reference PDFs, book PDF, and reading notes.

### Function

```python
def build_user_content(
    ref_pdfs: List[Path],
    book_pdf: Path,
    notes_text: str,
    pages: str | None = None
) -> List[Dict]:
    """
    Build user content blocks for Claude API message.

    Args:
        ref_pdfs: List of Path objects for reference PDFs in library
        book_pdf: Path to the book PDF being analyzed
        notes_text: Raw text of reading notes
        pages: Optional page range string (e.g., "1-50,100-150")

    Returns:
        List of content blocks for Claude API user message
    """
```

### Content Block Ordering

Content blocks are ordered strategically for optimal analysis:

1. **Reference PDFs** (First)
   - Establishes the techniques and methodology
   - Claude reads these first to understand the standard
   - Multiple reference PDFs provided in order
   - Last reference PDF includes cache control

2. **Book PDF** (Middle)
   - Context for what the user is reading
   - Allows Claude to understand material being studied
   - Helps evaluate whether notes are capturing key concepts

3. **Notes Text** (Last)
   - The actual notes to be analyzed
   - Comes after context (references and book) for better analysis
   - Presented as plain text for easy processing

### Implementation

```python
from pathlib import Path
from typing import List, Dict
from .pdf_utils import build_pdf_content_block

def build_user_content(
    ref_pdfs: List[Path],
    book_pdf: Path,
    notes_text: str,
    pages: str | None = None
) -> List[Dict]:
    """Build content blocks for analysis message."""

    content = []

    # Add reference PDFs with cache control on the last one
    for i, ref_pdf in enumerate(ref_pdfs):
        is_last = (i == len(ref_pdfs) - 1)
        cache_control = {"type": "ephemeral"} if is_last else None

        content.append({
            "type": "text",
            "text": f"Reference technique PDF: {ref_pdf.name}"
        })
        content.append(build_pdf_content_block(ref_pdf, cache_control=cache_control))

    # Add book PDF
    content.append({
        "type": "text",
        "text": f"Book being studied: {book_pdf.name}"
        + (f" (pages {pages})" if pages else "")
    })
    content.append(build_pdf_content_block(book_pdf))

    # Add notes text
    content.append({
        "type": "text",
        "text": f"Reading notes to analyze:\n\n{notes_text}"
    })

    return content
```

## Usage in Analyzer

```python
# In the analyzer module:

system_prompt = build_system_prompt()

content_blocks = build_user_content(
    ref_pdfs=ref_library.get_all(),
    book_pdf=Path(book_pdf_path),
    notes_text=notes_content,
    pages=pages_arg
)

response = client.messages.create(
    model=config.model,
    max_tokens=4096,
    system=system_prompt,
    messages=[
        {
            "role": "user",
            "content": content_blocks
        }
    ]
)
```

## Prompt Characteristics

### Tone and Style

- **Professional but approachable**: Use clear, standard English without jargon
- **Constructive**: Focus on improvement opportunities, not criticism
- **Practical**: Provide actionable recommendations
- **Context-aware**: Consider the subject matter and reading goal

### Key Principles

1. **Comprehensive Coverage**: Reference all five analysis categories
2. **Concrete Examples**: Require specific examples from notes
3. **Technique-Grounded**: References should inform the analysis
4. **Actionable Output**: Every recommendation should be implementable
5. **Encouraging**: Recognize strengths alongside areas for improvement

### Output Guarantees

The system prompt ensures Claude will:
- Analyze using all five categories
- Reference the provided materials
- Give specific examples
- Provide ranked improvement suggestions
- Offer a holistic assessment

## Customization Points

Future enhancements could include:

- **Analysis focus**: Allow user to emphasize specific categories
- **Technique selection**: Analyze against specific techniques only
- **Output format**: Request JSON, bullet points, or essay format
- **Depth level**: Quick feedback vs. detailed analysis
- **Comparative analysis**: Compare to multiple reference styles

These customizations would be added via CLI flags and integrated into `build_system_prompt()` and `build_user_content()` functions.

## Acceptance Criteria

- [x] System prompt clearly instructs Claude on analysis approach
- [x] System prompt defines comprehensive evaluation categories
- [x] System prompt specifies output structure and format
- [x] User content builder correctly orders reference PDFs, book, and notes
- [x] Cache control applied only to last reference PDF
- [x] Content blocks include helpful context labels
- [x] Prompts encourage constructive, specific feedback
- [x] Analysis framework maps to fichamento techniques
- [x] Output format is predictable and well-structured
- [x] Prompts work with zero, one, or multiple reference PDFs
