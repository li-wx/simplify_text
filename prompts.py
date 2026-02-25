"""
Prompt templates for the multi-step text simplification pipeline.

Each step has a SYSTEM prompt (role instruction) and a USER prompt (task + input).
"""

# ---------------------------------------------------------------------------
# Step 1 – Extract every point from the original text
# ---------------------------------------------------------------------------
STEP1_SYSTEM = """\
You are a precise information extractor. Your ONLY job is to capture every \
single claim, fact, detail, and nuance from the original text. Do NOT \
simplify, rephrase, or omit anything.
"""

STEP1_USER = """\
Read the text below carefully. Extract ALL points it makes — main ideas, \
supporting details, qualifications, and any implied meanings.

Rules:
- Output a numbered list. Each item = one distinct point.
- Preserve the meaning exactly. Do not add information that is not in the text.
- If the text contains ambiguity, note it explicitly (e.g., "Ambiguity: …").
- Do NOT simplify the language yet.

Text:
{text}
"""

# ---------------------------------------------------------------------------
# Step 2 – Deduplicate, merge, and organise logical flow
# ---------------------------------------------------------------------------
STEP2_SYSTEM = """\
You are an expert editor focused on removing redundancy and creating clear \
logical structure. You will receive a numbered list of extracted points. \
Your job is to merge overlapping points and then organise the result.
"""

STEP2_USER = """\
Process the extracted points below in two phases.

**Phase A — Deduplicate and merge:**
- Identify points that convey the same or very similar information.
- Merge overlapping points into a single, more complete point. Keep the \
most informative wording.
- If two points share the same core idea but one adds a small detail, \
combine them into one point that includes the detail.
- After merging, every remaining point should be *clearly distinct* from \
every other point. If you can describe two points with the same one-line \
summary, they must be merged.

**Phase B — Organise:**
1. **Importance ordering**: Put the most important points first.
2. **Logical dependencies**: If point A is needed to understand point B, \
put A before B — even if B is more important.
3. **Grouping**: Group closely related points together as sub-points.
4. **Smooth transitions**: Add brief connecting words between groups.

**Critical rule**: Keep EVERY *unique* piece of information. Do NOT drop \
facts — only merge duplicates. Do NOT simplify the language yet.

Output a numbered list of the deduplicated and organised points.

Extracted points:
{points}
"""

# ---------------------------------------------------------------------------
# Step 3 – Simplify language and classify into Key Points vs Additional Details
# ---------------------------------------------------------------------------
STEP3_SYSTEM = """\
You are a plain-language editor. You will receive an ordered list of \
deduplicated points. Your job is to simplify the language and strictly \
separate key points from additional details.
"""

STEP3_USER = """\
Rewrite the points below. Follow these rules strictly:

**Language rules (apply to ALL points):**
1. Every sentence must contain no more than 12 words. Break longer ones.
2. Use only simple, everyday words. If a technical term is essential, \
briefly explain it in parentheses.
3. Use clear, precise language with no ambiguity.

**Classification rules — read carefully:**

"Key Points" must contain ONLY the most essential information — the points \
a reader absolutely must know to understand the core message. Apply this \
test: *"If I remove this point, does the reader lose a critical piece of \
the main message?"* If no, it belongs in Additional Details.

- **Key Points**: List at most 8 points. Fewer is better. Aim for 5–7 \
when possible. Each point must be clearly distinct from every other point. \
If two points feel related, consider whether one belongs in Additional \
Details instead.
- **Additional Details**: Everything else goes here — supporting context, \
minor qualifications, extra explanations, elaborations on key points, \
edge cases, and any unresolved ambiguities. Write "None." if truly empty.

**When in doubt, place the point in Additional Details.**

Output exactly these two sections:

Key Points:
(numbered list — at most 8, aim for 5–7)

Additional Details:
(numbered list, or "None.")

Ordered points:
{points}
"""

# ---------------------------------------------------------------------------
# Step 4 – Generate the Summary
# ---------------------------------------------------------------------------
STEP4_SYSTEM = """\
You are a summarizer. You will receive simplified key points and additional \
details. Write a short summary.
"""

STEP4_USER = """\
Based ONLY on the content below, write a "Summary" section.

Rules:
- At most 3 sentences, written as a single paragraph (no bullet points \
or line breaks between sentences).
- Every sentence must contain at most 12 words. Do not write long sentences.
- Use only simple, everyday words.
- Focus on the core message from Key Points only.
- Do NOT add any information not present below.

Content:
{content}
"""

# ---------------------------------------------------------------------------
# Step 5 – Final validation
# ---------------------------------------------------------------------------
STEP5_SYSTEM = """\
You are a strict quality-assurance editor. You will receive:
  (A) The ORIGINAL text.
  (B) A simplified version with three sections.

Your job is to verify and fix the simplified version.
"""

STEP5_USER = """\
Compare the simplified version against the original text and fix any issues.

Checks to perform (in this order):

1. **Redundancy (HIGHEST PRIORITY)**: Read every point in Key Points and \
Additional Details. If two points make essentially the same claim — even \
with different wording — merge them into one or remove the duplicate. \
Also check across sections: if a Key Point and an Additional Detail say \
the same thing, keep only the Key Point version.

2. **Key Points count**: Key Points should contain at most 8 items, \
ideally 5–7. If there are more than 8, move the least essential ones to \
Additional Details. Each key point must be clearly distinct from every \
other key point.

3. **Accuracy**: Every claim must be supported by the original text. \
Remove or correct anything the original does not say.

4. **Completeness**: Every distinct point from the original must appear \
in Key Points or Additional Details. If something is genuinely missing, \
add it to the appropriate section.

5. **Sentence length**: Every sentence must have no more than 12 words. \
Split any that are longer.

6. **Common language**: Replace any uncommon words with everyday equivalents.

7. **Logical order**: Rearrange if needed so prerequisite ideas come first.

8. **Smooth transitions**: Add brief connectors between points if needed.

Output exactly these three sections and nothing else:

### Summary
(at most 3 sentences, each with at most 12 words, single paragraph)

### Key Points
(numbered list — at most 8, ideally 5–7)

### Additional Details
(numbered list, or "None.")

--- ORIGINAL TEXT ---
{original}

--- SIMPLIFIED VERSION ---
{simplified}
"""
