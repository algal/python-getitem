#!/usr/bin/env python3

import sys, re, argparse
from collections import deque
from collections.abc import Iterable

def parse_slice_spec(value:str,should_decr_pos:bool=False) -> int | slice:
    "parses value into an int, or an int:Optional[int] slice"
    retval = None
    if ":" in value:
        start, end = value.split(":")
        retval = slice(int(start.strip()) if start.strip() else 0,
                     int(end.strip()) if end.strip() else None)
    else:
        retval = int(value)
    if not should_decr_pos:
      return retval
    else:
      def decr_pos(i):
          return (i-1) if (isinstance(i, int) and i > 0) else i
      if isinstance(retval, int):
        return decr_pos(retval)
      elif isinstance(retval, slice):
        return slice(decr_pos(retval.start),decr_pos(retval.stop))
      else:
        print('unreachable')
        sys.exit(1)

def split_with_positions(input_str, pattern):
    return [(match.group(), match.start(), match.end()) for match in re.finditer(pattern, input_str)]

def filtered_line(line:str, col: int | slice) -> str | None:
    "col : a slice or int"
    line = line.rstrip()
    fields = split_with_positions(line, r'\S+|\s+')
    non_space_fields = [field for field in fields if not field[0].isspace()]
    if not non_space_fields:
        return None
    if isinstance(col, slice):
        start_pos = non_space_fields[col.start][1] if col.start is not None else 0
        end_pos = non_space_fields[col.stop-1][2] if col.stop is not None else len(line)
        return line[start_pos:end_pos]
    else:
        return non_space_fields[col][0]

def pick(lines:Iterable[str],row_spec:str,col_spec:str) -> Iterable[str]:
    row = parse_slice_spec(row_spec)
    column = parse_slice_spec(col_spec)
    out_lines = super_islice(lines,row_spec)
    for line in out_lines:
        out = filtered_line(line,column)
        if out: yield out

def super_islice(iterable,slice_spec:str) -> Iterable:
    "slice_spec, a str of an index or a splice, like '-5:' etc.."
    if ":" in slice_spec:
        beg,end = tuple(slice_spec.split(":"))
        beg = 0 if beg=='' else int(beg)
        end = float('inf') if end=='' else int(end)
    else:
        beg = int(slice_spec)
        end = beg + 1 if beg!=-1 else float('inf')
    # assert: (beg,end):(+int,+int)
    buf = None
    if beg < 0:
        buf = deque(maxlen=abs(beg))
    elif end < 0:
        buf = deque()
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

def main():
    parser = argparse.ArgumentParser(formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument("row",    type=str, help="Row specification")
    parser.add_argument("column", type=str, help="Column specification")
    parser.prefix_chars=''
    parser.epilog="""
    Filter stdin and print specific rows and columns, specifying
    them in Python's slicing syntax.
    
    For example:
    cat myfile | ./pick :5 0     # Print the column 0 of the first 5 rows.
    cat myfile | ./pick 0 :      # Print the first row, all of it.
    cat myfile | ./pick -o 1 :   # Print the first row, all of it.
    cat myfile | ./pick -10 0:2  # Print the first 2 columns of the last 10 rows.
    cat myfile | ./pick -2:-1 : # Prints all fields of the second to last row.
    """
    args = parser.parse_args()

    in_lines = (line for line in sys.stdin)
    out_lines = pick(in_lines, args.row, args.column)
    for line in out_lines:
        print(line)

if __name__ == "__main__":
    main()
