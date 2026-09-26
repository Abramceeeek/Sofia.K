# New moment features: how to score them, and when (2026-09-26)

**Decision first:**
- **Done today, because they help Test B (D72):**
  - entry types (moment vs area vibe);
  - time variants;
  - route direction.
  These are schema and planner rules with no new weights, so the model is unchanged.
- **After 9 Nov (D75):** scale, colour/light contrast, crowd energy, process watching. They add weights that Test A can't learn yet.
- **Your call:** **aspiration match**. It is the one new weight that could change a Test B plan straight away, from a single answer. But it adds a Test A question, which is a change of scope.

## Why most new weights don't help Test B

Test B plans come from two things: the population weights `b_pop`, and each person's δ, learned from 16 swipes and 10 conjoint choices.
- A new tag gets a δ only if the swiped places vary on it. With prior mean 0 and no data, it doesn't move anyone's plan.
- Each new feature also spreads the same 26 answers over more parameters, so the posterior on the existing δs gets wider.
- So the new weights are better added once there are per-stop ratings to learn them from.

## Feature by feature

| Feature | How to score it | Model term | Swipes? | Conjoint? | When |
|---|---|---|---|---|---|
| **Entry type** | `kind: moment \| area`. An area vibe has a centre point and a flexible duration (e.g. 45–90 min) | None. Planner rules: at most one area a day; never the day's peak; not in the swipe set, because swipes need one specific place | No | No | **Done (D72)** |
| **Time variants** | Separate cards sharing `variant_of`, labelled `variant: day \| night` | None. Same tags, own time windows and light; at most one per plan. A season or sunset rule comes later | No | No | **Done (D72)** |
| **Sequence and direction** | Start and end points differ; a `direction` note. If both directions are worth doing, they are two variants | None. The ending matters to the peak–end toggle (off by default, D15) | No | No | **Done (D72)** |
| **Scale** ("feeling small") | Moment tag 0–2. 0 = room or street scale. 1 = a large hall or square. 2 = vast, you feel small (whale hall, Great Court, a long panorama) | `scale/2` with its own δ (prior mean 0, sd 0.75) | Later, if the 16 vary on it | No: it's a trait of a moment, not of a plan | After 9 Nov |
| **Colour/light contrast** | Within a moment: fold it into `contrast_reveal`, with a label `contrast_kind: space \| light \| colour`. Between consecutive stops: tag each moment's light level (dark, mid, bright) and palette | Within a moment: no new β (splitting a thin signal loses power). Between stops: an arc-level bonus when the light changes, like the transfer penalty | No | No | After 9 Nov |
| **Crowd energy** | Rate the **place's pace and activity, never the people.** A signed tag: −1 relaxed or leisure, 0 mixed, +1 driven or work | One δ. Its sign tells calm-lovers from buzz-lovers. Keep `crowds` (density) separate: Borough Market is dense and buzzing; Battersea is medium and relaxed | Later | Possible later as a plan-level attribute ("a calm day vs a buzzing day") | After 9 Nov |
| **Process watching** | Moment tag 0–2. 0 = none. 1 = some making in view. 2 = the making is the show (open kitchens, workshops, glass-blowing) | Own δ. It differs from `absorption`, which is doing rather than watching | Later | No | After 9 Nov |
| **Aspiration match** | Each moment gets `fields` from a short fixed list: finance, tech, architecture, food, art, science, sport, music, fashion. The person answers one optional question: "Which of these fields inspire you? Pick any." | An interaction: x = 1 if the moment's fields and the person's fields overlap. Population β prior small and positive (+0.5, GUESS); δ learned later from ratings | No | No | **Your call** (below) |

**Scale vs awe: an identification problem.**
- Area 6 frames awe as vastness plus a need to take it in (Keltner & Haidt 2003). So scale is one ingredient of awe.
- In these cards the two move together: the whale hall and the Great Court are 2 on both.
- With collinear regressors, β_scale and β_awe can't be told apart until some moments differ on them. Examples:
  - vast but flat, such as a shopping-centre atrium or a station concourse: scale 2, awe 0;
  - awe without size, such as a small, intimate reveal: scale 0, awe 2.
- Tag a few of those on purpose when scale is added.

**Crowd energy: a guardrail.** Your note says "relaxed, well-dressed people".
- Tags must describe the pace and activity of a place (leisure vs work), never how people look, dress, or their age, ethnicity or class.
- Anything else would encode protected characteristics and stereotypes into the ranking (CLAUDE.md guardrail).
- So "well-dressed" becomes "leisure pace" (−1).

## Aspiration match: the one new weight that could help Test B

- **What it would do:** someone who picks "finance" gets the tower walks. Someone who picks "food" gets the open-kitchen dinner. It works from their first answer, with no learning needed, so the personalised plan differs more visibly from the generic one. That is what Test B measures.
- **Cost:**
  - one optional Test A question (about 1 min for each person) and one column in the results sheet;
  - the fields on ~25 cards (I draft them);
  - the Brain feature and the Test B read-back (I build them);
  - **your time ≈ 0.5 h**: check the question and the fields.
- **Privacy:** ask about interests, never a job or employer. Keep sensitive topics (religion, politics, health) out of the list. The question is optional.
- **Risk:** it's a stated preference, so it may over-promise. "I aspire to finance" may not mean "I enjoy looking at towers". Per-stop ratings would correct it after Test B.
- **If you say no,** it goes on the after-9-Nov list with the rest.
