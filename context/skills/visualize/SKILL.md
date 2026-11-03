---
name: visualize
description: >-
  Explain a concept with a diagram, an interactive page or an animation when
  seeing it is easier than reading it. Use when the user asks to see, draw,
  diagram, animate or visualise how something works or is structured, or when a
  study session hits an idea that is spatial, step-by-step or parameter-driven.
  Not for charts of the user's own data or for UI design.
metadata:
  version: "1"
  status: active
  invocation: model
  requires: "shell, edit"
  origin: "milestone-3"
  last_evaluated: "never"
---
## Procedure
1. Name the one thing the visual must make obvious, in a sentence. If you can't, a visual won't help: explain in words instead.
2. Choose the form with `references/visuals.md`: Mermaid for structure and sequence, an HTML page for anything that moves, steps or responds to input.
3. **Mermaid:** put it inline in your reply or in the wiki page, under 20 nodes, with labels in plain words.
4. **HTML:** write one self-contained file to the topic's `visuals/<concept>.html`, or a scratch folder outside a topic. Follow the rules in `references/visuals.md`. Then run `puck learn open <file>`.
5. Tell the user what to look at and what to try, then ask what they noticed. End the message there.

## Output
A Mermaid diagram, or an HTML file opened in the user's browser.

## Done when
- [ ] The visual shows the sentence from step 1, and nothing irrelevant.
- [ ] An HTML file loads with no network access and works with keyboard alone.

## If something fails
If `puck learn open` can't open a browser, give the user the file path.

## Host differences
Read references/host-tools.md if a named capability is unclear.
