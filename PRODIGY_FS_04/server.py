from myapp import create_app
from myapp.database import db, Message, ChatMessage
from flask_socketio import emit, join_room, leave_room

app, socket = create_app()


# COMMUNICATION ARCHITECTURE

@socket.on("join-chat")
def join_private_chat(data):
    room = data["rid"]
    join_room(room=room)
    socket.emit(
        "joined-chat",
        {"msg": f"{room} is now online."},
        room=room,
        # include_self=False,
    )



@socket.on("outgoing")
def chatting_event(json, methods=["GET", "POST"]):
    """
    handles saving messages and sending messages to all clients
    :param json: json
    :param methods: POST GET
    :return: None
    """
    room_id = json["rid"]
    timestamp = json["timestamp"]
    message = json["message"]
    sender_id = json["sender_id"]
    sender_username = json["sender_username"]

   
    message_entry = Message.query.filter_by(room_id=room_id).first()

    
    chat_message = ChatMessage(
        content=message,
        timestamp=timestamp,
        sender_id=sender_id,
        sender_username=sender_username,
        room_id=room_id,
    )
    
    message_entry.messages.append(chat_message)

    
    try:
        chat_message.save_to_db()
        message_entry.save_to_db()
    except Exception as e:
        
        print(f"Error saving message to the database: {str(e)}")
        db.session.rollback()

   
    socket.emit(
        "message",
        json,
        room=room_id,
        include_self=False,
    )


if __name__ == "__main__":
    socket.run(app, allow_unsafe_werkzeug=True, debug=True)
