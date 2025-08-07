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

with open('commands.json', 'r', encoding='utf-8') as j:
    cmnds = json.load(j)
cmndList = '\n'.join(cmnds.keys())

with open('picPaths.json', 'r') as j:
    pics = json.load(j)
picList = '\n'.join(pics.keys())

meDir = os.path.join('images', 'memes')


print(f'BotToken: {botToken}')
print(f'SocketToken: {appToken}')
print(f'UserID: {userIDs}')
# print(f'Commandments: {cmnds}')

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

    match = re.search(r'--\S+', text)
    if match:
        cmnd = match.group()
    else:
        cmnd = text

    # Skip bot messages
    if ('[bot]' not in text) and (event.get('bot_id') or subtype == 'bot_message'):
        print("🤖 Skipping bot message")
        return

    # Skip messages without text
    if not text:
        print("📝 Skipping message without text")
        return

    print(f"✅ Processing message from user: {curUser}")

    print(f"🔍 Event details:")
    print(f"  - User: {curUser}")
    print(f"  - Expected Users: {userIDs}")
    print(f"  - Text: '{text}'")
    print(f"  - Command: '{cmnd}'")
    print(f"  - Channel: {channel}")
    print(f"  - Channel Type: {chnlTy}")
    print(f"  - Subtype: {subtype}")
    print(f"  - Bot ID: {event.get('bot_id')}")

    # Check if this is the correct user and contains the trigger
    if curUser in userIDs:
        if cmnd == "--del":
            print("🧹 Chat delete function called.")
            delChat(userToken, channel, timeRange)
            client.files_upload_v2(
                channel=channel,
                file=pics['--nuke'],
                title="I am death, destroyer of both worlds",
                initial_comment=cmnds['--judgement']
            )
        elif cmnd == "--list":
            print("User Requested List of Commands")
            say(f"Here are the list of Commands, MiLord ...\n{cmndList}")
        elif "--list/" in cmnd:
            dirz = listDir(cmnd)
            say(f"Here's the list of sub-directories, MiLord...\n{dirz}")
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
        elif cmnd in cmnds:
            say(cmnds[cmnd])
        else:
            print(f"❌ Trigger not found in text: '{text}'")
    else:
        print(f"Wrong user (got {curUser}, expected {userIDs})")

    print("="*50 + "\n")


def main():
    print("-"*50)
    handler = SocketModeHandler(app, appToken)
    handler.start()


if __name__ == '__main__':
    main()
