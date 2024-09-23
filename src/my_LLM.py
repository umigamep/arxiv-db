import os

from openai import OpenAI, OpenAIError

client = OpenAI(api_key=os.environ["OPENAI_APIKEY"])


def create_summary_system_prompt():
    prompt = """
    ## 指令
    あなたはサイエンスコミュニケーターとして、研究の魅力を大学生に発信するのに長けています。ユーザが論文のタイトルと概要を提供します。人々の目を惹くように、以下の形式に従って箇条書き3つで要約を作成してください。
    ## 形式
    - 課題: 論文が取り組んだ課題について、問題意識がよく伝わるように書いてください
    - 手法: どのようなアプローチで課題に取り組んだかを魅力的に書いてください
    - 結果: 得られた結果の重要性がよくわかるように書いてください
    ## 例
    ### 入力
    title: Umbrella is useful.
    abstract: It is raining. I went out with an umbrella. I didn't get wet.
    ### 出力
    - 課題：雨が降っている。
    - 手法：傘を持って出かけた。
    - 結果：濡れなかった。
    """

    return prompt


def create_summary_user_prompt(title, abst):
    prompt = f"""
    研究の魅力が大学1年生にも伝わるように、3行の箇条書きで要約を作成してください。
    title: {title}\n
    abstract: {abst}
    """

    return prompt


def request_gpt4o_mini(system_prompt, user_prompt):
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": [{"type": "text", "text": system_prompt}],
                },
                {"role": "user", "content": [{"type": "text", "text": user_prompt}]},
            ],
            temperature=0.8,
        )
        return response.choices[0].message.content

    except OpenAIError as e:
        # Handle all OpenAI API errors
        print(f"Error: {e}")


if __name__ == "__main__":
    system_prompt = "テスト"
    user_prompt = "「こんにちは」とだけ答えてください。"
    responce = request_gpt4o_mini(system_prompt, user_prompt)
    print(responce)
