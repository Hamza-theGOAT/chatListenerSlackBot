from slack_sdk import WebClient
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler
import os
import json
import re
import random
from dotenv import load_dotenv
from subFunctions.chatDelete.delChat import deleteMessage as delChat

load_dotenv()
userToken = os.getenv('userToken')
botToken = os.getenv('botToken')
appToken = os.getenv('socketToken')
userIDs = os.getenv('userID').split(',')
timeRange = int(os.getenv('timeRange'), 10)

client = WebClient(token=botToken)

with open('proclamations.json', 'r', encoding='utf-8') as j:
    proc = json.load(j)
procList = '\n'.join(proc.keys())

with open('picPaths.json', 'r') as j:
    pics = json.load(j)
picList = '\n'.join(pics.keys())

with open('audPaths.json', 'r') as j:
    auds = json.load(j)
audList = '\n'.join(auds.keys())

meDir = os.path.join('img', 'memes')


print(f'BotToken: {botToken}')
print(f'SocketToken: {appToken}')
print(f'UserID: {userIDs}')
# print(f'Commandments: {cmnds}')
# print(f'Commandments: {auds}')

# Initialize the app
app = App(token=botToken)


def listDir(cmnd):
    folders = cmnd.split('/')[1:]
    path = os.path.join(*folders)
    dirz = '\n'.join(os.listdir(path))

    print(f"User Requested List of directories in '{path}'")
    return dirz


@app.event("message")
def messageEvent(body, say, logger):
    print("\n" + "="*50)
    print("📩 ANY MESSAGE EVENT RECEIVED!")
    print("="*50)

    event = body.get('event', {})
    curUser = event.get('user')
    text = event.get('text', '')
    channel = event.get('channel', '')
    chnlTy = event.get('channel_type')
    subtype = event.get('subtype')
    botID = event.get('bot_id')

    # Skip messages without text
    if not text or not text.startswith('--'):
        print("📝 Skipping message without text/Command")
        return
    # Skip bot messages
    if ('[bot]' not in text) and (botID or subtype == 'bot_message'):
        print("🤖 Skipping bot message")
        return
    if curUser not in userIDs:
        print(f"Wrong user (got {curUser}, expected: {userIDs})")
        say("The Light does not shine upon thee!!!")
        return

    cmnd = re.search(r"--\S+", text)
    cmnd = cmnd.group() if cmnd else text

    print(f"✅ Processing message from user: {curUser}")

    print(f"🔍 Event details:")
    print(f"  - Text: '{text}'")
    print(f"  - Command: '{cmnd}'")
    print(f"  - Channel: {channel}")

    # Execute the given trigger

    # Function Triggers
    if cmnd == "--del":
        print("🧹 Chat delete function called.")
        delChat(userToken, channel, timeRange)
        client.files_upload_v2(
            channel=channel,
            file=pics['--nuke'],
            title="I am death, destroyer of both worlds",
            initial_comment=proc['biblical']['--judgement']
        )

    # Written Lines Triggers
    elif cmnd == "--comL":
        print("User Requested List of Commands")
        say(f"Here are the list of Commands, MiLord ...\n{procList}")
    elif '/' not in cmnd:
        for key, val in proc.items():
            if cmnd in val:
                say(val[cmnd])
    
    # List of sub-directories Trigger
    elif "--list/" in cmnd:
        dirz = listDir(cmnd)
        say(f"Here's the list of sub-directories, MiLord...\n{dirz}")

    # Random Meme request Trigger
    elif cmnd.startswith("--meme"):
        path = os.path.join(meDir, *cmnd.split('/')[1:])
        print(f"Extracted Path: {path}")
        if not os.path.isdir(path):
            path = meDir
        img = random.choice([f for f in os.listdir(path)])
        imgPath = os.path.join(path, img)
        print("🖼️ Sending image to Slack channel...")
        client.files_upload_v2(
            channel=channel,
            file=imgPath,
            title="Here's your meme, MiLord",
            initial_comment="Behold thy meme!"
        )

    # List of audio commands request Trigger
    elif cmnd == '--sayL':
        say(f"Here's the list MiLord:\n{audList}")

    # Audio command Trigger
    elif cmnd.startswith('--say'):
        cmnd = cmnd.split('/')[1:][0]
        print(f"Audio Command Received: {cmnd}")
        if cmnd in auds:
            client.files_upload_v2(
                channel=channel,
                file=auds[cmnd],
                title=f"{cmnd}.mp3",
                initial_comment="Here's your GOAT'ed words, MiLord ..."
            )
        else:
            say("Invalid Audio Command, MiLord!")

    # Invalid Command Result
    else:
        say("Given Command holds no action!")
        print(f"❌ Trigger not found in text: '{text}'")

    print("="*50 + "\n")


# Test slash command function
@app.command("/test")
def repeatText(ack, respond, command, say):
    # Acknowledge command request
    ack()
    say(f"{command['text']}")


def main():
    print("-"*50)
    handler = SocketModeHandler(app, appToken)
    handler.start()


if __name__ == '__main__':
    main()
