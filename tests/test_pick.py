import pytest, os, tempfile, textwrap, tomlkit  # noqa: E401
from pick import pick



s1:tuple[str,str] = ("""
On branch dev-longcontexteval
Your branch is up to date with 'origin/dev-longcontexteval'.

Untracked files:
  (use "git add <file>..." to include in what will be committed)
	bert24-base-v2.yaml
	r_first50000.json
	src/evals/items2000.json
	src/evals/rewritten10.json

nothing added to commit but untracked files present (use "git add" to track)
""",
"""
	bert24-base-v2.yaml
	r_first50000.json
	src/evals/items2000.json
	src/evals/rewritten10.json
 """)

def test_run():
    assert s1[1] == pick(s1[0])

