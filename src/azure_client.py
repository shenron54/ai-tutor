from openai import AzureOpenAI

class AzureClient:
    def __init__(self, api_key, endpoint, model_name):
        self.client = AzureOpenAI(
            api_key=api_key,
            api_version="2023-05-15",
            azure_endpoint=endpoint
        )
        self.model_name = model_name

    def get_completion(self, messages):
        try:
            completion = self.client.chat.completions.create(
                model=self.model_name,
                messages=messages
            )
            return completion.choices[0].message.content
        except Exception as e:
            return f"An error occurred: {str(e)}"