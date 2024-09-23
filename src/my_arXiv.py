import arxiv

client = arxiv.Client()


def search_arXiv(category, max_result=100):
    search = arxiv.Search(
        query="cat:" + category,
        max_results=max_result,
        sort_by=arxiv.SortCriterion.SubmittedDate,
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
