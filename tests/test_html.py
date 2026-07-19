from datetime import date, datetime, timedelta
from unittest.mock import MagicMock, patch

from bs4 import BeautifulSoup

from friendslist.calendar_helpers import get_events
from friendslist.db import get_addresses_dict, get_all_messages_for_delta, insert_message
from friendslist.generate_calendar import build_calendar_props
from friendslist.html_helpers import render_email_body


def test_render_email_html_end_to_end(db_connection):
    today = datetime(2026, 7, 19, 12, 0, 0)
    start_sunday = date(2026, 7, 19)

    insert_message(
        db_connection,
        today - timedelta(days=1),
        "alice@gmail.com",
        "Weekend plans",
        "Want to hike on Saturday?",
        "<div>Want to hike on Saturday?</div>",
        ["hike.png"],
    )
    insert_message(
        db_connection,
        today - timedelta(days=2),
        "bob@gmail.com",
        "Photos from the trip",
        "Here are a couple shots",
        "<div>Here are a couple shots</div>",
        ["trip1.png", "trip2.png"],
    )
    insert_message(
        db_connection,
        today - timedelta(days=3),
        "alice@gmail.com",
        "Quick hello",
        "No attachments on this one",
        "<div>No attachments on this one</div>",
        [],
    )

    messages = get_all_messages_for_delta(db_connection, today, 14)
    assert len(messages) == 3

    fake_events_result = {
        "items": [
            {
                "summary": "Board game night",
                "creator": {"email": "alice@gmail.com"},
                "start": {"dateTime": "2026-07-20T19:00:00-04:00"},
                "end": {"dateTime": "2026-07-20T22:00:00-04:00"},
            },
            {
                "summary": "Beach day",
                "creator": {"email": "bob@gmail.com"},
                "start": {"date": "2026-07-21"},
                "end": {"date": "2026-07-22"},
            },
        ]
    }
    mock_service = MagicMock()
    mock_service.events.return_value.list.return_value.execute.return_value = (
        fake_events_result
    )

    with (
        patch("friendslist.calendar_helpers.get_credentials"),
        patch("friendslist.calendar_helpers.build", return_value=mock_service),
    ):
        addresses_dict = get_addresses_dict(db_connection)
        events = get_events(addresses_dict)

    cal_title_range, cal_weeks = build_calendar_props(start_sunday, events)
    html = render_email_body(
        date=today,
        messages=messages,
        cal_title_range=cal_title_range,
        cal_weeks=cal_weeks,
    )

    soup = BeautifulSoup(html, "html.parser")

    anchor = soup.find('a')
    assert anchor["href"] == "https://calendar.google.com/calendar/u/2?cid=some_calendar_id"

    text = soup.get_text(" ", strip=True)

    assert "Weekend plans" in text
    assert "Want to hike on Saturday?" in text
    assert "Photos from the trip" in text
    assert "Here are a couple shots" in text
    assert "Quick hello" in text
    assert "No attachments on this one" in text
    assert "Alice" in text
    assert "Bob" in text

    cid_srcs = {img["src"] for img in soup.find_all("img")}
    expected_cids = {
        f"cid:{attachment['id']}"
        for message in messages
        for attachment in message["attachments"]
    }
    assert cid_srcs == expected_cids
    assert len(cid_srcs) == 3

    assert soup.select_one(".calendar-title").get_text(strip=True) == cal_title_range
    event_labels = [ev.get_text(" ", strip=True) for ev in soup.select(".event")]
    assert any("Alice: Board game night" in label for label in event_labels)
    assert any("7:00 PM" in label for label in event_labels)
    assert any("Bob: Beach day" in label for label in event_labels)
    assert soup.select_one(".event-all-day") is not None
