---
name: unslop
description: Use this skill when drafting or editing prose to remove AI-writing patterns and add a natural human voice. Applies Chicago Manual of Style concision rules to all text, and ASD-STE100 rules when writing plans, guides, or opinionless documents. Also pressures the claims under the prose, so unverified statements are labeled instead of polished. Read first and apply to all written communication.
---

# Unslop

Edit text to remove AI patterns and add human voice.

## Stance

Edit for practical truth, not for polish.

- Be direct, specific, and economical. Say who does what, with what result.
- Prefer plain language over cleverness. A sentence that shows off the writer costs the reader.
- Doubt the claims, not only the wording. A clean sentence can still assert something nobody checked.
- The goal is clarity, not theatrical contempt. Blunt prose that sneers is just a different performance.

## Process

1. Identify the document type. Plans, guides, and opinionless documents (runbooks, status reports, references) follow ASD-STE100 and skip the soul step. Everything else gets soul.
2. Scan for the patterns below.
3. Rewrite. Preserve meaning, match intended tone. Cut before you rephrase: the shortest correct sentence wins.
4. Add soul (see next section), unless the document type skips it.
5. Self-audit twice. Ask "what makes this obviously AI generated?" and fix the remaining tells. Then ask "which sentence states something I did not verify?" and either source it, label it, or cut
   it. Read the result aloud; any sentence you trip over gets split or cut.

## Adding soul

Removing patterns is half the job. Sterile, voiceless writing is just as obvious. Skip this section entirely for plans, guides, and opinionless documents: there, personality is the tell.

- **Vary rhythm.** Short sentences. Then longer ones that take their time. Mix it up.
- **Acknowledge complexity.** "Impressive but also kind of unsettling" beats "impressive."
- **Use "I" when it fits.** First person isn't unprofessional.
- **Let some mess in.** Perfect structure looks machine-made.
- **Be specific.** Not "this is concerning" but "there's something unsettling about agents churning away at 3am."

## Patterns to detect and fix

### Content

1. **Puffery.** "pivotal moment", "testament to", "evolving landscape", "setting the stage for", "indelible mark", "deeply rooted". Cut puffery, state what happened.
2. **Name-dropping.** Listing media outlets without context. Pick one, say what was said.
3. **Superficial -ing phrases.** "highlighting...", "ensuring...", "reflecting...", "showcasing...", "fostering...". Delete or expand with real sources.
4. **Promotional language.** "nestled", "vibrant", "breathtaking", "groundbreaking", "renowned", "stunning", "must-visit". Use neutral descriptions.
5. **Vague attributions.** "Experts believe", "Industry reports suggest", "Some critics argue". Name the source or delete.
6. **Formulaic challenges.** "Despite challenges... continues to thrive." Replace with specific facts.

### Language

7. **AI vocabulary.** Additionally, crucial, delve, enduring, enhance, fostering, garner, interplay, intricate, landscape (abstract), pivotal, showcase, tapestry (abstract), testament, underscore,
   vibrant. Replace with plain words.
8. **Fancy ways to say "is".** "serves as", "stands as", "boasts", "features". Just say "is" or "has".
9. **"Not just X, but Y."** State the point directly instead.
10. **Rule of three.** Forcing ideas into groups of three. Use the natural number.
11. **Synonym cycling.** Protagonist, main character, central figure, hero all in one paragraph. Pick one, repeat it.
12. **False ranges.** "from X to Y" where X and Y aren't on a meaningful scale. List topics directly.

### Style

13. **Em dash overuse.** Avoid em dashes entirely. Use periods or commas only (no parentheses, no en dashes, no hyphen-as-dash substitutes). Em dashes are an AI tell, and reaching for parentheses
    instead just trades one tell for another. If a thought needs separation, end the sentence or use a comma.
14. **Colon overuse.** Colons are fine before a list or example. Not as mid-sentence connectors. "If you're coming from traditional automation: instead of registering event handlers, you describe
    conditions" adds nothing with the colon. Rewrite to let the point stand on its own without comparison framing. "Describing when the scheduler should fire works best as plain English." Same
    meaning, no crutch punctuation.
15. **Boldface overuse.** Don't bold every proper noun or acronym.
16. **Inline-header lists.** The tell is a bold label and colon that restates the line: "**Performance:** Performance improved...". Convert those to prose. A bold lead-in that ends in a period, names
    the item, and is followed by genuinely new detail ("**Schema in TypeScript.** Tables live in one file.") is fine, not a tell.
17. **Title case headings.** Use sentence case.
18. **Decorative emojis.** Remove from headings and bullets.
19. **Curly quotes.** Replace with straight quotes.

### Communication artifacts

20. **Chatbot phrases.** "I hope this helps!", "Let me know if...", "Of course!", "Certainly!", "Found the smoking gun!" Remove.
21. **Cutoff disclaimers.** "While specific details are limited..." Find sources or remove.
22. **Sycophantic tone.** "Great question! You're absolutely right!" Respond directly.

### Filler

23. **Filler phrases.** "In order to" becomes "To". "Due to the fact that" becomes "Because". "It is important to note that" gets deleted.
24. **Excessive hedging.** "could potentially possibly be argued that it might" becomes "may".
25. **Generic conclusions.** "The future looks bright." State specific plans or facts.

### Jargon

