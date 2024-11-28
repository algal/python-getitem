#!/usr/bin/env python3
import sys, re, argparse
from collections import deque
from collections.abc import Iterable

def parse_slice_spec(slice_spec:str,should_decr_pos:bool=False) -> slice:
    "parses value into an (int,int)"
    if ":" in slice_spec:
        beg,end = tuple(slice_spec.split(":"))
        beg = 0 if beg=='' else int(beg)
        end = float('inf') if end=='' else int(end)
    else:
        beg = int(slice_spec)
        end = beg + 1 if beg!=-1 else float('inf')
    return slice(beg,end)

def split_with_positions(str_to_split, pattern):
    "Returns (s,beg,end) for every substring in between the split"
    result = []
    last_end = 0
    for match in re.finditer(pattern, str_to_split):
        if match.start() > last_end:
            result.append((str_to_split[last_end:match.start()], last_end, match.start()))
        last_end = match.end()
    if last_end < len(str_to_split):
        result.append((str_to_split[last_end:], last_end, len(str_to_split)))
    return result

def filtered_line(line:str, col: slice) -> str | None:
    "col : a slice or int"
    line = line.rstrip()
    fields = split_with_positions(line, r'\s+')
    if not fields:
        return None
    start_pos = fields[col.start][1]
    end_pos   = fields[col.stop-1][2] if col.stop != float('inf') else len(line)
    return line[start_pos:end_pos]

def pick(lines:Iterable[str],row_spec:str,col_spec:str) -> Iterable[str]:
    column = parse_slice_spec(col_spec)
    out_lines = super_islice(lines,row_spec)
    for line in out_lines:
        out = filtered_line(line,column)
        if out: yield out

def super_islice(iterable,slice_spec:str) -> Iterable:
    """
    slice_spec, a str of an index or a splice, like '-5:' etc..

    Consumes iterable once. Maintains a buffer if necessary.
    """
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
    parser = argparse.ArgumentParser(formatter_class=argparse.RawTextHelpFormatter,
#    usage='%(prog)s [-h] [-f FILE] row_slice column_slice'
    usage='%(prog)s [-h] row_slice column_slice'
#    parser.add_argument("-f","--file", help="Input file path")
    # convoluted parsing needed to allow positional arguments which start with HYPHEN-MINUS
    parser.add_argument("row_col_specs", nargs=argparse.REMAINDER, help="Row and column specifications")
    parser.epilog="""
    Filter stdin and print specific rows and columns, specifying
    them in Python's slicing syntax.
    
    For example:
    cat myfile | ./pick :5 0     # Print the column 0 of the first 5 rows.
    cat myfile | ./pick 0 :      # Print the first row, all of it.
    cat myfile | ./pick -10 0:2  # Print the first 2 columns of the last 10 rows.
    cat myfile | ./pick -2:-1 : # Prints all fields of the second to last row.
    """
    args = parser.parse_args()

    if len(args.row_col_specs) != 2:
        parser.error("Must provide a row_slice and a column_slice spec")
    row, column = args.row_col_specs

    in_lines = (line for line in sys.stdin)
    out_lines = pick(in_lines, args.row, args.column)
    for line in out_lines:
        print(line)

if __name__ == "__main__":
    main()
