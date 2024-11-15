import openai

def query_openai(prompt, api_key):
    openai.api_key = api_key
    response = openai.Completion.create(
        model="text-davinci-003",
        prompt=prompt,
        max_tokens=100
    )
    return response.choices[0].text.strip()
