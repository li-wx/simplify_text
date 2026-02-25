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
# Step 2 – Organise logical flow
# ---------------------------------------------------------------------------
STEP2_SYSTEM = """\
You are an expert editor focused on logical structure and flow. You will \
receive a numbered list of points extracted from a text. Your ONLY job is \
to reorganise them for clarity while keeping every point accurate and complete.
"""

STEP2_USER = """\
Reorganise the extracted points below. Follow these rules strictly:

1. **Accuracy first**: Keep EVERY point. Do NOT drop, merge, or invent \
information.
2. **Importance ordering**: Put the most important points first.
3. **Logical dependencies**: If point A is needed to understand point B, \
put A before B — even if B is more important.
4. **Grouping**: Group closely related points together as sub-points.
5. **Smooth transitions**: Add brief connecting words or phrases between \
points and groups so a reader can follow the flow easily.

Output a numbered list of the reorganised points. Keep the original wording \
for now — do NOT simplify the language yet.

Extracted points:
{points}
"""

# ---------------------------------------------------------------------------
# Step 3 – Enhance detail quality
# ---------------------------------------------------------------------------
STEP3_SYSTEM = """\
You are a plain-language editor. You will receive an ordered list of points. \
Your job is to polish the language and separate key points from additional \
details.
"""

STEP3_USER = """\
Rewrite the ordered points below. Follow these rules strictly:

1. **Sentence Length**: Every sentence must contain no more than 12 words. \
Break longer sentences into shorter ones.
2. **Common Language**: Use only simple, everyday words. If a technical term \
is essential, briefly explain it in parentheses.
3. **No Redundancy**: Remove duplicated ideas, but do NOT remove unique \
details.
4. **No Ambiguity**: Use clear, precise language.
5. **Separate sections**:
   - "Key Points": list main, critical points only. Include at most 9 points here. \
    Do not list more than 9 points in this section.
   - "Additional Details": move non-critical points, minor context, \
extra explanations of any unresolved ambiguities here. \
Write "None." if empty.

Output exactly those two sections.

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
- At most 3 sentences, written as a single paragraph (no bullet points 
or line breaks between sentences).
- Every sentence must contain at most 12 words. Do not write long sentences.
- Use only simple, everyday words.
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

Checks to perform:
1. **Accuracy**: Every claim in the output must be supported by the original. \
Remove or correct anything the original does not say. Flag nothing as missing \
only if the original actually states it.
2. **Completeness**: Every distinct point from the original must appear in \
Key Points or Additional Details. If something is missing, add it.
3. **Sentence Length**: Every sentence must have no more than 12 words. Split \
any that are longer.
4. **Common Language**: Replace any uncommon words with everyday equivalents.
5. **Logical Order**: Rearrange if needed so prerequisite ideas come first.
6. **Smooth Transitions**: Add brief connectors between points if needed.
7. **No Redundancy**: Remove duplicated ideas.
8. **No Ambiguity**: Clarify vague references. If inherent ambiguity exists, \
note it in Additional Details.

Output exactly these three sections and nothing else:

### Summary
(at most 3 sentences, each sentence with at most 12 words, written as a single paragraph)

### Key Points
(numbered list)

### Additional Details
(list, or "None.")

--- ORIGINAL TEXT ---
{original}

--- SIMPLIFIED VERSION ---
{simplified}
"""
