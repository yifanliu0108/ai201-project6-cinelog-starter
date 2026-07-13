# PR Response Doc — CineLog Watchlist Feature

## AI Usage

I used Codex as an orientation and verification aid while working through the
review. It helped me understand the repository structure, interpret the
existing collection-service and test patterns, navigate Git and VS Code, run
the test suite, and check the commit history. I verified its explanations
against the source code. I also used it to stress-test the reasoning for
Comments 4 and 5. It raised the privacy cost of a public default and the
scanability benefit of alphabetical ordering; I incorporated those as explicit
tradeoffs rather than treating either decision as cost-free. The final
positions are grounded in CineLog's community focus, the fields actually
returned by `get_watchlist()`, and the existing newest-first collection order.

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

**My position:** Keep `public=True` as the default, but treat an explicit
visibility control as an important follow-up rather than assuming all users are
comfortable sharing indefinitely.

**Reasoning:** CineLog is a community film-tracking application, and a
watchlist has social value when friends can discover shared interests and make
recommendations. A public default makes that value available without requiring
every new user to understand and configure a visibility setting first. The
current watchlist response exposes film information, the date added, and the
visibility flag; it does not expose private notes or ratings. For this product,
I am optimizing for low-friction discovery and useful profiles while keeping
the default consistent with the model already introduced by this feature.

**Tradeoff acknowledged:** A watchlist can still reveal personal interests, so
public-by-default has a real consent and privacy cost even without notes or
ratings. A private default would better protect users who never inspect their
settings, at the cost of making CineLog's community features feel empty. The
current add endpoint also does not expose the existing `public` field, which
makes the public default harder to override than it should be. A follow-up
should clearly communicate visibility and allow callers to choose it when an
entry is created; until then, the default must be documented rather than
treated as accidental behavior.

## Comment 5 — Sort order

**My position:** I accepted the maintainer's preference and changed the default
watchlist order from alphabetical to `date_added` descending (newest first).

**Reasoning:** A CineLog watchlist represents future intent rather than an
archival catalog. The films a user added most recently are likely to reflect
what they currently want to watch, so surfacing them first reduces the effort
needed to choose something. Newest-first also matches `get_collection()`, which
already orders entries by `date_added` descending, giving the two user-film
lists a consistent time-oriented default. I updated the query, documented the
behavior in its docstring, and added a test with deliberately non-alphabetical
titles to prove that timestamps—not titles—control the result.

**Engagement with reviewer's point:** The reviewer is right that recent intent
is the stronger default for the common "what did I just save?" workflow.
Alphabetical order remains easier when a user remembers a title and wants to
scan a long list, and it is deterministic even when timestamps are close. On
balance, that lookup benefit is better handled by search or an explicit sort
option than by making every user lose recency as the default. I therefore
changed the server response to newest-first while recognizing alphabetical as
a useful future client option.

## Comment 6 — Rebase

**What conflicted:** I fetched my fork and rebased `feature/watchlist` onto
`origin/main`. Git reported an add/add conflict in `.gitignore` because both
branches had introduced the file. The more important semantic conflict was in
the model state: main's refactor migrated `Film.id` and
`CollectionEntry.film_id` to UUID strings and removed the pre-refactor
`WatchlistEntry`, while the rebased watchlist service still imported and used
that model. Its service and route documentation also still described film IDs
as integers.

**How I resolved it:** For `.gitignore`, I kept the common generated-file rules
and main's additional `.pytest_cache/` rule. I preserved main's UUID
implementation and restored `WatchlistEntry` with a UUID primary key and a
`db.String(36)` UUID foreign key to `film.id`; I did not restore the old integer
column. I retained the Film-to-watchlist relationship needed by
`get_watchlist()` and updated the service and route documentation to describe a
UUID string payload.

**How I verified no conflict remains:** I searched for conflict markers and
stale integer watchlist documentation, confirmed that `origin/main` is an
ancestor of the feature branch, and checked `git log --merges origin/main..HEAD`
for feature-branch merge commits. I also ran the complete test suite against
the rebased code; all seven tests passed, including watchlist creation,
deduplication, nonexistent UUID handling, and newest-first ordering.

## PR Description

### Feature overview

This PR adds a watchlist service and REST endpoints that let a user save films
for later and retrieve their saved films. It validates film UUIDs, prevents a
user from adding the same film twice, returns film metadata with watchlist
metadata, and includes focused service tests for missing films, duplicates, and
sort order. The branch is rebased onto the UUID-based main branch.

### Design decisions

- **Visibility:** Watchlist entries retain `public=True` as the documented
  default to support low-friction sharing and recommendations in CineLog's
  community context. I acknowledge that viewing preferences can be sensitive;
  an explicit visibility control should be added so users can easily opt out.
- **Sort order:** Watchlists now default to `date_added` descending. This treats
  the watchlist as a queue of current viewing intent and matches the existing
  newest-first collection behavior. Alphabetical sorting remains a useful
  future search or client-side option.

### Manual testing

1. Create and activate the environment, install dependencies, and initialize
   the database:

   ```bash
   python -m venv .venv
   source .venv/bin/activate
   python -m pip install -r requirements.txt
   flask --app app:create_app shell
   ```

2. In the Flask shell, create a user and two films, then copy the printed UUIDs:

   ```python
   from app import db
   from models import Film, User

   user = User(username="manual-user", email="manual@example.com")
   film_one = Film(title="Arrival", year=2016, genre="Sci-Fi")
   film_two = Film(title="Moonlight", year=2016, genre="Drama")
   db.session.add_all([user, film_one, film_two])
   db.session.commit()
   print(user.id, film_one.id, film_two.id)
   exit()
   ```

3. Start the API in one terminal:

   ```bash
   python app.py
   ```

4. In another terminal, add each film using the UUIDs printed above:

   ```bash
   curl -X POST http://127.0.0.1:5000/watchlist/<USER_UUID>/add \
     -H "Content-Type: application/json" \
     -d '{"film_id":"<FILM_ONE_UUID>"}'

   curl -X POST http://127.0.0.1:5000/watchlist/<USER_UUID>/add \
     -H "Content-Type: application/json" \
     -d '{"film_id":"<FILM_TWO_UUID>"}'
   ```

5. Retrieve the watchlist and confirm the second film is first because it was
   added most recently:

   ```bash
   curl http://127.0.0.1:5000/watchlist/<USER_UUID>
   ```

6. Run the automated verification:

   ```bash
   python -m pytest tests/ -v
   ```

   Expected result: all seven tests pass.

## Commit history screenshot

The final `git log --oneline origin/main..HEAD` screenshot is included below
after the history cleanup.
