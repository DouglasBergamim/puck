---
type: llm
---

PASS if the reply comes from inspecting the working directory (instruction files, layout, git state) and either gives a brief with what it is, layout, commands and gaps citing paths, or, when the directory has no project, says so plainly as a gap instead of describing one.
FAIL if it creates or edits any file, opens a task, or describes files, commands or structure that it did not find in the directory.
