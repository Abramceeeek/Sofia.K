# Questions for other AI models: reviewing ODYS's London trips

**How to use this:**
1. Open a new chat with each model (for example ChatGPT, Gemini, Copilot, Mistral, Grok).
2. Paste the prompt below.
3. Then paste the whole of `examples.md` (or attach it).
4. Save each answer as `answers/<model>-<date>.md`, next to this file.
5. Claude puts the answers into one table and lists what they agree on.

Use the same prompt for every model, so the answers can be compared. Don't add your own opinion to the prompt: it would steer them.

---

## The prompt (copy from here)

You are reviewing a travel app called ODYS. It doesn't list famous places. It plans London days around how a specific person wants to feel, from a short set of answers:
- places they know and how they felt there;
- their interests;
- who they travel with;
- their pace and budget;
- how they want the trip to feel.

Below are six invented travellers. For each, you'll see their answers and the exact plan the app produced, in the words the app shows on the phone. Nothing was edited by hand.

Please be a demanding, honest reviewer. Don't be polite, and don't praise anything that hasn't earned it. Quote the plan when you make a point.

**Part A: for each of the six travellers, score 1 to 5 (5 is best), with one sentence of evidence for each score.**

| # | Question |
|---|---|
| A1 | **Personalised.** Does the trip clearly follow what this person said? Does anything contradict their answers? |
| A2 | **Thinks about the human being.** Energy across the day, rest, food at sensible times, travel time, darkness and cold in December, children or older travellers where relevant. |
| A3 | **Solves a real problem.** Would this save them real planning effort, or would they still have to search elsewhere? |
| A4 | **Helpful and worth it.** Would they follow it, and feel the time and money were well spent? |
| A5 | **Easy to understand.** Is each stop clear about what to do, where, when, what it costs and why it was chosen? |
| A6 | **Layout and wording.** Is the text clear, warm and plain? Is the order of information right? Does anything sound robotic, repetitive or confusing? |

**Part B: across all six.**

| # | Question |
|---|---|
| B1 | The three best things about these plans. |
| B2 | The five most important problems, ranked by how much they would hurt a real trip. Give a concrete fix for each. |
| B3 | Anything that looks wrong or risky: impossible timings, a place likely to be shut, an odd order, misleading wording, a "Why" line that doesn't match the person. |
| B4 | What kinds of London places are missing for these travellers (for example evenings, rainy days, children, food by cuisine or price)? |
| B5 | Compared with what a well-informed local friend would plan, how close is this, from 1 to 10? What is the single biggest gap? |
| B6 | Would you recommend this app to a friend visiting London? Yes, no, or not yet, and why. |

**Answer format:**
- Part A as a table: one row per traveller, one column per question (A1 to A6), plus a column for your one-line evidence.
- Then Part B as numbered lists.
- Keep it under 1,200 words.

[Paste examples.md here]

---

## For Claude: reading the answers back

**What to gather from each model's answers:**
- Part A's scores, averaged per question and per traveller.
- Every problem that two or more models raise. These go first.
- Every factual claim, such as "this place is closed on Saturdays". Check each one on the place's official page before acting on it. Other models can be wrong about London.

**These reviews are opinions from software, not evidence about real people.** They help find problems quickly. The friends' round and Test B remain the evidence (m196, D127).
