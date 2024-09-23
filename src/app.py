import time

import schedule
from tqdm import tqdm

from my_arXiv import search_arXiv
from my_LLM import (
    create_summary_system_prompt,
    create_summary_user_prompt,
    request_gpt4o_mini,
)
from my_notion import check_existing_id, insert_arXiv_database
from my_slack import post_to_slack

DATABASE_ID = "1062073f173f80109244d8aa52ea1dbb"  # 接続先DB
MAX_RESULT = 30  # aiXivの各カテゴリで最新何件まで検索するか
SYSTEM_PROMPT = create_summary_system_prompt()
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
        post_cnt = 0
        for page_info in tqdm(page_info_list):
            arxiv_id = page_info["url"].rsplit("/", 1)[-1]
            if check_existing_id(DATABASE_ID, arxiv_id):
                print(f"Record with ID {arxiv_id} already exists. Skipping insertion.")
            else:
                # LLMでサマリーを作成
                user_prompt = create_summary_user_prompt(
                    title=page_info["title"], abst=page_info["abstract"]
                )
                LLM_summary = request_gpt4o_mini(
                    system_prompt=SYSTEM_PROMPT, user_prompt=user_prompt
                )
                page_info["LLM-summary"] = LLM_summary

                # Notionのテーブルにインサート
                is_not_inserted = insert_arXiv_database(DATABASE_ID, page_info)

                if not is_not_inserted:
                    # 結果をSlackにpost
                    channel = (
                        "#arxiv-" + page_info["category"].replace(".", "_").lower()
                    )
                    text = "\n".join(
                        [
                            f"【{post_cnt}】{page_info["title"]}",
                            f"URL: {page_info["url"]}",
                            "Summary:",
                            LLM_summary,
                        ]
                    )
                    post_to_slack(text=text, channel=channel)
                    post_cnt += 1
        time.sleep(3)


# AM11:00のjob実行を登録
schedule.every().day.at("08:00").do(job)  # 日本時間はここから+9時間

if __name__ == "__main__":
    # job()
    # jobの実行監視、指定時間になったらjob関数を実行
    while True:
        schedule.run_pending()
        time.sleep(60)
