# Task 4 report: Lossless clean HTML and normalized Markdown

## Implementation

- Added `clean_html.py` for offline `#storytext` / `div.storytext` selection, source-order block inventory, normalized visible-text SHA-256 values, hash-addressed manual annotations, and semantic/provenance HTML.
- Added `html_to_markdown.py` for mechanical story-section-only conversion with author-note and missing-chapter markers, Unix line endings, NBSP normalization, stripped trailing spaces, bounded blank runs, and one final newline.
- Added synthetic-only transform tests. No live fanfiction prose is present in the tests or fixtures added by this task.

## RED → GREEN evidence

1. RED:

   ```text
   .fanfic-venv/bin/python -m pytest tests/fanfic_dataset/test_transform.py -q
   ModuleNotFoundError: No module named 'scripts.fanfic_dataset.clean_html'
   ```

2. GREEN after the initial implementation:

   ```text
   4 passed in 0.07s
   ```

3. A subsequent focused invariant test reproduced inline punctuation spacing (`First block .`). Root cause: BeautifulSoup `get_text(" ")` inserts a separator between inline-tag text and punctuation. Replacing it with raw text-node joining preserved the original adjacency.

4. Final focused transform suite:

   ```text
   7 passed in 0.07s
   ```

## Verification

```text
.fanfic-venv/bin/python -m compileall -q scripts/fanfic_dataset
success

.fanfic-venv/bin/python -m pytest tests/fanfic_dataset -q
121 passed in 0.87s

git diff --check
success

offline smoke check passed
```

## Files

- `scripts/fanfic_dataset/clean_html.py`
- `scripts/fanfic_dataset/html_to_markdown.py`
- `tests/fanfic_dataset/test_transform.py`

## Self-review and concerns

- All selected story-container blocks are retained unless they are script/style/form-control nodes; no prose is classified by content.
- The clean semantic template derives requested work metadata from the captured raw page's visible profile, while `CapturedPage` provides chapter and canonical URL provenance. No network or registry lookup occurs.
- Annotations reject malformed, unknown, or multiply classified hashes.
- No known concerns.

## Critical/Important fix wave — 2026-07-23

### Findings and fixes

- Block retention was incorrectly coupled to nonempty normalized visible text. Allowed
  direct elements are now inventoried in source order even when their normalized text
  and SHA-256 are empty; this covers horizontal rules, empty structural blocks, and
  non-remote image-only blocks.
- Direct story text used its normalized hash input as output and interpolated a
  `NavigableString` into HTML. Output now uses the original direct text node in a
  BeautifulSoup-created paragraph, while only the inventory text/hash is normalized.
- Sanitization skipped root attributes and decomposed prohibited ancestors before
  traversing their descendants. Prohibited descendant subtrees are now removed
  deepest-first, then the root and remaining descendants are attribute-sanitized.
  Remote images declared through `src`, `srcset`, and common lazy-source attributes
  are removed; relative image `src`/`alt`/`title` values remain.
- Markdown chapter-text groups are now closed before author-note or missing-chapter
  notice blocks and reopened only for later chapter-text blocks, producing disjoint
  ranges in exact source order.
- Chapter 1 provenance now reuses the established FanFiction.net visible-profile
  selectors and parsing helpers, including summary-class fallback, hyphen-separated
  metadata, unlabeled language, fallback titles, and adjacent metadata elements.

### RED → GREEN evidence

1. Initial focused RED:

   ```text
   .fanfic-venv/bin/python -m pytest tests/fanfic_dataset/test_transform.py -q
   .......FFFF
   4 failed, 7 passed in 0.11s
   ```

   The failures independently reproduced empty-block loss/unsafe direct text,
   parent-before-descendant sanitization (`TypeError`), nested Markdown markers, and
   brittle fallback metadata.

2. Remote `srcset` RED:

   ```text
   .fanfic-venv/bin/python -m pytest \
     tests/fanfic_dataset/test_transform.py::test_clean_html_preserves_allowed_empty_and_image_blocks_and_original_text -q
   1 failed in 0.08s
   ```

3. Adjacent visible metadata RED:

   ```text
   .fanfic-venv/bin/python -m pytest \
     tests/fanfic_dataset/test_transform.py::test_chapter_one_metadata_uses_visible_fanfiction_net_variants -q
   1 failed in 0.09s
   ```

4. Final focused GREEN:

   ```text
   .fanfic-venv/bin/python -m pytest tests/fanfic_dataset/test_transform.py -q
   11 passed in 0.08s
   ```

