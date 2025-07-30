from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler
import os
from dotenv import load_dotenv


def getCredz():
    load_dotenv()

    userToken = os.getenv('userToken')
    app = App(token=userToken)

    return app


def main():
    app = getCredz()


if __name__ == '__main__':
    main()
