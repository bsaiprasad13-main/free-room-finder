# Tasks: Jan–May 2027 semester update

Goes with [spec.md](spec.md) and [design.md](design.md). Status: **built**, waiting on semester dates (Q2) and your merge.

## 0. Your answers needed (spec "Open questions")
- [x] Q1 Slot chart is the same as the image you shared
- [ ] Q2 First and last class day of Jan–May 2027 (**still needed**)
- [x] Q3 DoMS slot chart (or OK to leave DOMS rooms + CRC101 out); GH/GM/GT/GW = slot G?
- [x] Q4 List or leave out MES 200, HTTP 200B, NCCR308, PH 263
- [x] Q5 Jan–May 2026 course list, if you can get it (optional, fills `NA`/`Other` gaps)

## 1. Script (`scripts/build_timetable.py`)
- [x] Add `--semester` (required) and `--starts`/`--ends` (optional); write the `semester` object into `timetable.json`
- [x] Map GH/GM/GT/GW to G in `on_grid()`
- [x] Leave out rooms used by DoMS-slot courses; list them in the summary
- [x] Update the docstring and usage example
- [x] Check: feeding the current data through the writer still reproduces it byte for byte (apart from the new `semester` line)

## 2. Complaints
- [x] Empty `reported_occupied.json` (Jul–Nov entries deleted, per your decision)

## 3. Build the data
- [x] Run the script on `SlotWise_SubjectWise List__2026-11-21.xlsx` (121 rooms, 18 buildings)
- [ ] Re-run with `--starts`/`--ends` once you send the dates
- [x] Review the summary: rooms left out, rows dropped, codes skipped
- [x] Spot checks: CY1001 (C, RJN 101–302), EE1100 (E, RJN 101/102), CRC305 at all G times are busy; no DOMS room or CRC101 listed

## 4. Page (`index.html`)
- [x] Semester pill in the header (`.sem-pill`), from `timetable.json`
- [x] Amber notice under the header, before/after the semester dates only
- [x] Read Me line naming the semester
- [x] Footer fallback count updated to the new room count

## 5. Test
- [x] At 375px and desktop: the pill fits next to "Free Rooms" with no overlap and no horizontal scroll
- [x] Notice shows before `starts`, hides during the semester, shows after `ends` (by faking today's date in the browser)
- [x] With an old `timetable.json` (no `semester` field): no pill, no notice, no errors
- [x] Range search, building chips (new: CB, NAC; DOMS absent), free-until labels and search still work
- [x] No console errors

## 6. Ship
- [x] Branch from `main`, commit, open a PR with the build summary and spot checks
- [ ] **You** merge after the Jul–Nov semester's last class day
- [ ] After merge: check freerooms.onslate.in shows the new pill and data (open it twice, because of the offline fallback)
