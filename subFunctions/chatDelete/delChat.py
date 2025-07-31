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
                print(f"Rate limit hit. Retrying after {retry_after} seconds")
                time.sleep(retry_after)
                retries += 1
            else:
                print(f"Failed to delete message {
                      messageTS}: {e.response['error']}")
                break


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
            try:
                APIreqDelay(channelID, message['ts'], 5, client)
                print(f"Deleted message with timestamp {message['ts']}")
            except SlackApiError as e:
                print(f"Error deleting message: {e.response['error']}")
            else:
                print(f"""Skipping message with timestamp {
                      message['ts']} as it's outside the time frame""")


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
