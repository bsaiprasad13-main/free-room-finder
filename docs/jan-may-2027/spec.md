# Spec: Jan–May 2027 semester update

Status: **built** (branch `jan-may-2027`). Semester dates still to come.

## Decisions (Nov 21)
- Q1 Slot chart: **same** as Jul–Nov.
- Q2 Semester dates: **not given yet.** Built without them: the pill shows, and the dated notice appears once `--starts/--ends` are passed.
- Q3 DoMS: **leave the DOMS rooms out** (and CRC101, which a DoMS-slot course uses). GH/GM/GT/GW treated as G (default; not confirmed).
- Q4 MES 200, HTTP 200B, NCCR308, PH 263: **left out** (default; not confirmed as classrooms).
- Q5 No Jan–May 2026 list; no gap-filling.
- Jul–Nov data is **not kept**: its complaints were deleted, not archived (replaces R1.6's "archived").

## Goals

1. Switch Free Rooms to the **Jan–May 2027** course list (`SlotWise_SubjectWise List__2026-11-21.xlsx`).
2. Show **which semester** the timetable is for, so students know what they're looking at.
3. Keep the main rule: **never show an occupied room as free.** When unsure, show it as busy.

## What the new course list contains

| | Jul–Nov 2026 (live now) | Jan–May 2027 (new) |
|---|---|---|
| Files | 19, one per department | 1, all 26 departments |
| Course rows | 1,343 | 1,187 |
| Different courses | 1,006 | 917 (145 also run in Jul–Nov) |
| Rows with no usable room | 767 | 371 (`NA` 171, `Other` 132, halls/labs, bare numbers) |
| Rooms named | 103 | 132 before the decisions below |

New in this list:
- **DOMS building** (DOMS 101, 104, 251–253, 401). Its courses use **DoMS-only slots** (ML, MP–MZ) that aren't on the slot chart.
- **NAC II 2xx/3xx rooms** and **NAC 631–633** return. **CB 150/218/250/321** return.
- A few rooms that may not be classrooms: MES 200, HTTP 200B, NCCR308, PH 263.

## Requirements

### R1. Data
- R1.1 `timetable.json` is built only from the Jan–May 2027 list, using the same rules as now: slot chart, AdditionalSlot blocks too, A1-style codes block their base letter, rows with no room or slot are dropped.
- R1.2 The Jul–Nov list is **not** used to fill gaps. Only 145 courses carry over, so it would block the wrong rooms.
- R1.3 Courses in **DoMS slots** (ML, MP–MZ) meet at fixed times that aren't on the slot chart. **Rooms they use are left out of the app** (DOMS 101/104/251/252/253/401 and CRC101), because the app would wrongly show them free. If you get the DoMS chart, they can come back. (New rule.)
- R1.4 **GH, GM, GT, GW** count as slot **G** and block all of G's times. Today's script skips them. (New rule.)
- R1.5 Project and special-topics codes with no class time (UU, VV, WW, XX, YY, ZZ, X, Y, Z, N, NT, MM, PP–TT) don't block anything, as today.
- R1.6 Jul–Nov complaints (`reported_occupied.json`) are **archived, not applied.** They describe last semester's classes.
- R1.7 The semester name and dates are stored **in `timetable.json`**, so the label can never disagree with the data.

Expected result: about **125 rooms** (132 named, minus the 7 in R1.3), before decisions on the non-classrooms in Q4.

### R2. Semester label
- R2.1 The page shows the semester name (for example "Jan–May 2027") at all times.
- R2.2 **Outside the semester dates**, an amber notice says the timetable may not match current classes:
  - Before the start: "Timetable for Jan–May 2027 · classes start 2 Jan".
  - After the end: "Jan–May 2027 timetable has ended · rooms may be wrong".
- R2.3 The Read Me says which semester the data is for.
- R2.4 It works at 375px phone width with no overlap or horizontal scroll, in the existing dark theme.

### R3. Release timing
- R3.1 Merge **after the Jul–Nov semester's last class day**, so students still in Jul–Nov classes aren't shown Jan–May rooms. Until the semester starts, R2.2 shows the "classes start" notice.

## Out of scope
- Showing two semesters at once, or switching between them.
- Getting rooms for `NA`/`Other` courses from outside the course list.
- Changes to the range search, free-until labels or building filters, beyond new building chips appearing.

## Acceptance criteria
- No DOMS room and not CRC101 is listed (R1.3). The build summary names the rooms it left out and why.
- Spot checks: CY1001 (slot C, RJN 101–302) and EE1100 (slot E, RJN 101/102) are busy at every one of their slot times. CRC305 is busy at all G times (R1.4).
- No Jul–Nov complaint is applied (R1.6).
- The semester label shows on phone and desktop. The amber notice appears when the date is outside the semester and is hidden inside it (tested by setting the date).
- No console errors. Range search, filters and free-until labels still work.

## Open questions (need your answers)
1. **Slot chart:** is the Jan–May 2027 chart the same as the image you shared (A = Mon 8, Tue 13, Thu 11, Fri 10, …)?
2. **Semester dates:** first and last class day of Jan–May 2027, from the academic calendar.
3. **DoMS:** do you have the DoMS slot chart (ML, MP–MZ)? With it, the DOMS rooms and CRC101 can be listed. Without it, they're left out (R1.3). Also: is it right that GH/GM/GT/GW are variants of slot G (R1.4)?
4. **Non-classrooms:** list or leave out MES 200, HTTP 200B, NCCR308 and PH 263?
5. **Gaps:** 303 rows have `NA`/`Other`, including PH1010 Physics I. If you can get the **Jan–May 2026** list (the same courses ran then), it could fill these gaps the way July filled October's.
