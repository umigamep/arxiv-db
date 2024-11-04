import os
import time

from prefect import flow
from tools.my_arXiv import search_arXiv
from tools.my_notion import MyArxivDatabaseClient
from tools.my_slack import MySlackClient
from tools.paper_info import PaperInfo, create_llm_summary, insert_paper_into_database

DATABASE_ID = os.environ["ARXIV_DATABASE_ID"]

arxiv_database = MyArxivDatabaseClient(
    auth=os.environ["NOTION_TOKEN"], database_id=DATABASE_ID
)
slack = MySlackClient(token=os.environ["SLACK_API_TOKEN"])

MAX_RESULT = 12  # aiXivの各カテゴリで最新何件まで検索するか
CATEGORY_LIST = ["stat.AP", "stat.ME", "cs.IR", "cs.CL"]  # + ["stat.CO", "stat.ML"]


# 実行job関数
@flow  # (log_prints=True)
def job():
    # カテゴリごとにクロール
    for category in CATEGORY_LIST:
        # arXiv APIにリクエスト
        print("----------------")
        print(f"{category=}")
        print("----------------")
        page_info_list = search_arXiv(category, max_result=MAX_RESULT)
        # ヒットしたpageごとに要約を作成し、インサートし、ポスト
        for page_info in page_info_list:
            page_info["arxiv_id"] = page_info["url"].rsplit("/", 1)[-1].split("v")[0]
            id_exsists = arxiv_database.check_id_exists(page_info["arxiv_id"])
            if id_exsists:
                print(
                    f"Record with ID {page_info["arxiv_id"]} already exists. Skipping insertion."
                )
            else:
                paper_info = PaperInfo(**page_info)
                llm_summary = create_llm_summary(
                    paper_info, os.environ["OPENAI_APIKEY"]
                )
                paper_info.llm_summary = llm_summary
                insert_paper_into_database(paper_info, arxiv_database)

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


if __name__ == "__main__":
    job()
