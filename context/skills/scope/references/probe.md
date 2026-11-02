# Bracketed probe

The probe finds where the learner's knowledge stops, per strand, in a few minutes. It is diagnosis, not teaching: give no hints and no explanations until it ends.

1. Pick 2-4 strands from the topic: the main areas a learner could know independently. If `map.md` exists, use its top-level groups.
2. For each strand, ask one question at a middle level. Multiple choice is fine here, because the goal is to locate an edge, not to practise.
   - Write the correct statement first, then turn it into distractors drawn from real misconceptions, so the right answer can't be spotted by its form.
   - Always include "I don't know" as an option. Guessing hides the edge.
3. Right: ask a harder one in the same strand. Wrong or "I don't know": ask an easier one.
4. Stop a strand once it is bracketed: a right answer at one level and a wrong answer one level up. Two questions in a row at the same result also stops it.
5. Ask one question per message, and end the message with the question.
6. Report per strand: the highest level answered right and the first level missed, in plain words ("knows what a matrix is; hasn't met eigenvectors").

Use this to set starting statuses later: concepts below the bracket start as `introduced`, everything else as `unseen`. Never as `practised` or higher: one right answer is not practice.
