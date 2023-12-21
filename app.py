from flask import Flask, request, render_template, redirect, url_for, flash, session
from models import db, User, GroupChats
from chat import createChatAndAddParticipant, joinChat


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://vanhorn:password@localhost/sms_chat_db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

with app.app_context():
    db.create_all()

# Secret key for flashing messages
app.secret_key = 'secret_key'

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        phone_number = request.form['phone_number']

        if not name or not phone_number:
            flash('Missing name or phone number', 'error')
            return redirect(url_for('register'))

        existing_user = User.query.filter_by(phone_number=phone_number).first()
        if existing_user:
            flash('Phone number already exists', 'error')
            return redirect(url_for('conversations'))

        new_user = User(name=name, phone_number=phone_number)
        db.session.add(new_user)
        db.session.commit()

        # Store user information in the session
        session['user_id'] = new_user.id

        flash(f'User {name} registered successfully!', 'success')
        return redirect(url_for('conversations'))  # Assuming you redirect to group creation

    return render_template('register.html')


# @app.route('/create_group', methods=['GET', 'POST'])
# def create_group():
#     if request.method == 'POST':
#         group_name = request.form['group_name']
#         if group_name:
#             # Retrieve user information from the session
#             user_id = session.get('user_id')

#             # Add the user (from the registration step) to the group chat's users list
#             user = User.query.get(user_id)

#             # Create Twilio group chat and add user
#             conversation = createChatAndAddParticipant(user.name, user.phone_number, group_name)

#             new_group = GroupChats(**conversation)
#             new_group.users.append(user)

#             db.session.add(new_group)
#             db.session.commit()

#             return redirect(url_for('group_created', group_name=group_name))


#         return 'Group name is required'
#     return render_template('create_group.html')

@app.route('/conversations')
def conversations():
    # Handle POST request for creating a new group
    if request.method == 'POST':
        group_name = request.form['group_name']
        if group_name:
            # Retrieve user information from the session
            user_id = session.get('user_id')

            # Add the user (from the registration step) to the group chat's users list
            user = User.query.get(user_id)

            # Create Twilio group chat and add user
            conversation = createChatAndAddParticipant(user.name, user.phone_number, group_name)

            new_group = GroupChats(**conversation)
            new_group.users.append(user)

            db.session.add(new_group)
            db.session.commit()

            return redirect(url_for('conversations'))

        return 'Group name is required'

    # Retrieve user information from the session for listing conversations
    user_id = session.get('user_id')
    user = User.query.get(user_id)
    conversations = GroupChats.query.all()
    user_conversation_ids = {c.id for c in user.group_chats} if user else set()

    # Render a template that combines group creation and conversation list
    return render_template('conversations.html', conversations=conversations, user_conversation_ids=user_conversation_ids)

# def list_conversations():
#     # Retrieve user information from the session
#     user_id = session.get('user_id')
#     user = User.query.get(user_id)

#     # Query the GroupChats table to get a list of conversations
#     conversations = GroupChats.query.all()

#     # Create a set of conversation IDs that the user is a member of
#     user_conversation_ids = {c.id for c in user.group_chats} if user else set()

#     return render_template('conversations.html', conversations=conversations, user_conversation_ids=user_conversation_ids)


@app.route('/join_conversation/<int:conversation_id>', methods=['POST'])
def join_conversation(conversation_id):
    # Retrieve user information from the session
    user_id = session.get('user_id')

    # Add the user (from the registration step) to the selected conversation's users list
    user = User.query.get(user_id)
    conversation = GroupChats.query.get(conversation_id)

    if user and conversation:
        conversation.users.append(user)
        db.session.commit()
    
    joinChat(conversation.sid, user.phone_number)

    return redirect(url_for('list_conversations'))

@app.route('/group_created/<group_name>')
def group_created(group_name):
    return f'Group "{group_name}" has been created successfully!'

if __name__ == '__main__':
    app.run(debug=True)

