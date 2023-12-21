# import os
from twilio.rest import Client
from dotenv import load_dotenv
import os

load_dotenv()

account_sid = os.getenv('ACCOUNT_SID')
auth_token = os.getenv('AUTH_TOKEN')

client = Client(account_sid, auth_token)

# Function to ensure the phone number follows E.164 format
def format_phone_number(phone_number):

    phone_number = ''.join(filter(str.isdigit, phone_number))
    
    if not phone_number.startswith('1'):
        phone_number = '1' + phone_number
    
    if not phone_number.startswith('+'):
        phone_number = '+' + phone_number

    return phone_number

# fetch existing convos from twilio service
def fetchAllConversations():
    conversations = client.conversations.v1.conversations.list()
    return conversations

def createChatAndAddParticipant(user_name, number, chat_name):

    # format number for proper validation
    number = format_phone_number(number)

    conversation = client.conversations \
                     .v1 \
                     .conversations \
                     .create(friendly_name=chat_name)
    
    chat_details = {
        "name": chat_name,
        "sid": conversation.sid,
        "participants": {}
    }

    # create chat manager
    client.conversations \
                    .v1 \
                    .conversations(conversation.sid) \
                    .participants \
                    .create(
                         identity='Manager',
                         messaging_binding_projected_address='+17208079029'
                     )

    participant = client.conversations \
                    .v1 \
                    .conversations(conversation.sid) \
                    .participants \
                    .create(
                         messaging_binding_address=number
                     )
    
    client.conversations \
        .v1 \
        .conversations(conversation.sid) \
        .messages \
        .create(
            body=f'Hi {user_name}. Thanks for creating this group chat named: {chat_name}',
            author='Manager'
        )
    
    chat_details['participants'][participant.sid] = number

    print(f'Created new group chat {chat_name}: {conversation.sid}')
    
    conversationObj = {
        "sid": conversation.sid,
        "account_sid": conversation.account_sid,
        "chat_service_sid": conversation.chat_service_sid,
        "messaging_service_sid": conversation.messaging_service_sid,
        "friendly_name": conversation.friendly_name,
        "unique_name": conversation.unique_name,
        "attributes": conversation.attributes,
        "date_created": conversation.date_created,
        "date_updated": conversation.date_updated,
        "state": conversation.state
    }

    return conversationObj

def joinChat(conversationSid, number):
    client.conversations \
        .v1 \
        .conversations(conversationSid) \
        .participants \
        .create(
            messaging_binding_address=number
        )