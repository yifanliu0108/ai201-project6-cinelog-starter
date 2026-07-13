"""Tests for the watchlist service."""

import pytest

from app import create_app, db
from models import Film, User, WatchlistEntry
from services.collection_service import FilmNotFoundError
from services.watchlist_service import (
    AlreadyInWatchlistError,
    add_to_watchlist,
    get_watchlist,
)


@pytest.fixture
def app():
    """Create an isolated test app with an in-memory database."""
    app = create_app(config={
        "TESTING": True,
        "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
    })
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture
def sample_user(app):
    """Create a user for watchlist tests."""
    with app.app_context():
        user = User(username="watcher", email="watcher@example.com")
        db.session.add(user)
        db.session.commit()
        return user.id


@pytest.fixture
def sample_film(app):
    """Create a film for watchlist tests."""
    with app.app_context():
        film = Film(title="Moonlight", year=2016, genre="Drama")
        db.session.add(film)
        db.session.commit()
        return film.id


def test_add_to_watchlist_nonexistent_film_raises(app, sample_user):
    """Adding a nonexistent film should raise FilmNotFoundError."""
    with app.app_context():
        fake_film_id = "00000000-0000-0000-0000-000000000000"

        with pytest.raises(FilmNotFoundError):
            add_to_watchlist(user_id=sample_user, film_id=fake_film_id)


def test_add_to_watchlist_duplicate_raises(app, sample_user, sample_film):
    """Adding the same film twice should leave only one watchlist entry."""
    with app.app_context():
        add_to_watchlist(user_id=sample_user, film_id=sample_film)

        with pytest.raises(AlreadyInWatchlistError):
            add_to_watchlist(user_id=sample_user, film_id=sample_film)

        count = WatchlistEntry.query.filter_by(
            user_id=sample_user, film_id=sample_film
        ).count()
        assert count == 1


def test_get_watchlist_returns_newest_first(app, sample_user):
    """The most recently added watchlist film should be returned first."""
    with app.app_context():
        from datetime import datetime, timedelta, timezone

        earlier_film = Film(title="Arrival", year=2016, genre="Sci-Fi")
        later_film = Film(title="Zodiac", year=2007, genre="Thriller")
        db.session.add_all([earlier_film, later_film])
        db.session.commit()

        earlier = datetime.now(timezone.utc) - timedelta(days=5)
        later = datetime.now(timezone.utc)
        db.session.add_all([
            WatchlistEntry(
                user_id=sample_user,
                film_id=earlier_film.id,
                date_added=earlier,
            ),
            WatchlistEntry(
                user_id=sample_user,
                film_id=later_film.id,
                date_added=later,
            ),
        ])
        db.session.commit()

        watchlist = get_watchlist(sample_user)
        titles = [film["title"] for film in watchlist]

        assert titles == ["Zodiac", "Arrival"]
