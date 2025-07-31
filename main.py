from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler
import os
from dotenv import load_dotenv
from subFunctions.chatDelete.delChat import deleteMessage as delChat

load_dotenv()
userToken = os.getenv('userToken')
botToken = os.getenv('botToken')
appToken = os.getenv('socketToken')
userIDs = os.getenv('userID').split(',')
timeRange = int(os.getenv('timeRange'), 10)

print(f'BotToken: {botToken}')
print(f'SocketToken: {appToken}')
print(f'UserID: {userIDs}')

# Initialize the app
app = App(token=botToken)

# Listen to ALL message events first to debug


@app.event("message")
def debug_all_messages(body, say, logger):
    print("\n" + "="*50)
    print("📩 ANY MESSAGE EVENT RECEIVED!")
    print("="*50)

    event = body.get('event', {})
    curUser = event.get('user')
    text = event.get('text', '')
    channel = event.get('channel', '')
    chnlTy = event.get('channel_type')
    subtype = event.get('subtype')

    print(f"🔍 Event details:")
    print(f"  - User: {curUser}")
    print(f"  - Expected Users: {userIDs}")
    print(f"  - Text: '{text}'")
    print(f"  - Channel: {channel}")
    print(f"  - Channel Type: {chnlTy}")
    print(f"  - Subtype: {subtype}")
    print(f"  - Bot ID: {event.get('bot_id')}")

    # Skip bot messages
    if event.get('bot_id') or subtype == 'bot_message':
        print("🤖 Skipping bot message")
        return

    # Skip messages without text
    if not text:
        print("📝 Skipping message without text")
        return

    print(f"✅ Processing message from user: {curUser}")

    # Check if this is the correct user and contains the trigger
    if curUser in userIDs and "--del" in text.lower():
        print("🔔 TRIGGER MATCHED!")
        print("🧹 Chat delete function called.")
        say("✅ Function Triggered! Running function...")
        delChat(userToken, channel, timeRange)
    else:
        reasons = []
        if curUser not in userIDs:
            reasons.append(
                f"Wrong user (got {curUser}, expected {userIDs})")
        if "--del" not in text.lower():
            reasons.append(f"Trigger not found in text: '{text}'")
        print(f"❌ Trigger not matched: {' | '.join(reasons)}")

    print("="*50 + "\n")


def main():
    print("-"*50)
    handler = SocketModeHandler(app, appToken)
    handler.start()


if __name__ == '__main__':
    main()
