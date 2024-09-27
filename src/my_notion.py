import os
import re

from notion_client import Client

notion = Client(auth=os.environ["NOTION_TOKEN"])


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


def check_existing_id(database_id, arxiv_id):
    query = {
        "database_id": database_id,
        "filter": {"property": "arXiv-ID", "rich_text": {"equals": arxiv_id}},
        "page_size": 1,  # 一致するものが見つかったらすぐに終了するため
    }
    response = notion.databases.query(**query)
    return len(response["results"]) > 0


def insert_arXiv_database(database_id, page_info):
    if check_existing_id(database_id, page_info["arxiv_id"]):
        print(
            f"Record with ID {page_info["arxiv_id"]} already exists. Skipping insertion."
        )
        return 0

    try:
        notion.pages.create(
            parent={"database_id": database_id},
            properties={
                "arXiv-ID": create_text_content(page_info["arxiv_id"]),
                "Title": create_title_content(
                    page_info["title"], href=page_info["url"]
                ),
                "Authors": create_text_content(page_info["authors"]),
                "Abstract": create_rich_text_content(page_info["abstract"]),
                "LLM-summary": create_rich_text_content(page_info["LLM-summary"]),
                "Comments": create_text_content(page_info["comment"]),
                "Categories": create_category_content(page_info["category"]),
                "Submission Date": create_date_content(page_info["submitted_date"]),
            },
        )
    except Exception as e:
        print(f"Error inserting into Notion database: {e}")
        return 1
    return 0


if __name__ == "__main__":
    database_id = "1062073f173f80109244d8aa52ea1dbb"  # URLの'/{}?v='部分

    # response = read_notion_database(notion, database_id)
    # for result in response["results"]:
    #     print("-----------------")
    #     print(f"pageid: {result['id']}")
    #     for key, value in result["properties"].items():
    #         print(f"{key=}: {value=}")

    page_info = {}
    page_info["title"] = "Computational Dynamical Systems"
    page_info["arxiv_id"] = "arxiv_id"
    page_info["abstract"] = (
        "We study the computational complexity theory of smooth, finite-dimensionaldynamical systems. Building off of previous work, we give definitions for whatit means for a smooth dynamical system to simulate a Turing machine. We thenshow that 'chaotic' dynamical systems (more precisely, Axiom A systems) and'integrable' dynamical systems (more generally, measure-preserving systems)cannot robustly simulate universal Turing machines, although such machines canbe robustly simulated by other kinds of dynamical systems. Subsequently, weshow that any Turing machine that can be encoded into a structurally stableone-dimensional dynamical system must have a decidable halting problem, andmoreover an explicit time complexity bound in instances where it does halt.More broadly, our work elucidates what it means for one 'machine' to simulateanother, and emphasizes the necessity of defining low-complexity 'encoders' and'decoders' to translate between the dynamics of the simulation and the systembeing simulated. We highlight how the notion of a computational dynamicalsystem leads to questions at the intersection of computational complexitytheory, dynamical systems theory, and real algebraic geometry."
    )
    page_info["LLM-summary"] = "ここに【サマリー】が入る"
    page_info["url"] = "http://arxiv.org/abs/2409.12179v1"
    page_info["submitted_date"] = "2024-09-18"
    page_info["category"] = "cs.AI"
    page_info["comment"] = "46+14 pages, 6 figures; accepted to FOCS 2024"
    page_info["authors"] = "Jordan Cotler/Semon Rezchikov"

    insert_arXiv_database(database_id, page_info)
