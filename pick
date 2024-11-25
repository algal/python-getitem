#!/usr/bin/env python3

import sys
import re
from collections import deque

def usage():
    print("Usage: {} [--onebased | -o | -u] ROW COLUMN".format(sys.argv[0]))
    print("")
    print("Filter stdin and print specific rows and columns, specifying")
    print("them in Python's slicing syntax.")
    print("Optionally, can use one-based indexes, unlike Python.")
    print("")
    print("For example:")
    print("cat myfile | ./pick :5 0     # Print the column 0 of the first 5 rows.")
    print("cat myfile | ./pick 0 :      # Print the first row, all of it.")
    print("cat myfile | ./pick -o 1 :   # Print the first row, all of it.")
    print("cat myfile | ./pick -10 0:2  # Print the first 2 columns of the last 10 rows.")
    print("cat myfile | ./pick -2:-1 : # Prints all fields of the second to last row.")
    print("")
    sys.exit(1)

def parse_input(value,decr_pos=False):
    "parses value into an int, or an int:Optional[int] slice"
    retval = None
    if ":" in value:
        start, end = value.split(":")
        retval = slice(int(start.strip()) if start.strip() else 0,
                     int(end.strip()) if end.strip() else None)
    else:
        retval = int(value)
    if not decr_pos:
      return retval
    else:
      def decr_pos(i): return (i-1) if (isinstance(i, int) and i > 0) else i
      
      if isinstance(retval, int):
        return decr_pos(retval)
      elif isinstance(retval, slice):
        return slice(decr_pos(retval.start),decr_pos(retval.stop))
      else:
        print('unreachable')
        sys.exit(1)

def split_with_positions(input_str, pattern):
    return [(match.group(), match.start(), match.end()) for match in re.finditer(pattern, input_str)]

def print_filtered_line(line, col):
    "col : a slice or int"
    line = line.rstrip()
    fields = split_with_positions(line, r'\S+|\s+')
    non_space_fields = [field for field in fields if not field[0].isspace()]
    if not non_space_fields:
        print()
        return
    if isinstance(col, slice):
        start_pos = non_space_fields[col.start][1] if col.start is not None else 0
        end_pos = non_space_fields[col.stop-1][2] if col.stop is not None else len(line)
        print(line[start_pos:end_pos])
    else:
        print(non_space_fields[col][0])

def apply_filters(i, row, col, line):
    "Filters and prints fields of the ith row. i>=0."
    if isinstance(row, slice):
        start, stop = row.start if row.start else 0, row.stop if row.stop else float('inf')
        if start <= i < stop:
            # Bug: this join transforms all whitespace separations into spaces
            print_filtered_line(line,col)
    elif i == row:
        print_filtered_line(line,col)

def main():
    onebased = False
    if "--onebased" in sys.argv:
        onebased = True
        sys.argv.remove("--onebased")
    if "-o" in sys.argv:
        onebased = True
        sys.argv.remove("-o")
    if "-u" in sys.argv:
        onebased = True
        sys.argv.remove("-u")

    if len(sys.argv) != 3:
        usage()

    row = parse_input(sys.argv[1],onebased)
    column = parse_input(sys.argv[2],onebased)

    buffer = None
    if isinstance(row, int) and row < 0:
        buffer = deque(maxlen=abs(row))
    elif isinstance(row,slice) and row.start < 0:
        buffer = deque(maxlen=abs(row.start))

    for i, line in enumerate(sys.stdin):
        if buffer is not None:
            buffer.append((i, line))
        else:
            apply_filters(i, row, column, line)

    if buffer is not None:
        lastrow = buffer[-1][0]
        if isinstance(row,int):
            row = lastrow + 1 + row
        else:
            row = slice(lastrow + 1 + row.start, row.stop)
        for i, line in buffer:
            apply_filters(i, row, column, line)

if __name__ == "__main__":
    main()
