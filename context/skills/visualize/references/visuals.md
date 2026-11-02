# Visuals

## Which form

| The idea is… | Use | Examples |
|---|---|---|
| A structure: parts and how they connect | Mermaid `graph` or `classDiagram` | Architecture, taxonomies, dependency maps |
| A sequence of messages between parties | Mermaid `sequenceDiagram` | Protocols, request flows |
| A set of states and transitions | Mermaid `stateDiagram-v2`; HTML if the user should drive it | Automata, lifecycles |
| A process over time | HTML stepper | Algorithms, training loops, proofs step by step |
| A quantity that changes with a parameter | HTML slider that redraws | Learning rates, distributions, physical systems |
| A space or geometry | HTML canvas or SVG | Vectors, transformations, embeddings |
| Prose would do | No visual | Definitions, history, opinions |

## HTML rules

- **One file.** Inline all CSS and JavaScript. No CDN, no fonts, no network requests, so it works offline and leaks nothing.
- **Plain DOM, SVG or canvas.** No frameworks.
- **Controls.** Every animation has Previous, Next and Reset buttons and responds to the arrow keys and space. Nothing autoplays without a pause button.
- **State on screen.** Show the current step number and a one-line caption saying what just happened and why.
- **The user's input.** Where it fits, let the user type their own input (an array to sort, a vector to transform) and watch the process run on it.
- **Readable.** At least 16px text, labelled axes and units, and colour never as the only signal: add shape or text too.
- **Small.** Aim under 300 lines. Split a large idea into two pages.
- **Title and source.** A `<title>` naming the concept, and a footer citing the ledger ids the content comes from, or `[not in sources]`.
