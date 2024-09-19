import os

from openai import OpenAI, OpenAIError

client = OpenAI(api_key=os.environ["OPENAI_APIKEY"])


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
        return response

    except OpenAIError as e:
        # Handle all OpenAI API errors
        print(f"Error: {e}")


if __name__ == "__main__":
    system_prompt = "テスト"
    user_prompt = "「こんにちは」とだけ答えてください。"
    responce = request_gpt4o_mini(system_prompt, user_prompt)
    print(responce)
