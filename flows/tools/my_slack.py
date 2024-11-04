import os

from prefect import task
from slack_sdk.web import WebClient


# slack app url: https://api.slack.com/apps/A07MQNVK1V5
class MySlackClient(WebClient):
    def __init__(
        self,
        token: str | None = None,
    ):
        super().__init__(token)

    @task
    def post_text_to_channel(self, text, channel):
        try:
            self.chat_postMessage(
                channel=channel,
                text=text,
            )

        except Exception as e:
            print(e)


if __name__ == "__main__":
    slack = MySlackClient(token=os.environ["SLACK_API_TOKEN"])
    text = ":tada: APIから *こんにちは* "
    channel = "#slack-sdk-test"

    slack.post_text_to_channel(text, channel)
