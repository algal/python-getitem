#!/usr/bin/env python3
import sys, re, getopt, pathlib
from collections import deque
from collections.abc import Iterable

def parse_slice_spec(slice_spec:str,should_decr_pos:bool=False) -> tuple:
    "parses value into an (int,int)"
    if ":" in slice_spec:
        beg,end = tuple(slice_spec.split(":"))
        beg = 0 if beg=='' else int(beg)
        end = float('inf') if end=='' else int(end)
    else:
        beg = int(slice_spec)
        end = beg + 1 if beg!=-1 else float('inf')
    return (beg,end)

def split_with_positions(str_to_split, pattern):
    "Returns [(s,beg,end)] for the substrings in between the pattern"
    result = []
    last_end = 0
    for match in re.finditer(pattern, str_to_split):
        if match.start() > last_end:
            result.append((str_to_split[last_end:match.start()], last_end, match.start()))
        last_end = match.end()
    if last_end < len(str_to_split):
        result.append((str_to_split[last_end:], last_end, len(str_to_split)))
    return result

def filtered_line(line:str, col_spec: str) -> str | None:
    "col : a slice or int"
    eol_to_preserve = "\n" if line.endswith("\n") else ""
    fields = split_with_positions(line, r'\s+')
    sliced_fields = list(islice(fields,col_spec))
    if not sliced_fields: return None
    col = parse_slice_spec(col_spec)
    start_pos = sliced_fields[  0 ][1]
    end_pos   = sliced_fields[ -1 ][2]
    fl = (" " * start_pos) + line[start_pos:end_pos] + eol_to_preserve
    return fl

def pick(lines:Iterable[str],row_spec:str,col_spec:str,line_count=None) -> Iterable[str]:
    out_lines = islice(lines,row_spec,iterable_len=line_count)
    for line in out_lines:
        out = filtered_line(line,col_spec)
        if out: yield out

def islice(iterable,slice_spec:str,iterable_len=None) -> Iterable:
    """
    slice_spec, a str of an index or a splice, like '-5:' etc..

    Consumes iterable once. Maintains a buffer if necessary.
    """
    (beg,end) = parse_slice_spec(slice_spec)
    if hasattr(iterable,'__len__'): iterable_len = len(iterable)
    if iterable_len is not None:
        beg = (beg + iterable_len) if (beg<0) else beg
        end = (end + iterable_len) if (end<0) else end
    if beg < 0:
        buf = deque(maxlen=abs(beg))
    elif end < 0:
        buf = deque()
    else:
        buf = None
    if buf is None:
        src = enumerate(iterable)
    else:
        lastrow = 0
        for i,line in enumerate(iterable):
            buf.append((i,line))
            lastrow = i
        (beg,end) = tuple([x if x>=0 else x+1+lastrow for x in (beg,end)])
        src = buf
    for i,line in src:
        if beg <= i and i < end:
            yield line

def usage():
    epilog="""
    Usage: program [-h] [-f FILE] row_spec col_spec

    Filter stdin and print specific rows and columns, specifying
    them in Python's slicing syntax.
    
    For example:
    cat myfile | ./pick :5 0     # Print the column 0 of the first 5 rows.
    cat myfile | ./pick 0 :      # Print the first row, all of it.
    cat myfile | ./pick -10 0:2  # Print the first 2 columns of the last 10 rows.
    cat myfile | ./pick -2:-1 : # Prints all fields of the second to last row.
    """
    print(epilog)

def main():
    args = sys.argv[1:]
    input_file = None
    remaining_args = []
    
    i = 0
    while i < len(args):
        if args[i] in ('-h', '--help'):
            usage()
            sys.exit(0)
        elif args[i] in ('-f', '--file'):
            if i + 1 < len(args):
                input_file = args[i + 1]
                i += 2
                continue
            else:
                print("Error: -f/--file requires a value")
                sys.exit(2)
        remaining_args.append(args[i])
        i += 1
    if len(remaining_args[:2]) < 2:
        usage()
        sys.exit(1)
    (row,col) = tuple(remaining_args[:2])
    if (p:=input_file):
        line_count = sum(1 for _ in open(p))
        in_lines = iter(open(p))
    else:
        line_count = None
        in_lines = (line for line in sys.stdin)
    out_lines = pick(in_lines, row, col,line_count=line_count)
    for line in out_lines:
        print(line,end="")

if __name__ == "__main__":
    main()
