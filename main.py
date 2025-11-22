from llm import query_deepseek

def main():
    print("🚀 Testing DeepSeek via Ollama...")
    question = "Hello DeepSeek, can you summarize what Speedlink is about in one line?"
    answer = query_deepseek(question)
    print("Model response:", answer)

if __name__ == "__main__":
    main()
