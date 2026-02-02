import os
from openai import OpenAI


def get_client():
    """Initialize OpenAI client with API key from environment."""
    api_key = os.getenv("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")
    if not api_key:
        raise ValueError("OPENAI_API_KEY environment variable not set")
    return OpenAI(api_key=api_key)


def chat(message: str, model: str = "gpt-3.5-turbo") -> str:
    """
    Send a message to ChatGPT and get a response.
    
    Args:
        message: The user's message to send
        model: The model to use (default: gpt-3.5-turbo)
    
    Returns:
        The assistant's response text
    """
    client = get_client()
    
    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "user", "content": message}
        ]
    )
    
    return response.choices[0].message.content


def chat_with_history(messages: list, model: str = "gpt-3.5-turbo") -> str:
    """
    Send a conversation with history to ChatGPT.
    
    Args:
        messages: List of message dicts with 'role' and 'content'
        model: The model to use
    
    Returns:
        The assistant's response text
    """
    client = get_client()
    
    response = client.chat.completions.create(
        model=model,
        messages=messages
    )
    
    return response.choices[0].message.content


def main():
    """Interactive chat loop."""
    print("ChatGPT AI Assistant")
    print("Type 'quit' to exit\n")
    
    conversation = []
    
    while True:
        user_input = input("You: ").strip()
        
        if user_input.lower() == 'quit':
            print("Goodbye!")
            break
        
        if not user_input:
            continue
        
        # Add user message to conversation
        conversation.append({"role": "user", "content": user_input})
        
        try:
            # Get response from ChatGPT
            response = chat_with_history(conversation)
            print(f"\nAssistant: {response}\n")
            
            # Add assistant response to conversation history
            conversation.append({"role": "assistant", "content": response})
            
        except Exception as e:
            print(f"\nError: {e}\n")
            # Remove the failed message from history
            conversation.pop()


if __name__ == "__main__":
    main()