5. Final full fanfic GREEN:

   ```text
   .fanfic-venv/bin/python -m pytest tests/fanfic_dataset -q
   125 passed in 0.86s
   ```

6. Compile and diff checks:

   ```text
   .fanfic-venv/bin/python -m compileall -q scripts/fanfic_dataset
   success
   git diff --check
   success
   ```

### Files and self-review

- `scripts/fanfic_dataset/clean_html.py`
- `scripts/fanfic_dataset/html_to_markdown.py`
- `tests/fanfic_dataset/test_transform.py`
- The fix does not implement the separately logged Minor behavior for non-object
  top-level annotations.
- No unrelated tracked or untracked files were modified or staged by this fix wave.
- No known concerns.

### Commit

- Pending at report append time; the final SHA and subject are appended below after
  the isolated Task 4 fix commit.
- `80613ad559e74c1625c93ddd38089e3b3754a30b fix: preserve fanfic transform semantics`

## Important fix wave 2 — 2026-07-23

### Finding and fix

- Normalized visible text joined all descendant text nodes without a separator,
  preserving inline punctuation but collapsing nested block siblings such as
  `<p>Alpha.</p><p>Beta.</p>` into `Alpha.Beta.` and therefore producing corrupt
  annotation hashes.
- Replaced the flat join with a recursive visible-text walker that inserts
  separation only around block-level and line-break elements. Inline elements
  retain source adjacency, including punctuation immediately after emphasis.
- The walker is used only for block inventory text and hashes. The synthetic
  regression asserts that serialized story HTML is unchanged.

### RED → GREEN evidence

1. Focused RED:

   ```text
   .fanfic-venv/bin/python -m pytest tests/fanfic_dataset/test_transform.py::test_clean_html_hash_text_separates_nested_blocks_without_spacing_inline_punctuation -q
   1 failed in 0.08s
   AssertionError: assert 'Alpha.Beta.With emphasis.' == 'Alpha. Beta. With emphasis.'
   ```

2. Focused transform GREEN:

   ```text
   .fanfic-venv/bin/python -m pytest tests/fanfic_dataset/test_transform.py -q
   12 passed in 0.08s
   ```

3. Full fanfic GREEN:

   ```text
   .fanfic-venv/bin/python -m pytest tests/fanfic_dataset -q
   126 passed in 0.83s
   ```

4. Compile and diff checks:

   ```text
   .fanfic-venv/bin/python -m compileall -q scripts/fanfic_dataset
   success
   git diff --check
   success
   ```

### Files, self-review, and commit

- The commit changed only `scripts/fanfic_dataset/clean_html.py` and
  `tests/fanfic_dataset/test_transform.py`; this report was appended separately as
  required.
- Confirmed the staged diff contained only those two Task 4 files; unrelated and
  pre-existing untracked files were not staged or modified.
- The separately logged Minor behavior for non-object top-level annotations remains
  intentionally unchanged.
- No known concerns.
- `522c0cf48a3b9755ff7f3f7538804c1fe521d5f9 fix: preserve block boundaries in annotation hashes`

## Important fix wave 3 — 2026-07-23

### Findings and fixes

- BeautifulSoup `Comment` is a `NavigableString` subclass, so the direct-child
  story loop appended comment contents to adjacent direct prose and serialized
  them into a generated paragraph. Direct comments are now skipped before the
  general string branch, leaving block inventory, normalized text, hashes, and
  semantic output unaffected.
- `_profile_metadata()` silently synthesized empty required identity fields when
  the profile was absent and passed through empty title or author values. It now
  uses the same `ExtractionError` messages and visible-profile parsing fallbacks
  as `fanfiction_net` for missing profile, empty work title, and empty author.
- Existing story-focused synthetic tests were updated with a shared minimal valid
  profile because the new required-provenance invariant intentionally rejects
  story-only documents. Existing heading/bold-title, author-link, summary-class,
  and metadata-format fallback coverage remains green.

### RED → GREEN evidence

1. Focused RED:

   ```text
   .fanfic-venv/bin/python -m pytest \
     tests/fanfic_dataset/test_transform.py::test_clean_html_ignores_direct_story_comments \
     tests/fanfic_dataset/test_transform.py::test_clean_html_rejects_missing_required_provenance -q
   FFFF
   4 failed in 0.10s
   ```

   The comment regression observed `Alpha invisible comment Beta`; the missing
   profile, empty title, and empty author cases each failed because no
   `ExtractionError` was raised.

