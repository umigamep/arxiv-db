from openai import OpenAIError


class PaperInfo:
    def __init__(
        self,
        arxiv_id: str | None = None,
        title: str | None = None,
        url: str | None = None,
        authors: str | None = None,
        abstract: str | None = None,
        llm_summary: str | None = None,
        comment: str | None = None,
        category: str | None = None,
        submitted_date: str | None = None,
    ) -> None:
        self.arxiv_id = arxiv_id
        self.title = title
        self.url = url
        self.authors = authors
        self.abstract = abstract
        self.llm_summary = llm_summary
        self.comment = comment
        self.category = category
        self.submitted_date = submitted_date

    def all_contents_exist(self):
        return all(
            value not in (None, "")
            for value in [
                self.arxiv_id,
                self.title,
                self.url,
                self.authors,
                self.abstract,
                self.llm_summary,
                self.comment,
                self.category,
                self.submitted_date,
            ]
        )

    def create_llm_summary(self, openai_client):
        if self.title is not None and self.abstract is not None:
            system_prompt = self.create_summary_system_prompt()
            user_prompt = self.create_summary_user_prompt(
                title=self.title, abstract=self.abstract
            )

            try:
                response = openai_client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[
                        {
                            "role": "system",
                            "content": [{"type": "text", "text": system_prompt}],
                        },
                        {
                            "role": "user",
                            "content": [{"type": "text", "text": user_prompt}],
                        },
                    ],
                    temperature=0.8,
                )
                self.llm_summary = response.choices[0].message.content

            except OpenAIError as e:
                # Handle all OpenAI API errors
                print(f"Error: {e}")
        else:
            raise ValueError(
                f"""titleまたはabstractが存在しません:\n {self.title=}\n{self.abstract=}"""
            )

    def create_summary_user_prompt(self, title, abstract):
        prompt = f"""
        大学1年生でも興味を持てるように、次の研究を簡潔に説明してください。研究の課題、取り組みの手法、結果の重要性が伝わるように、3つの箇条書きで要約を作成してください。
        - title: {title}
        - abstract: {abstract}
        """

        return prompt

    def create_summary_system_prompt(self):
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

    def insert_into_database(self, my_notion_database_client):
        my_notion_database_client.insert_paper_info(self)
