# Test B dry run (D86): read these as a participant would

*Prepared 28 Sep. **Two made-up people, not participants**, built from the real results-sheet template. Brief: a Saturday, from London Bridge station, 10:00–18:00, 4 stops, £40 (`brief.used.yaml`). Plans come from the 30 ready cards. The generic plan is the **example** in `brain/data/testb/generic.example.yaml`; the real one is yours to write (0.5 h, week of 19 Oct).*

| Person | Swipes and choices (made up) | Fields | Personal plan | Generic plan |
|---|---|---|---|---|
| **P01, "calm and culture"** | Loved museums, views, parks; didn't enjoy Camden or the cable car; chose relaxed, quiet, dry days | History & culture, nature | **A** | B |
| **P02, "active and food"** | Loved markets, Brick Lane, the ponds, Sky Garden; didn't enjoy museums or Big Ben; chose packed days and long walks | Food, finance & tech | **A** | B |

**How to spend your hour (≈ 1 h):**
1. **Read `P01_plan_A.txt` and `P01_plan_B.txt` as P01 would** (they are the WhatsApp messages; the PDFs match). Ask yourself: would I follow this? Is anything confusing? Does anything give away which plan is the personal one? Then do the same for P02.
2. **Skim `P01_review.md` and `P02_review.md`** (for you only). They show why each stop was chosen, the strong moments left out, the read-back lines, and the checklist.
3. **Answer two questions (below) and note anything else** to change: tone, length, arrival text, times, prices.

## Two things I noticed: your call

1. **The personal plans finish early.** P01's last stop starts at 12:38 and ends at about 13:15. The generic plan runs to about 15:30, though both briefs say 10:00–18:00. A participant could notice that and guess which plan is the personal one.
   - **(a) Spread the stops across the day:** the planner would aim for the last stop to start in the afternoon, with slower gaps (Claude, about 1 h; recommended).
   - **(b) Shorten the brief** to about 10:00–15:00 for both plans.
2. **"A field that inspires them" is the top reason for every stop** for both people, at +0.73 each time. The prior (+0.5) is a GUESS, and it may be pushing aside what their swipes and choices said.
   - **(a) Keep it.**
   - **(b) Lower the prior to +0.25**, so swipes and choices do more of the work (recommended; 5 minutes).

## Already fixed (28 Sep)
- Internal notes such as "(GUESS)" no longer appear in plan text.
- "Getting there … from X" now names the place you left (e.g. "from St Paul's Cathedral"), not the previous stop's title.
- The arrival line no longer repeats "From …" twice.

**Legs marked "check this leg"** use rough transit estimates. You check them by hand before sending, as the review checklist says.