2. Focused regression GREEN:

   ```text
   .fanfic-venv/bin/python -m pytest \
     tests/fanfic_dataset/test_transform.py::test_clean_html_ignores_direct_story_comments \
     tests/fanfic_dataset/test_transform.py::test_clean_html_rejects_missing_required_provenance -q
   4 passed in 0.06s
   ```

3. Focused transform GREEN:

   ```text
   .fanfic-venv/bin/python -m pytest tests/fanfic_dataset/test_transform.py -q
   16 passed in 0.09s
   ```

4. Full fanfic GREEN:

   ```text
   .fanfic-venv/bin/python -m pytest tests/fanfic_dataset -q
   130 passed in 0.83s
   ```

5. Compile and diff checks:

   ```text
   .fanfic-venv/bin/python -m compileall -q scripts/fanfic_dataset
   success
   git diff --check
   success
   ```

### Files, self-review, and commit

- The isolated Task 4 change is limited to
  `scripts/fanfic_dataset/clean_html.py` and
  `tests/fanfic_dataset/test_transform.py`.
- Confirmed direct comments cannot flush, create, alter, or serialize a block;
  nested comments remain excluded from visible-text hashes by the existing
  recursive walker.
- Required profile validation happens before the semantic HTML document is
  constructed, while supported FanFiction.net fallbacks remain delegated to the
  established parsing helpers.
- The separately logged Minor non-object annotations behavior remains
  intentionally unchanged.
- Pre-existing unrelated and untracked files were neither modified nor staged,
  apart from this required report append.
- No known concerns.
- `27d1599bf83ea34da342d2ac0e327838fb5dad34 fix: validate fanfic transform provenance`

## Important fix wave 4 — 2026-07-23

### Findings and fixes

- `_story_blocks()` flushed accumulated direct text before every direct element, so
  phrasing content such as `Hello <em>world</em>!` became three independent semantic
  blocks and Markdown paragraphs. Direct text, inline semantic elements, and direct
  `<br>` elements are now buffered into one generated `<p>` and flushed only at a
  genuine block-level direct child.
- The generated phrasing paragraph is sanitized as a unit, preserving inline
  structure and punctuation while retaining the existing normalized visible-text
  hashing behavior.
- `_sanitize_story_node()` traversed only tag descendants. BeautifulSoup comments
  nested inside copied blocks therefore survived serialization even though the
  visible-text walker excluded them. Descendant comments are now extracted before
  prohibited subtree and attribute sanitization, preserving adjacent visible text.

### RED → GREEN evidence

1. Focused RED:

   ```text
   .fanfic-venv/bin/python -m pytest \
     tests/fanfic_dataset/test_transform.py::test_markdown_groups_direct_inline_content_in_one_paragraph \
     tests/fanfic_dataset/test_transform.py::test_markdown_groups_direct_br_with_surrounding_inline_content \
     tests/fanfic_dataset/test_transform.py::test_clean_html_removes_nested_comments_without_separating_visible_text -q
   3 failed in 0.10s
   ```

   The direct-inline case produced five blocks instead of two, the direct-`<br>`
   case produced five blocks instead of one, and the nested comment remained in
   serialized block HTML.

2. Focused regression GREEN:

   ```text
   .fanfic-venv/bin/python -m pytest \
     tests/fanfic_dataset/test_transform.py::test_markdown_groups_direct_inline_content_in_one_paragraph \
     tests/fanfic_dataset/test_transform.py::test_markdown_groups_direct_br_with_surrounding_inline_content \
     tests/fanfic_dataset/test_transform.py::test_clean_html_removes_nested_comments_without_separating_visible_text -q
   3 passed in 0.09s
   ```

3. Focused transform GREEN:

   ```text
   .fanfic-venv/bin/python -m pytest tests/fanfic_dataset/test_transform.py -q
   19 passed in 0.08s
   ```

4. Full fanfic GREEN:

   ```text
   .fanfic-venv/bin/python -m pytest tests/fanfic_dataset -q
   133 passed in 0.84s
   ```

5. Compile and diff checks:

   ```text
   .fanfic-venv/bin/python -m compileall -q scripts/fanfic_dataset
   success
   git diff --check
   success
   ```

### Files, self-review, and commit

- The isolated Task 4 change is limited to
  `scripts/fanfic_dataset/clean_html.py` and
  `tests/fanfic_dataset/test_transform.py`.
- Direct phrasing content retains source order and inline markup; direct `<br>`
  remains in the semantic paragraph and appears as a newline in normalized Markdown.
- Direct block elements still form independent inventory blocks. Dropped controls,
  scripts, styles, direct comments, and remote images neither create nor split a
  phrasing block.
