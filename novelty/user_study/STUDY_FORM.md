# Small user study: do the textbook footnotes help?

Promised in the final report (section 8): "a small user study comparing notes with and without
explanations". Ready to run on 23 or 25 Nov with 5 to 8 classmates. About 10 minutes each.

## Design
- Two IE643 test lectures, each in two versions: with the Dive into Deep Learning footnotes and
  without them. Same renderer, same text, same figures. Only the footnotes differ.
- Every participant reads ONE lecture with footnotes and the OTHER without, so each person
  compares the two conditions and no one sees the same lecture twice.
- Half the participants get group A, half group B (alternate by arrival order):

| Group | First read | Then read |
|---|---|---|
| A | lec03 WITH footnotes (`lec03_with_footnotes.pdf`) | lec09 WITHOUT (`lec09_without_footnotes.pdf`) |
| B | lec09 WITH footnotes (`lec09_with_footnotes.pdf`) | lec03 WITHOUT (`lec03_without_footnotes.pdf`) |

- Do not tell participants which version we expect to be better. Call them "version 1" and
  "version 2".

## Form (copy into Google Forms, one section per document)

Intro text: "We turn handwritten lecture notes into PDFs. Please skim two short documents
(about 4 minutes each) and answer a few questions. No names are recorded."

Q0. Group (A or B), filled in by us.

For EACH document (section 1 = first read, section 2 = then read):
1. How clear was this document to follow? (1 = very unclear ... 5 = very clear)
2. How useful would this document be for revising the topic? (1 = not useful ... 5 = very useful)
3. How much do you trust that the content is correct? (1 = not at all ... 5 = fully)
4. Did anything in the document help you understand a concept you were unsure about? (yes / no)
   If yes, what? (short text)

Only for the version WITH footnotes (shown in that section):
5. Were the footnotes relevant to the section they were attached to? (1 = never ... 5 = always)
6. Did any footnote seem wrong or misleading? (yes / no) If yes, which one? (short text)
7. Did the footnotes get in the way of reading the notes? (1 = not at all ... 5 = a lot)

At the end:
8. Which version would you rather revise from? (version 1 / version 2 / no preference)
9. Any other comment? (short text)

## Analysis (no GPU)
- For questions 1 to 3: report the mean and the number of people who rated the footnote version
  higher, equal or lower than the plain version (paired, per person). With 5 to 8 people, report
  counts and do not claim significance. A sign test can be shown for completeness.
- Question 8: count preferences.
- Questions 5 to 7 describe the footnotes themselves and can be compared with our own grading
  (18 of 21 footnotes relevant and supported).
- Write the numbers into `novelty/user_study/results.md` and NOTES.md.
