import time

import yaml
from prefect import flow
from prefect.blocks.system import Secret
from tools.my_arXiv import search_arXiv
from tools.my_notion import MyArxivDatabaseClient
from tools.my_slack import MySlackClient
from tools.paper_info import PaperInfo, create_llm_summary, insert_paper_into_database

DATABASE_ID = Secret.load("arxiv-database-id").get()

arxiv_database = MyArxivDatabaseClient(
    auth=Secret.load("notion-token").get(), database_id=DATABASE_ID
)
slack = MySlackClient(token=Secret.load("slack-api-token").get())

params = yaml.safe_load(open("flows/agg_arxiv_daily_flow.yaml"))
MAX_RESULT = params["MAX_RESULT"]  # aiXivの各カテゴリで最新何件まで検索するか
CATEGORY_LIST = params["CATEGORY_LIST"]


# 実行job関数
@flow  # (log_prints=True)
def agg_arxiv_daily_flow():
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
                    paper_info, Secret.load("openai-apikey").get()
                )
                paper_info.llm_summary = llm_summary
                insert_paper_into_database(paper_info, arxiv_database)

            time.sleep(1)
        time.sleep(3)
    channel = params["SLACK_CHANNEL"]
    text = "\n".join(
        [
            "<!channel> 本日の論文を更新しました。",
            f"🔗 https://www.notion.so/{DATABASE_ID}",
        ]
    )
    slack.post_text_to_channel(text=text, channel=channel)


if __name__ == "__main__":
    agg_arxiv_daily_flow()
