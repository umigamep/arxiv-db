import os
import re

from notion_client import Client
from prefect import task

notion = Client(auth=os.environ["NOTION_TOKEN"])


class MyArxivDatabaseClient:
    def __init__(self, auth, database_id) -> None:
        self.auth = auth
        self.database_id = database_id

    def _get_client(self) -> Client:
        # @taskのpickleのために、メソッドを呼び出すたびに新しいClientインスタンスを作成
        return Client(auth=self.auth)

    @task
    def check_id_exists(self, arxiv_id):
        try:
            client = self._get_client()
            query = {
                "database_id": self.database_id,
                "filter": {"property": "arXiv-ID", "rich_text": {"equals": arxiv_id}},
                "page_size": 1,
            }
            response = client.databases.query(**query)
            return len(response["results"]) > 0
        except Exception as e:
            print(f"Error checking existing ID: {e}")
            return True  # 挿入しない方に倒す

    @task
    def insert_paper_info(self, paper_info):
        client = self._get_client()
        if self.check_id_exists(paper_info.arxiv_id):
            print(
                f"Record with ID {paper_info.arxiv_id} already exists. Skipping insertion."
            )
            return 0

        try:
            client.pages.create(
                parent={"database_id": self.database_id},
                properties={
                    "arXiv-ID": create_text_content(paper_info.arxiv_id),
                    "Title": create_title_content(
                        paper_info.title, href=paper_info.url
                    ),
                    "Authors": create_text_content(paper_info.authors),
                    "Abstract": create_rich_text_content(paper_info.abstract),
                    "LLM-summary": create_rich_text_content(paper_info.llm_summary),
                    "Comments": create_text_content(paper_info.comment),
                    "Categories": create_category_content(paper_info.category),
                    "Submission Date": create_date_content(paper_info.submitted_date),
                },
            )
        except Exception as e:
            print(f"Error inserting into Notion database: {e}")
            return 1
        return 0

    def read(self):
        client = self._get_client()
        response = client.databases.query(
            **{
                "database_id": self.database_id,
            }
        )
        return response


def read_notion_database(notion, database_id):
    response = notion.databases.query(
        **{
            "database_id": database_id,
        }
    )
    return response


def create_title_content(title, href=None):
    return {
        "title": [
            {
                "type": "text",
                "text": {"content": title, "link": {"url": href} if href else None},
            }
        ]
    }


def create_text_content(text):
    if text is None:
        text = ""
    return {"rich_text": [{"type": "text", "text": {"content": text}}]}


def create_rich_text_content(text):
    if text is None:
        return {"rich_text": []}

    parts = re.split(r"(【.*?】)", text)
    rich_text = []

    for part in parts:
        if part.startswith("【") and part.endswith("】"):
            # 太字にする部分
            content = part[1:-1]  # 【】を除去
            rich_text.append(
                {
                    "type": "text",
                    "text": {"content": content},
                    "annotations": {"bold": True},
                }
            )
        elif part:
            # 通常のテキスト
            rich_text.append({"type": "text", "text": {"content": part}})

    return {"rich_text": rich_text}


def create_date_content(date):
    return {"date": {"start": date}}


def create_category_content(category):
    return {"multi_select": [{"name": category}]}
