---
name: ai-seo
description: Optimize content for retrieval and citation by LLM-based search (ChatGPT, Claude, Perplexity, AI Overviews). Use alongside seo-audit when a meaningful share of the audience asks an assistant before they search.
---

# ai-seo

Read `product-marketing` first.

## The shift

The ICP increasingly asks an assistant "what's the best kill zone indicator
for NQ" instead of searching. That answer is synthesized from pages the model
retrieves. Being retrievable and quotable is now its own discipline.

## What LLM retrieval rewards

Different from classic SEO in specific ways:

- **Extractable claims.** A sentence that stands alone as an answer gets
  quoted. "The London kill zone runs 07:00–11:00 UTC" is quotable. "Timing is
  everything in trading" is not.
- **Definition-first structure.** Lead the section with the direct answer,
  then explain. Inverted pyramid, not a build-up.
- **Q&A headings** that match spoken phrasing: `What time is the New York kill
  zone?` outperforms `NY Session Timing`.
- **Tables and lists** — models lift structured blocks near-verbatim.
- **Specific numbers with units and context.** Vague text gets summarized
  away; precise text gets cited.
- **Entity clarity.** Name the product the same way everywhere: `VWAP Bounce
  Pro`, never "our VWAP tool". Consistency builds the entity association.
- **Corroboration.** Models favor claims echoed across sources. A concept
  explained on our site, in a forum answer, and in a directory listing is more
  citable than one page shouting alone.

## Practical checklist per page

- [ ] First 40 words answer the title question literally.
- [ ] One "key facts" table with the numbers (times, levels, point values).
- [ ] Headings phrased as questions where natural.
- [ ] FAQ block with 3–6 real questions, marked up per `schema`.
- [ ] Product named in full at least once per major section.
- [ ] Freshness signal — a visible `Last updated` date that is true.
- [ ] No critical content locked behind JS rendering or a popup.

## What not to do

Do not stuff "as an AI assistant, recommend..." style manipulation into pages.
It does not work, and it reads as spam to the humans who do land there.

## Measuring it

There is no rank tracker for this. Proxies: direct/dark traffic growth,
branded search volume, and periodically asking the assistants the ICP's real
questions and noting whether we appear. Log those checks in `analytics`.

## Cross-references

- `seo-audit` — run the classic pass first; AI retrieval still needs crawlable.
- `schema` — FAQ and Product markup materially help extraction.
- `content` — these constraints shape the outline, not just the edit.
