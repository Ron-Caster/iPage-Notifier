from groq import Groq

def get_groq_response(conversation_history, user_prompt=None):
    client = Groq()
    if user_prompt:
        conversation_history.append({"role": "user", "content": user_prompt})

    completion = client.chat.completions.create(
        model="llama3-8b-8192",
        messages=conversation_history,
        temperature=1,
        max_tokens=1024,
        top_p=1,
        stream=True,
        stop=None,
    )

    response = ""
    for chunk in completion:
        response += chunk.choices[0].delta.content or ""

    return response
