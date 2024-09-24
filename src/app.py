import time

import schedule
from tqdm import tqdm

from my_arXiv import search_arXiv
from my_LLM import (
    request_gpt4o_mini,
)
from my_notion import check_existing_id, insert_arXiv_database
from my_slack import post_to_slack

DATABASE_ID = "1062073f173f80109244d8aa52ea1dbb"  # 接続先DB
MAX_RESULT = 30  # aiXivの各カテゴリで最新何件まで検索するか
CATEGORY_LIST = ["stat.AP", "stat.ME", "cs.IR", "cs.CL"]  # + ["stat.CO", "stat.ML"]


def create_summary_system_prompt():
    # 【】をあとで太字として処理する
    prompt = """
    ## 指令
    あなたは大学生に向けて研究の魅力を伝える経験豊富なサイエンスコミュニケーターです。ユーザから提供される論文のタイトルと概要をもとに、研究の重要性や新規性が大学生にもわかりやすく、かつ興味を引く形で要約を作成してください。以下の形式に従って、3つのポイントに分けた簡潔かつ魅力的な要約を提供します。説明は専門的でありつつも、わかりやすさを重視し、興味を引き付ける内容にしてください。また、【強調したい部分】を'【強調したい部分】'のように囲って強調してください。

    ## 形式
    🤔 課題: 論文が取り組んでいる問題やその背景を簡潔に示し、その問題の重要性を強調してください。
    💡 手法: 課題に対してどのようなアプローチを取ったのか、技術や研究手法の新規性や独自性を伝えるように説明してください。
    ✅ 結果: 研究で得られた結果の意義や今後の展望を明確にし、研究の価値を引き立てる形でまとめてください。

    ## 例
    ### 入力
    title: Umbrella is useful.
    abstract: It was raining. I went out with an umbrella. I didn't get wet.

    ### 出力
    🤔 課題: 雨の日に外出する際、【濡れることを防ぐ手段】が必要である。
    💡 手法: 【傘を使用して】雨を防ぐという【シンプルだが効果的な方法を採用】した。
    ✅ 結果: 濡れることなく外出できたことで、【傘の実用性が確認された】。
    """

    return prompt


def create_summary_user_prompt(title, abst):
    prompt = f"""
    大学1年生でも興味を持てるように、次の研究を簡潔に説明してください。研究の課題、取り組みの手法、結果の重要性が伝わるように、3つの箇条書きで要約を作成してください。
    - title: {title}
    - abstract: {abst}
    """

    return prompt


SUMMARY_SYSTEM_PROMPT = create_summary_system_prompt()


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
        # post_cnt = 0
        for page_info in tqdm(page_info_list):
            page_info["arxiv_id"] = page_info["url"].rsplit("/", 1)[-1].split("v")[0]
            if check_existing_id(DATABASE_ID, page_info["arxiv_id"]):
                print(
                    f"Record with ID {page_info["arxiv_id"]} already exists. Skipping insertion."
                )
            else:
                # LLMでサマリーを作成
                user_prompt = create_summary_user_prompt(
                    title=page_info["title"], abst=page_info["abstract"]
                )
                LLM_summary = request_gpt4o_mini(
                    system_prompt=SUMMARY_SYSTEM_PROMPT, user_prompt=user_prompt
                )
                page_info["LLM-summary"] = LLM_summary

                # Notionのテーブルにインサート
                insert_arXiv_database(DATABASE_ID, page_info)
                # is_not_inserted = insert_arXiv_database(DATABASE_ID, page_info)

                # if not is_not_inserted:
                #     # 結果をSlackにpost
                #     channel = (
                #         "#arxiv-" + page_info["category"].replace(".", "_").lower()
                #     )
                #     text = "\n".join(
                #         [
                #             f"📑-{post_cnt}: {page_info["title"]}",
                #             f"🔗: {page_info["url"]}",
                #             "Summary:",
                #             LLM_summary.replace("【", " *").replace("】", "* "),
                #         ]
                #     )
                #     post_to_slack(text=text, channel=channel)
                #     post_cnt += 1
        time.sleep(10)
    channel = "#slack-sdk-test"
    text = "\n".join(
        [
            "<!channel> 本日の論文を更新しました。",
            "🔗: https://www.notion.so/1062073f173f80109244d8aa52ea1dbb?v=10a2073f173f803cb61c000c107d30f9&pvs=4",
        ]
    )
    post_to_slack(text=text, channel=channel)


# AM11:00のjob実行を登録
schedule.every().day.at("00:30").do(job)  # 日本時間はここから+9時間

if __name__ == "__main__":
    # job()
    # jobの実行監視、指定時間になったらjob関数を実行
    while True:
        schedule.run_pending()
        time.sleep(60)
