import arxiv

client = arxiv.Client()


def search_arXiv(category):
    search = arxiv.Search(
        query="cat:" + category,
        max_results=5,
        sort_by=arxiv.SortCriterion.SubmittedDate,
    )
    for result in client.results(search):
        # 論文情報の取得
        paper_info = {
            "title": result.title,
            "abstract": result.summary.replace("\n", ""),
            "url": result.entry_id,
            "submitted_date": result.published.strftime("%Y-%m-%d"),
            "category": category,
            "comment": result.comment,
            "authors": "/".join([author.name for author in result.authors]),
        }
        print(paper_info)


if __name__ == "__main__":
    search_arXiv("cs.AI")
