from prefect import flow

# Source for the code to deploy (here, a GitHub repo)
SOURCE_REPO = "https://github.com/umigamep/arXiv-db.git"

if __name__ == "__main__":
    flow.from_source(
        source=SOURCE_REPO,
        entrypoint="flows/agg_arxiv_daily_flow.py:agg_arxiv_daily_flow",  # Specific flow to run
    ).deploy(
        name="agg_arxiv_daily",
        work_pool_name="my-work-pool",  # Work pool target
        cron="0 1 * * *",  # Cron schedule (1am every day)
    )
