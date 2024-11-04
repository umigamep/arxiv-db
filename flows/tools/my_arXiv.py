from datetime import datetime, timedelta

import arxiv
from prefect import task


@task
def search_arXiv(category, max_result=100):
    client = arxiv.Client()
    # 現在の日付から1週間前と2週間前の日付を計算
    two_weeks_ago = (datetime.now() - timedelta(days=13)).strftime("%Y%m%d")
    one_week_ago = (datetime.now() - timedelta(days=6)).strftime("%Y%m%d")

    # 日付範囲を含むクエリを作成
    date_range_query = f"submittedDate:[{two_weeks_ago} TO {one_week_ago}]"
    full_query = f"cat:{category} AND {date_range_query}"

    search = arxiv.Search(
        query=full_query,
        max_results=max_result,
        sort_by=arxiv.SortCriterion.SubmittedDate,
        sort_order=arxiv.SortOrder.Descending,
    )
    paper_info_list = [
        {
            "title": result.title,
            "abstract": result.summary.replace("\n", ""),
            "url": result.entry_id,
            "submitted_date": result.published.strftime("%Y-%m-%d"),
            "category": category,
            "comment": result.comment,
            "authors": "/".join([author.name for author in result.authors]),
        }
        for result in client.results(search)
    ]

    return paper_info_list


if __name__ == "__main__":
    print(search_arXiv("cs.AI"))
