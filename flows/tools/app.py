import os
import time

import schedule
from my_arXiv import search_arXiv
from my_notion import MyArxivDatabaseClient
from my_slack import MySlackClient
from openai import OpenAI
from paper_info import PaperInfo
from tqdm import tqdm

DATABASE_ID = os.environ["ARXIV_DATABASE_ID"]

arxiv_database = MyArxivDatabaseClient(
    auth=os.environ["NOTION_TOKEN"], database_id=DATABASE_ID
)
openai_client = OpenAI(api_key=os.environ["OPENAI_APIKEY"])
slack = MySlackClient(token=os.environ["SLACK_API_TOKEN"])

MAX_RESULT = 10  # aiXivの各カテゴリで最新何件まで検索するか
CATEGORY_LIST = ["stat.AP", "stat.ME", "cs.IR", "cs.CL"]  # + ["stat.CO", "stat.ML"]


# 実行job関数
def job():
    # カテゴリごとにクロール
    for category in CATEGORY_LIST:
        # arXiv APIにリクエスト
        print("----------------")
        print(f"{category=}")
        print("----------------")
        page_info_list = search_arXiv(category, max_result=MAX_RESULT)
        # ヒットしたpageごとに要約を作成し、インサートし、ポスト
        for page_info in tqdm(page_info_list):
            page_info["arxiv_id"] = page_info["url"].rsplit("/", 1)[-1].split("v")[0]
            if arxiv_database.check_id_exists(page_info["arxiv_id"]):
                print(
                    f"Record with ID {page_info["arxiv_id"]} already exists. Skipping insertion."
                )
            else:
                paper_info = PaperInfo(**page_info)
                paper_info.create_llm_summary(openai_client=openai_client)
                paper_info.insert_into_database(arxiv_database)

            time.sleep(1)
        time.sleep(3)
    channel = "#slack-sdk-test"
    text = "\n".join(
        [
            "<!channel> 本日の論文を更新しました。",
            f"🔗 https://www.notion.so/{DATABASE_ID}",
        ]
    )
    slack.post_text_to_channel(text=text, channel=channel)


# AM9:30のjob実行を登録
schedule.every().day.at("00:30").do(job)  # 日本時間はここから+9時間

if __name__ == "__main__":
    job()
    # jobの実行監視、指定時間になったらjob関数を実行
    # while True:
    #     schedule.run_pending()
    #     time.sleep(60)
