# Source roles

Each ledger entry gets one role. Roles decide where a source lands on the reading path.

| Role | What it is | How to find it |
|---|---|---|
| `anchor` | A recent survey, review, handbook chapter or lecture notes that maps the field | `puck sources search "<topic>" --kind survey`, then prefer ones that are recent, widely cited and written by people the field cites |
| `canon` | A work most of the field builds on | The most-cited works in an anchor's reference list: `puck sources graph <anchor ref> --direction references` |
| `frontier` | Recent work moving the field | Works citing the canon or an anchor since a recent year: `puck sources graph <ref> --direction cited-by --since <year>` |
| `textbook` | A book that teaches the material in order | `puck sources search "<topic>" --kind book`; prefer high edition and citation counts, and books an anchor recommends |
| `practical` | Docs, tutorials or code that make it usable | Web search; prefer official docs over blogs |
| `critique` | Failures, failed replications, objections, rival schools | Search for "limitations", "critique", "fails to replicate", or the rival school's name |

## Reading a citation graph

- **References** look backwards. The most-cited items in a survey's references are usually the canon. Two or more anchors citing the same work confirms it.
- **Cited-by** looks forwards. Sorting by citations surfaces the influential follow-ups; restricting to recent years surfaces the frontier. Citation counts lag, so a strong two-year-old paper can have few.
- **Counts are not quality.** Methods papers and datasets collect citations for being used, not for being right. Say why each source matters in `--why`.
- **Independence.** Sources that repeat one origin (a press release and the news stories about it, or a paper and its blog post) share an independence group: pass the same `--group`. Agreement among one group counts once.

## Depth

- `orient`: anchors and one textbook are enough; canon only where the anchors disagree.
- `use`: add the canon behind each core concept and the practical sources.
- `master`: add frontier and critique for each subfield, and read primary papers rather than summaries.
