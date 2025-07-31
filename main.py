from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler
import os
from dotenv import load_dotenv


load_dotenv()
botToken = os.getenv('botToken')
appToken = os.getenv('socketToken')
app = App(token=botToken)


@app.event("message")
def eventHandler(body, say, logger):
    print("📩 Message event received!")

    userID = body['event'].get('user')
    text = body['event'].get('text', '')

    if userID == os.getenv('userID') and "--del" in text.lower():
        print("🔔 Trigger matched!")
        say("✅ Running the function now...")
        chatDel()


def chatDel():
    print("🧹 Chat delete function called.")


def main():
    handler = SocketModeHandler(app, appToken)
    handler.start()


if __name__ == '__main__':
    main()
