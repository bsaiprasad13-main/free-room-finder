"""Build timetable.json from the college's "SlotWise_SubjectWise List" downloads.

Usage (from the repo root):
    python scripts/build_timetable.py "path/to/SlotWise_SubjectWise List*.xlsx" ...

Pass every department's .xlsx file (globs are fine). Only the Python standard
library is needed. timetable.json is overwritten and a summary of what was
skipped is printed, so check it before committing.

How a room is decided to be free:
  * Every course row names a Slot, an optional AdditionalSlot and a RoomNo.
    Rows with no slot or no room are dropped.
  * GRID below (the institute slot chart) gives the times each slot meets.
    AdditionalSlot codes block their times too. Codes like A1 or D2 that aren't
    on the chart block all of their base letter's times. Codes with no time on
    the chart (PP, UU, XX, NT, ...) are skipped.
  * A room is free in a slot when no course uses it then. Only rooms named in
    the files are listed. Labs and halls without a room number are left out.
  * 14:00-16:45 lists rooms free in both afternoon halves.
"""
import glob
import json
import re
import sys
import xml.etree.ElementTree as ET
import zipfile
from collections import Counter
from pathlib import Path

OUT = Path(__file__).resolve().parent.parent / 'timetable.json'

# (label, start, end) in minutes; the order matches GRID columns
TIMES = [('8:00–8:50', 480, 530), ('9:00–9:50', 540, 590), ('10:00–10:50', 600, 650),
         ('11:00–11:50', 660, 710), ('13:00–13:50', 780, 830), ('14:00–15:15', 840, 915),
         ('15:30–16:45', 930, 1005), ('17:00–17:50', 1020, 1070)]
GRID = {
    'Monday':    ['A', 'B', 'C', 'D', 'G', 'H H1 P', 'M M2 P', 'J J3'],
    'Tuesday':   ['B', 'C', 'D', 'E', 'A', 'M M1 Q', 'H H2 Q', 'F'],
    'Wednesday': ['C', 'D', 'E', 'F', 'B', 'J J1 R', 'K K2 R', 'G'],
    'Thursday':  ['E', 'F', 'G', 'A', 'D', 'L L1 S', 'J J2 S', 'H H3'],
    'Friday':    ['F', 'G', 'A', 'B', 'C', 'K K1 T', 'L L2 T', 'E'],
}
ON_GRID = {code for row in GRID.values() for cell in row for code in cell.split()}

NS = {'m': 'http://schemas.openxmlformats.org/spreadsheetml/2006/main',
      'r': 'http://schemas.openxmlformats.org/officeDocument/2006/relationships'}


def read_rows(path):
    """First sheet of an .xlsx as a list of dicts keyed by the header row."""
    z = zipfile.ZipFile(path)
    shared = []
    if 'xl/sharedStrings.xml' in z.namelist():
        for si in ET.fromstring(z.read('xl/sharedStrings.xml')).findall('m:si', NS):
            shared.append(''.join(t.text or '' for t in si.iter('{%s}t' % NS['m'])))
    rels = {r.get('Id'): r.get('Target') for r in ET.fromstring(z.read('xl/_rels/workbook.xml.rels'))}
    sheet = ET.fromstring(z.read('xl/workbook.xml')).find('m:sheets', NS)[0]
    target = rels[sheet.get('{%s}id' % NS['r'])].lstrip('/')
    rows = []
    for row in ET.fromstring(z.read(target if target.startswith('xl/') else 'xl/' + target)).iter('{%s}row' % NS['m']):
        vals = {}
        for c in row.findall('m:c', NS):
            col = 0
            for ch in re.match(r'[A-Z]+', c.get('r')).group():
                col = col * 26 + ord(ch) - 64
            v = c.find('m:v', NS)
            if c.get('t') == 's' and v is not None:
                vals[col - 1] = shared[int(v.text)]
            elif c.get('t') == 'inlineStr':
                vals[col - 1] = ''.join(t.text or '' for t in c.iter('{%s}t' % NS['m']))
            else:
                vals[col - 1] = v.text if v is not None else None
        rows.append([vals.get(i) for i in range(max(vals) + 1)] if vals else [])
    header = rows[0]
    return [dict(zip(header, r + [None] * (len(header) - len(r)))) for r in rows[1:] if any(r)]


