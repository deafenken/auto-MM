# Citation discipline — building `literature.md` without hallucinating

The single biggest LLM failure mode in contest writing is fake citations. Plausible-looking authors, journals, page ranges — all fabricated. Editors and judges check. This file is the protocol that prevents it.

## Hard rules

### CD1 — Every entry must be verified before it lands in `literature.md`

Verification means **one of**:
- The DOI resolves on doi.org to a paper matching the title and authors.
- The arXiv ID resolves on arxiv.org to a matching abstract.
- A specific URL (publisher / institutional / governmental) is fetched and the page text contains the title.
- A printed citation in a textbook / official policy document that the user can hand-verify.

No verification → no entry.

### CD2 — Do not cite from training-data memory

The model's prior knowledge of papers is unreliable for specific bibliographic details (page numbers, exact titles, year shifts). Always re-fetch.

The wrong pattern: "I remember a 2018 paper by Smith on VRPs in green zones..." → write the entry. **Stop.** Verify via search before the entry is appended.

The right pattern: WebSearch for the topic → identify candidate papers → WebFetch the abstract or DOI page → confirm details → write the entry.

### CD3 — Prefer primary sources over secondary

For an algorithm, cite the original paper introducing it (e.g., Pisinger & Ropke 2007 for ALNS). For a policy, cite the policy document. For a domain fact, cite the source data publication.

Secondary sources (textbooks, reviews) are OK as supporting context but should not be the only support for a claim that has a primary source.

### CD4 — One source per claim, in the right place

If `model.md` says "ALNS converges effectively on routing problems [Pisinger 2007]", the citation goes there, not in a separate "general references" bucket. Citations are placed where they support a specific sentence.

### CD5 — `literature.md` is the working bibliography

```markdown
## Pisinger & Ropke 2007 — ALNS for VRP

**Authors:** D. Pisinger, S. Ropke
**Title:** A general heuristic for vehicle routing problems
**Venue:** Computers & Operations Research, 34(8):2403-2435
**Year:** 2007
**DOI:** 10.1016/j.cor.2005.09.012
**Verified-at:** 2026-02-08T10:30Z via doi.org
**Supports:** the choice of ALNS as backbone heuristic in candidates.md and the convergence claim in model.md §5.2
**bibkey:** pisinger2007alns
```

Stage 3 reads this and emits the BibTeX entries.

## Workflow

```
For each modeling claim that needs support:
  1. Identify the precise claim (one sentence).
  2. Search for the supporting source (WebSearch, then WebFetch the top candidate).
  3. If a source matches:
      - Record in literature.md with the template above.
      - Mark Verified-at with timestamp.
      - Cite at the point of the claim in model.md / candidates.md.
  4. If no source matches:
      - Restate the claim as a team assumption in assumptions.md, OR
      - Remove the claim from the writing, OR
      - Open an escalation: "claim X needs a source I cannot find."
```

## Verification cheats (allowed when judiciously used)

- **arXiv IDs** are the easiest to verify: `arxiv.org/abs/XXXX.YYYYY`. If the abstract matches and the authors match, you're done.
- **DOI lookup**: `https://doi.org/<DOI>` redirects to the paper's publisher page. The page title plus authors confirm.
- **Wikipedia for context, primary source for citation**: Wikipedia can guide you to a topic, but the paper cited must be the primary source, not the Wikipedia article.
- **Semantic Scholar / Google Scholar**: useful for retrieving DOIs but the paper itself must still be confirmed.

## When in doubt, drop the claim

A weak paper with one fewer citation > a disqualified paper with one fake citation. If after 10 minutes you can't verify, the right move is to remove the supporting claim or rephrase it as an unsupported assumption.

This is especially important for "background" citations that are easy to add and easy to fake. Fewer, real citations >> many, suspicious citations.

## Special case — CUMCM Chinese references

For CUMCM (中文 paper):

- Prefer Chinese-core (北大核心, CSCD, 中文 SCI) papers when claiming domain context for a Chinese setting.
- Verify via 知网 (cnki.net) or Wanfang. Record the link.
- Official Chinese policy documents (国务院, 国家发改委, 行业协会) are strong: cite the URL + title + issue date.
- Don't mix Chinese-only and English-only refs randomly; use both deliberately. The writing stage will format both consistently in the GB/T 7714 style.

## Special case — code/data citations

If your model uses a public dataset or a library version that matters:

- Datasets: cite the dataset's official release page or canonical paper.
- Libraries: cite a version-pinned URL (e.g. Zenodo DOI for a release) only if the choice matters for reproducibility.
- For routine libraries (NumPy, Pandas), do not citation-pad; mention in the appendix software list.

## Forbidden practices

- Citing a Chinese-titled paper with an English title (or vice versa) — translation errors are a strong fake signal.
- Citing a paper "in press" without a stable URL.
- Citing a paper with `et al.` and no first-author check.
- Stacking 4+ supporting citations on a single sentence to look thorough — choose the strongest 1-2.
- Citing the contest's own problem PDF as a reference. The problem statement is the work, not a source.
