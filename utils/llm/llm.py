from openai import OpenAI

class LLM_Client(object):
    def __init__(self, api_key: str, base_url: str, model:str):
        self.client = OpenAI(
            api_key = api_key,
            base_url = base_url
        )
        self.model = model
    
    def query_once(self, prompt: str, user_text:str):
        completion = self.client.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": prompt,
                },
                {
                    "role": "user",
                    "content": user_text,
                }
            ],
            model=self.model
        )

        return completion.choices[0].message.content
