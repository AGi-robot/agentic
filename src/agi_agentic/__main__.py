"""CLI for trying a model's tool calling with a configured SearXNG instance."""
import argparse
import os

from . import Tool, run


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("prompt")
    parser.add_argument("--base-url", default="http://127.0.0.1:8080/v1")
    parser.add_argument("--model", required=True)
    parser.add_argument("--search-url", default=os.getenv("SEARXNG_URL", ""))
    parser.add_argument("--max-rounds", type=int, default=4)
    args = parser.parse_args()
    tools = []
    if args.search_url:
        try:
            from agi_research import search
        except ImportError:
            parser.error("Install OppaAI/research to enable search")
        tools.append(Tool("web_search", "Search the web for source titles, URLs and snippets.",
                          {"type": "object", "properties": {"query": {"type": "string", "maxLength": 500}}, "required": ["query"], "additionalProperties": False},
                          lambda query: search(query, base_url=args.search_url)))
    print(run(args.prompt, base_url=args.base_url, model=args.model, tools=tools,
              api_key=os.getenv("OPENAI_API_KEY", ""), max_rounds=args.max_rounds))


if __name__ == "__main__":
    main()
