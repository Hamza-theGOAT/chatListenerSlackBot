import os
import time
import schedule
from dotenv import load_dotenv
from slack_sdk import WebClient
from datetime import datetime, timedelta
from slack_sdk.errors import SlackApiError


def APIreqDelay(channelID, messageTS, attempts, client):
    retries = 0
    while retries < attempts:
        try:
            client.chat_delete(channel=channelID, ts=str(messageTS))
            print(f"Deleted Message with Timestamp {messageTS}")
            time.sleep(1)
            break
        except SlackApiError as e:
            if e.response["error"] == 'ratelimited':
                retry_after = int(e.response.headers.get("Retry-After", 1))
                print(
                    f"⏱️ Rate limit hit. Retrying after {retry_after} seconds")
                time.sleep(retry_after)
                retries += 1
            else:
                print(f"Failed to delete message {
                      messageTS}: {e.response['error']}")
                break


def getThreadMsg(client, channelID, threadTS, timeLimit):
    response = client.conversations_replies(
        channel=channelID,
        ts=threadTS,
        inclusive=True
    )

    threadMsgs = response.get('messages', [])
    print(f"📝 Found {len(threadMsgs)} messages in thread {threadTS}")

    # Filter messages by time limit
    msgToDel = []
    for msg in threadMsgs:
        msgTS = float(msg['ts'])
        if msgTS >= timeLimit:
            msgToDel.append(msg)

    return msgToDel


def deleteMessage(token, channelID, timeRange):
    client = WebClient(token=token)
    rightNow = datetime.now()
    timeLimit = rightNow - timedelta(weeks=timeRange)
    timeTimestamp = timeLimit.timestamp()
    # Fetch messages from the DM channel
    response = client.conversations_history(channel=channelID)
    messages = response['messages']
    print(f"Fetched {len(messages)} messages from channel {channelID}")

    for message in messages:
        messageTS = float(message['ts'])
        if messageTS >= timeTimestamp:

            # Check if this message has replies
            if message.get('reply_count', 0) > 0:
                threadTS = message['ts']

                # Get all messages in this thread
                threadMsgs = getThreadMsg(
                    client, channelID, threadTS, timeTimestamp)

                # Delete thread messages (including the parent)
                for threadMsg in threadMsgs:
                    APIreqDelay(channelID, threadMsg['ts'], 5, client)
            else:
                APIreqDelay(channelID, message['ts'], 5, client)
        else:
            print(f"⏭️ Skipping message {message['ts']} (outside time range)")


def main():
    load_dotenv()
    token = os.getenv('slackToken')
    channelID = os.getenv('userID')
    timeRange = int(os.getenv('timeRange', 6))
    deleteMessage(token, channelID, timeRange)


def agnition():
    schedule.every(2).minutes.do(main)
    print("Starting the Scheduler...")
    while True:
        schedule.run_pending()
        time.sleep(1)


if __name__ == '__main__':
    main()
    # agnition()
