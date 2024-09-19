import os

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
    return {"rich_text": [{"type": "text", "text": {"content": text}}]}


def create_date_content(date):
    return {"date": {"start": date}}


def create_category_content(category, color="gray"):
    return {"multi_select": [{"name": category, "color": color}]}


def insert_arXiv_database(
    database_id, title, authors, abst, comment, category, url, date
):
    try:
        notion.pages.create(
            parent={"database_id": database_id},
            properties={
                "Title": create_title_content(title, href=url),
                "Authors": create_text_content(authors),
                "Abstract": create_text_content(abst),
                "Comment": create_text_content(comment),
                "Categories": create_category_content(category),
                "Submission Date": create_date_content(date),
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

    title = "Computational Dynamical Systems"
    abst = "We study the computational complexity theory of smooth, finite-dimensionaldynamical systems. Building off of previous work, we give definitions for whatit means for a smooth dynamical system to simulate a Turing machine. We thenshow that 'chaotic' dynamical systems (more precisely, Axiom A systems) and'integrable' dynamical systems (more generally, measure-preserving systems)cannot robustly simulate universal Turing machines, although such machines canbe robustly simulated by other kinds of dynamical systems. Subsequently, weshow that any Turing machine that can be encoded into a structurally stableone-dimensional dynamical system must have a decidable halting problem, andmoreover an explicit time complexity bound in instances where it does halt.More broadly, our work elucidates what it means for one 'machine' to simulateanother, and emphasizes the necessity of defining low-complexity 'encoders' and'decoders' to translate between the dynamics of the simulation and the systembeing simulated. We highlight how the notion of a computational dynamicalsystem leads to questions at the intersection of computational complexitytheory, dynamical systems theory, and real algebraic geometry."
    url = "http://arxiv.org/abs/2409.12179v1"
    date = "2024-09-18"
    category = "cs.AI"
    comment = "46+14 pages, 6 figures; accepted to FOCS 2024"
    authors = "Jordan Cotler/Semon Rezchikov"
    insert_arXiv_database(
        database_id, title, authors, abst, comment, category, url, date
    )
