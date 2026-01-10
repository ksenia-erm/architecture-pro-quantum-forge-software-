from rag_bot import RAGbot
import sys
import signal

def signal_handler(sig, frame):
    """Handle Ctrl+C gracefully"""
    print("\n\n👋 Goodbye!")
    sys.exit(0)

def main():
    print("🚀 Hogwarts Knowledge RAG Bot (Ctrl+C to exit)")
    print("=" * 60)

    # Initialize RAGbot
    bot = RAGbot(chroma_path="../chroma_db")

    # Demo queries for testing
    demo_queries = [
        "Who is Alaric Pendragon?",
        "What happened in the Battle of the Astronomy Tower?",
        "Who is Marcus Thornfield?",
        "Who became Minister for Magic from Marcus's friends?"
    ]

    print("\n📋 Demo Queries:")
    for i, query in enumerate(demo_queries, 1):
        print(f"{i}. {query}")

    print("\n" + "=" * 60)

    # Interactive loop
    try:
        while True:
            query = input("\n❓ ").strip()

            # Handle empty input or exit commands
            if not query or query.lower() in ['exit', 'quit', 'bye', 'q']:
                print("👋 Goodbye!")
                break

            # Skip empty lines
            if not query:
                continue

            # Get RAG response
            print("🤖 ", end="", flush=True)
            answer = bot.query(query)
            print(answer)
            print("-" * 80)

    except KeyboardInterrupt:
        print("\n\n👋 Goodbye!")
    except Exception as e:
        print(f"\n❌ Error: {e}")

if __name__ == "__main__":
    # Handle Ctrl+C
    signal.signal(signal.SIGINT, signal_handler)
    main()
