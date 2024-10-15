from openai import AzureOpenAI, RateLimitError

class AzureClient:
    def __init__(self, endpoint, key, model_name):
        self.client = AzureOpenAI(
            azure_endpoint=endpoint,
            api_version="2024-02-01",
            api_key=key
        )
        self.model_name = model_name

    def get_completion(self, messages):
        try:
            completion = self.client.chat.completions.create(
                model=self.model_name,
                messages=messages
            )
            return completion.choices[0].message.content
        except RateLimitError as e:
            return f"Rate limit exceeded. Please try again later. Error: {str(e)}"
        except Exception as e:
            return f"An error occurred: {str(e)}"

# Usage
# azure_client = AzureClient(endpoint, key, model_name)
# response = azure_client.get_completion(messages)