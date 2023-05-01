import openai

openai.api_key = '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'

# Initialize conversation
conversation = [
    {"role": "system", "content": "You are a helpful assistant."},
]

while True:
    message = input("User: ")

    conversation.append({
        'role': 'user',
        'content': message
    })

    response = openai.Completion.create(
        engine="text-davinci-003",
        model="gpt-3.5-turbo",  # As of my knowledge cutoff in September 2021, "gpt-3.5-turbo" is not a valid model. Please check OpenAI's latest model versions.
        messages=conversation,
        max_tokens=150,
    )

    conversation.append({
        'role': 'assistant',
        'content': response['choices'][0]['message']['content']
    })

    print(f"Assistant: {response['choices'][0]['message']['content']}")
