import os

from slack_sdk.web import WebClient

# slack app url: https://api.slack.com/apps/A07MQNVK1V5
client = WebClient(token=os.environ["SLACK_API_TOKEN"])


def post_to_slack(text, channel):
    try:
        client.chat_postMessage(text=text, channel=channel)

    except Exception as e:
        print(e)


if __name__ == "__main__":
    text = "Hello from slack-sdk"
    channel = "#slack-sdk-test"
    post_to_slack(text, channel)