def room_names(raw):
    """'ESB 106, ESB 127' -> ['ESB106', 'ESB127']; 'NAC II 238' -> ['NACII238'].

    A number after a comma reuses the previous building ('RMN 101, 102').
    Bare numbers, labs and halls ('531', 'CAE LAB', 'DCIF') give nothing.
    """
    names, bldg = [], None
    for part in re.split(r'[,+]', (raw or '').upper()):
        part = re.sub(r'\bNAC[\s-]*II\b', 'NACII', part)
        for m in re.finditer(r'([A-Z]+)?[\s-]*(\d+[A-Z]?)\b', part):
            bldg = m.group(1) or bldg
            if bldg:
                names.append(bldg + m.group(2))
    return names


def slot_codes(text):
    return [c for c in re.split(r'[\s,]+', (text or '').strip().upper()) if c]


def on_grid(code, skipped):
    """Map a slot code to grid codes: as-is, or A1 -> A. Unplaceable codes are counted."""
    if code in ON_GRID:
        return [code]
    m = re.fullmatch(r'([A-Z])\d', code)
    if m and m.group(1) in ON_GRID:
        return [m.group(1)]
    skipped[code] += 1
    return []


def to_json(buildings, days):
    """Same layout as before: one line per slot, so diffs stay readable."""
    compact = lambda v: json.dumps(v, ensure_ascii=False, separators=(',', ':'))
    day_blocks = []
    for day, slots in days.items():
        lines = ',\n'.join('      ' + compact(s) for s in slots)
        day_blocks.append(f'    {compact(day)}: [\n{lines}\n    ]')
    return ('{\n'
            f'  "buildings": {compact(buildings)},\n'
            '  "days": {\n' + ',\n'.join(day_blocks) + '\n  }\n}\n')


def main(patterns):
    files = sorted({f for p in patterns for f in glob.glob(p)})
    if not files:
        sys.exit('No .xlsx files matched. Pass the SlotWise_SubjectWise List downloads.')
    busy = {}                      # room -> set of (day, column) it is in use
    rooms = set()
    dropped, skipped, unnamed = 0, Counter(), Counter()
    for f in files:
        for row in read_rows(f):
            slots = slot_codes(row.get('Slot'))
            names = room_names(row.get('RoomNo'))
            if not slots or not names:
                dropped += 1
                if slots and (row.get('RoomNo') or '').strip().strip('-'):
                    unnamed[row['RoomNo'].strip()] += 1
                continue
            rooms.update(names)
            codes = {g for c in slots + slot_codes(row.get('AdditionalSlot')) for g in on_grid(c, skipped)}
            for day, cells in GRID.items():
                for col, cell in enumerate(cells):
                    if codes & set(cell.split()):
                        for r in names:
                            busy.setdefault(r, set()).add((day, col))

    ordered = sorted(rooms, key=lambda r: (re.match(r'[A-Z]+', r).group(), int(re.search(r'\d+', r).group()), r))
    days = {}
    for day in GRID:
        free = [[r for r in ordered if (day, col) not in busy.get(r, ())] for col in range(len(TIMES))]
        slots = [{'time': t, 'start': s, 'end': e, 'rooms': free[col]} for col, (t, s, e) in enumerate(TIMES)]
        # 14:00-16:45: free in both afternoon halves, listed before them like before
        both = [r for r in free[5] if r in free[6]]
        slots.insert(5, {'time': '14:00–16:45', 'start': 840, 'end': 1005, 'rooms': both})
        days[day] = slots
    buildings = sorted({re.match(r'[A-Z]+', r).group() for r in ordered})
    OUT.write_text(to_json(buildings, days), encoding='utf-8', newline='\n')

    print(f'Read {len(files)} files. Wrote {OUT.name}: {len(ordered)} rooms in {len(buildings)} buildings.')
    print(f'Dropped {dropped} rows with no slot or no room.')
    if unnamed:
        print('Rooms without a building and number (left out):', dict(unnamed.most_common()))
    if skipped:
        print('Slot codes with no time on the grid (skipped):', dict(skipped.most_common()))


if __name__ == '__main__':
    main(sys.argv[1:])
