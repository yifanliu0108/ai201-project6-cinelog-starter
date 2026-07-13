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

**What I did:** I followed the `add_to_collection()` pattern by querying for an
existing `WatchlistEntry` with the same `user_id` and `film_id` after validating
that the film exists but before creating a new entry. If a match is found,
`add_to_watchlist()` raises the watchlist-specific
`AlreadyInWatchlistError`. This makes duplicate handling explicit and prevents
the second insert and commit from running.

**How I verified:** I compared the order and query fields against
`add_to_collection()` and ran the full existing test suite after the change;
all four tests passed. I also added a focused duplicate-add test in the
watchlist test commit, which calls the function twice and verifies both the
exception and that only one database row remains.

## Comment 3 — Missing test

**What I did:** I created `tests/test_watchlist.py` using the isolated in-memory
application, database setup, and fixture structure from `tests/test_collection.py`.
The required test passes an all-zero UUID that is absent from the database and
asserts that `add_to_watchlist()` raises `FilmNotFoundError`, rather than
allowing a database integrity error to occur.

**How I verified:** I used
`test_add_to_collection_nonexistent_film_raises` as the direct model. Running
`python -m pytest tests/test_watchlist.py -v` passed both watchlist tests, and
running `python -m pytest tests/ -v` passed all six project tests.

## Stretch — Duplicate watchlist test

I added a second watchlist test for duplicate additions because deduplication
is the new behavior introduced in response to Comment 2 and was otherwise not
covered by the starter suite. The test adds the same film twice, expects
`AlreadyInWatchlistError` on the second call, and confirms that exactly one
`WatchlistEntry` remains in the database.

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
