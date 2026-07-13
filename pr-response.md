# PR Response Doc — CineLog Watchlist Feature

## AI Usage

I used Codex as an orientation and verification aid while working through the
review. It helped me understand the repository structure, interpret the
existing collection-service and test patterns, navigate Git and VS Code, and
check the working tree and test results. I verified its explanations against
the source code. I will make the product decisions for Comments 4 and 5 myself
and update this section at the end with any additional AI use.

## Comment 1 — Rename

**What I did:** I renamed `save_to_watchlist()` to `add_to_watchlist()` in
`services/watchlist_service.py` so that it follows CineLog's established
`verb_to_noun` naming convention, as demonstrated by `add_to_collection()`.
I also updated the function's docstring and both call sites in
`routes/watchlist/watchlist.py`: the service import and the call made by the
`add_film()` route.

**How I verified:** I performed a project-wide search for both function names.
The old name returned no results, while the new name appeared in exactly the
service definition, route import, and route call. I then ran
`python -m pytest tests/ -v`; all four existing tests passed.

## Comment 2 — Deduplication

**What I did:** Pending. I will follow the `add_to_collection()` pattern to
check for an existing `WatchlistEntry` with the same `user_id` and `film_id`
before creating a new entry, and raise a watchlist-specific error when a
duplicate is found.

**How I verified:** Pending until the implementation is complete.

## Comment 3 — Missing test

**What I did:** Pending. I will add `tests/test_watchlist.py` with a test that
confirms `add_to_watchlist()` raises `FilmNotFoundError` when the supplied film
ID is not present in the database.

**How I verified:** Pending until the test is written and run.

## Comment 4 — Default visibility

**My position:** Pending — I will make and document this design decision after
finishing Comments 1–3.

**Reasoning:** Pending.

**Tradeoff acknowledged:** Pending.

## Comment 5 — Sort order

**My position:** Pending — I will make and document this design decision after
finishing Comments 1–3.

**Reasoning:** Pending.

**Engagement with reviewer's point:** Pending.

## Comment 6 — Rebase

**What conflicted:** Pending until the feature branch is rebased on the updated
`main` branch.

**How I resolved it:** Pending.

**How I verified no conflict remains:** Pending.

## PR Description

Pending final completion. The final description will summarize the watchlist
feature, the visibility and sort-order decisions, the rebase and UUID conflict
resolution, and the manual and automated verification steps.
