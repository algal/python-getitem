import pytest, os, tempfile, textwrap, sys
from pathlib import Path

from pick import pick

s0:tuple[str,tuple[str,str],str] = ("""
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
("5:-2",":"),
"""
	bert24-base-v2.yaml
	r_first50000.json
	src/evals/items2000.json
	src/evals/rewritten10.json
""")

s1 = ("""
AAA
 BBB
CCC
""",
("1",":"),
"""
 BBB
"""
)

dirstring = """
.rw-r--r-- 0 root      2024-11-14 20:59 .localized
drwxr-x--- - alexis    2024-11-25 16:29 alexis
drwxr-xr-x - oldalexis 2023-09-17 14:13 alexis_1
drwxrwxrwt - root      2024-11-21 12:25 Shared
"""

s2 = (dirstring,
    (":",":"),
    dirstring
)

s3 = (dirstring,
    ("0:2",":"),"""
.rw-r--r-- 0 root      2024-11-14 20:59 .localized
drwxr-x--- - alexis    2024-11-25 16:29 alexis
"""
)

s4 = (dirstring,
    ("-2:",":"),"""
drwxr-xr-x - oldalexis 2023-09-17 14:13 alexis_1
drwxrwxrwt - root      2024-11-21 12:25 Shared
"""
)

s5 = (dirstring,
    ("-2","-3:-1"),"""
2023-09-17 14:13
"""
)

def f(s): return s[1:] if s[0]=='\n' else s
def g(t): return (f(t[0]),t[1],f(t[2]))

tests:list[tuple] = [g(x) for x in [s0,s1,s2,s3,s4,s5]]

@pytest.mark.parametrize("pidx", list(range(len(tests))))
def test_run(pidx:int):
    s = tests[pidx]
    lines = list(line for line in s[0].splitlines())
    actual = list(pick(lines,s[1][0],s[1][1]))
    expected = list(s[2].splitlines())
    assert actual == expected

def test_parse_slices():
    from pick import parse_slice_spec
    assert parse_slice_spec("5")     == (5  ,6)
    assert parse_slice_spec("0")     == (0  ,1)
    assert parse_slice_spec("-5")    == (-5 ,-4)
    assert parse_slice_spec("1:1")   == (1  ,1)
    assert parse_slice_spec("5:")    == (5  ,float('inf'))
    assert parse_slice_spec("-5:-2") == (-5 ,-2)
    assert parse_slice_spec("-5:")   == (-5 ,float('inf'))
    assert parse_slice_spec(":-5")   == (0  ,-5)
    