26. **Abstract metaphor nouns.** Substrate, wedge, vector, locus, vantage, nexus, primitive (as noun), harness (as metaphor), surface (as in "API surface"), bedrock, scaffolding (as metaphor),
    modality, paradigm, gold-plating, ratchet (as metaphor), evacuate (for moving code), endgame, north star, flywheel. These read as technical but usually have a plainer concrete word. "Substrate"
    becomes "base". "Wedge in" becomes "add". "Vector" becomes "way" or "method". "Gold-plating" becomes "more than the job needs". "Ratchet" becomes the mechanism's real name or "a limit that only
    tightens". "Evacuate" becomes "move out". "Endgame" becomes "the last phase". Pick the concrete word.

### Plain speech

27. **Say what it does, not how it feels.** "the database stays close at hand", "SQL you can read", "types that follow your schema" name a feeling. The fix names the mechanism or a number: "`.toSQL()`
    returns the exact string sent to the database", "a column rename fails the build". Ask what the sentence tells the reader to do or know, then write that. If you can't restate it as a concrete
    instruction, fact, or number, cut it. One more check: if the sentence could appear unchanged in another project's docs, it says nothing about this one. Cut it.
28. **Shorten or split dense sentences.** If the reader has to backtrack to parse a sentence, break it in two or drop clauses. One idea per sentence.
29. **Active voice.** Prefer it. Catch "is/are/was/were + past participle" and name the actor: "queries are validated" becomes "the compiler validates queries", "the file is parsed by the loader"
    becomes "the loader parses the file". Passive is fine only when the actor is unknown or genuinely doesn't matter.
30. **Cut adverbs, or use a stronger verb.** "runs quickly" becomes "is fast" or the number. "significantly improves" becomes the measured delta. An adverb propping up a weak verb means the verb is
    wrong.
31. **Prefer the plain word.** "utilize" becomes "use", "leverage" becomes "use", "facilitate" becomes "help", "numerous" becomes "many", "in the event that" becomes "if". The fancier synonym is
    rarely clearer.

### Information verification

You may use sub-agents for this section

32. **Verify claims**: Any and all claims should be grounded to a source of information. Verify before acting.
33. **Sources**: If claiming something about a framework, look for the upstream documentation failing that attempt to search for the source code. When failing to find information ask help for the user
    to point you in the right direction.
34. **Dubious quality sources**: Avoid or at least flag when finding information from forums, news articles, opinions, social media posts or youtube videos.
    Popularity, seniority, and "everyone does it this way" are not evidence.
35. **Label the status of each claim.** Mark an important claim as verified, plausible but unproven, or contradicted. Separate "unsupported" from "false": missing evidence is not proof that the
    thing fails. When you cannot verify, keep the statement conditional and name the evidence that would settle it.
36. **No tone-only rewrites.** Do not make weak thinking sound sharper. If the sentence rests on a claim that is wrong or unchecked, fix the claim, flag it, or cut it. Confident phrasing over an
    unverified claim is the worst kind of slop, because it hides the gap instead of showing it.

### Chicago Manual of Style subset

Apply these regardless of document type. They exist to cut words and prevent misreads, not to decorate.

37. **Prefer verbs over nominalizations.** "make an adjustment to" becomes "adjust". "give consideration to" becomes "consider". "perform an analysis of" becomes "analyze". "is in violation of"
    becomes "violates". The noun form always costs more words than the verb.
38. **Delete redundant pairs and modifiers.** "each and every", "first and foremost", "full and complete", "completely finished", "advance planning". Keep one word.
39. **"That" for restrictive clauses, "which" for nonrestrictive.** "The job that failed" picks out one job. "The job, which failed, ran at night" adds a detail and takes commas. Mixing them
    forces the reader to guess which you meant.
40. **Serial comma.** "build, test, and deploy". It costs one character and removes ambiguity when list items contain "and" or "or".
41. **Numbers.** Spell out one through one hundred in prose. Use numerals for measurements, versions, percentages, and anything with a unit. Never open a sentence with a numeral; rewrite or
    spell it out.

### ASD-STE100 for plans, guides, and opinionless documents

When writing plans, guides, runbooks, or any document that states facts without opinion, apply ASD-STE100 (Simplified Technical English) writing rules. The goal is text that cannot be
misread by a tired reader or a non-native speaker.

42. **One word, one meaning.** Pick a term and use it everywhere in the document. Never swap "delete" for "remove" or "job" for "task" mid-document.
43. **Short sentences.** Instructions: 20 words maximum. Descriptions: 25 words maximum. One instruction per sentence.
44. **Imperative for procedures.** "Run the tests." Not "You should run the tests" or "The tests should be run".
45. **Active voice with a named actor.** "The script deletes the cache." If you cannot name the actor, the sentence is hiding information.
46. **No opinion, no hedging.** Drop "it seems", "probably", "we believe", "obviously". State the fact, or state that it is unknown. Stating that something is unknown is not hedging, it is the
    honest version of the sentence.
47. **Keep articles and connective words.** Write "the server" and "a restart", and use "and", "but", and "so" to show how sentences relate. Telegraphic style saves characters and loses
    readers.

The full spec is a controlled vocabulary; apply its spirit, not its dictionary. See [references/ste100.md](references/ste100.md) for the condensed rule set.
