# Exercise types

Every exercise is a folder `exercises/<id>/` in the topic. Ids are short and unique: `<concept>-<n>`.

`exercise.json`:
```json
{"concept": "attention", "kind": "code", "check": "python3 -m pytest -q"}
```
`kind` is one of `code`, `math`, `concept`, `design`. Only `code` has a `check`.

| Kind | Use for | Files | Graded by |
|---|---|---|---|
| `code` | Anything that runs | `prompt.md`, starter files, tests, `exercise.json` with `check` | `puck learn check`: the tests must fail before and pass after |
| `math` | Derivations, proofs, calculations | `prompt.md`, `key.md` with the full worked solution, `rubric.md` | `grader` agent |
| `concept` | Explain it back, compare two ideas, predict an outcome | `prompt.md`, `key.md` with the points a good answer makes, `rubric.md` | `grader` agent |
| `design` | Apply the idea to a small scenario | `prompt.md`, `key.md` with one good design and its trade-offs, `rubric.md` | `grader` agent |

## Writing them

- **Worked example, then fade.** For a new technique, the first exercise is a worked example with one step left blank; the next removes more steps. Change the problem's setup between them, not just the numbers.
- **New case.** A check must apply the idea somewhere the explanation didn't, or it tests recall of the explanation.
- **Small.** One concept per exercise, ten minutes or less.
- **Code tests** test behaviour through the public interface, run in under a minute, and need nothing outside the folder. Use only the standard library unless the topic is a library.

## rubric.md

Three to six criteria, each independent and scored 0 or 1, each stating what earns the point:

```
1. States that attention weights sum to one across positions.
2. Explains that the weights come from query-key similarity, not position.
3. Applies it correctly to the new example: the output is mostly the third value.
```

No partial points and no overall impression score. A criterion that needs judgement says what counts, e.g. "Names any valid reason, such as A or B".
