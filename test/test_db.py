from db import insert_message


def test_insert_message(db_connection):
    insert_message(
        db_connection,
        "alice@gmail.com",
        "Test subject",
        "Test message",
        "<div>Test message</div>",
        ["attachment.png"],
    )
    
    cursor = db_connection.cursor()
    cursor.execute(
        """
        SELECT f.name, f.email, m.subject, m.body_plain, m.body_html, a.file_path 
        FROM messages m
        JOIN friends f ON m.friend_id = f.id
        JOIN attachments a ON m.id = a.message_id
    """)
    result = cursor.fetchone()
    assert result is not None
    assert result[0] == "Alice"
    assert result[1] == "alice@gmail.com"
    assert result[2] == "Test subject"
    assert result[3] == "Test message"
    assert result[4] == "<div>Test message</div>"
    assert result[5] == "attachment.png"