- Nested comments are removed without adding whitespace, so visible text on either
  side retains its original adjacency in hashes, clean HTML, and Markdown.
- The separately logged Minor non-object annotations behavior remains intentionally
  unchanged.
- Pre-existing unrelated and untracked files were neither modified nor staged,
  apart from this required report append.
- No known concerns.
- Commit pending; the final SHA and subject are appended below after the isolated
  Task 4 commit.
- `94f3f3e2e6f24d9451c88f20eef870b8cde5b15d fix: preserve direct fanfic phrasing`

## Important fix wave 5 — 2026-07-23

### Finding and fix

- Chapter 1 provenance skipped summary, rating, language, published, and updated
  fields when their parsed optional values were empty, violating the fixed semantic
  template. Chapter 1 now always emits those five labeled fields in stable order,
  using blank content when source metadata is unavailable. Non-Chapter-1 pages
  continue to omit the complete group.

### RED → GREEN evidence

1. Focused RED:

   ```text
   .fanfic-venv/bin/python -m pytest tests/fanfic_dataset/test_transform.py::test_chapter_one_emits_all_optional_metadata_labels_when_values_are_missing -q
   1 failed in 0.09s
   AssertionError: Right contains 5 more items: 'Summary: ', 'Rating: ', 'Language: ', 'Published: ', 'Updated: '
   ```

2. Focused regression GREEN:

   ```text
   1 passed in 0.07s
   ```

3. Focused transform GREEN:

   ```text
   .fanfic-venv/bin/python -m pytest tests/fanfic_dataset/test_transform.py -q
   20 passed in 0.09s
   ```

4. Full fanfic GREEN:

   ```text
   .fanfic-venv/bin/python -m pytest tests/fanfic_dataset -q
   134 passed in 0.85s
   ```

5. Compile and diff checks:

   ```text
   .fanfic-venv/bin/python -m compileall -q scripts/fanfic_dataset
   success
   git diff --check
   success
   ```

### Files, self-review, and commit

- Changed only `scripts/fanfic_dataset/clean_html.py` and
  `tests/fanfic_dataset/test_transform.py`, plus this required Task 4 report.
- The synthetic regression uses a profile with all optional metadata absent and
  verifies all five labels and their exact Chapter 1 ordering, plus their complete
  Chapter 2 omission.
- The separately logged Minor non-object annotations behavior remains intentionally
  unchanged. No known concerns.
- `ddae76fb565c4125b185464ab81c5011abfd4f9d fix: retain empty fanfic provenance fields`

## Important fix wave 6 — 2026-07-23

### Finding and fix

- A semantic story section without blocks normalized to only a newline. It now emits
  an empty, disjoint chapter-text marker range with the required final newline.
- `summary`, `legend`, `menu`, and `caption` were accepted as direct block-like
  tags but omitted from visible-text boundaries, collapsing nested sibling text.
  A single visible-block set now derives both direct-block and boundary sets.

### RED → GREEN evidence

1. Focused RED:

   ```text
   .fanfic-venv/bin/python -m pytest tests/fanfic_dataset/test_transform.py -q -k 'empty_chapter_range or block_like_nested'
   5 failed, 20 deselected in 0.10s
   ```

   The empty-story assertion received `"\\n"`; each named nested-tag regression
   received `Alpha.Beta.Gamma.Delta.` instead of `Alpha. Beta. Gamma.Delta.`.

2. Focused regression GREEN:

   ```text
   5 passed, 20 deselected in 0.07s
   ```

3. Focused transform GREEN:

   ```text
   .fanfic-venv/bin/python -m pytest tests/fanfic_dataset/test_transform.py -q
   25 passed in 0.09s
   ```

4. Full fanfic GREEN:

   ```text
   .fanfic-venv/bin/python -m pytest tests/fanfic_dataset -q
   139 passed in 0.91s
   ```

5. Compile and diff checks:

   ```text
   .fanfic-venv/bin/python -m compileall -q scripts/fanfic_dataset
   success
   git diff --check
   success
   ```

### Files, self-review, and commit

- Changed `scripts/fanfic_dataset/clean_html.py`,
  `scripts/fanfic_dataset/html_to_markdown.py`, and
  `tests/fanfic_dataset/test_transform.py`, plus this required Task 4 report.
- Regressions cover empty semantic stories and each named accepted block-like tag
  as nested siblings, while demonstrating inline punctuation remains adjacent.
- The separately logged Minor non-object annotations behavior remains unchanged.
- No known concerns. Commit SHA and subject are appended below after commit.
