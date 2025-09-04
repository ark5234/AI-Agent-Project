from openai import OpenAI

def query_openai(prompt, api_key):
    """Query OpenAI using the modern client API."""
    client = OpenAI(api_key=api_key)
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",  # Updated to current model
        messages=[{"role": "user", "content": prompt}],
        max_tokens=100
    )
    return response.choices[0].message.content.strip()
