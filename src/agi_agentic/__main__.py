"""CLI for trying a model's tool calling with a configured SearXNG instance."""
import argparse
import os
from contextlib import ExitStack

from . import Tool, run


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("prompt")
    parser.add_argument("--base-url", default="http://127.0.0.1:8080/v1")
    parser.add_argument("--model", required=True)
    parser.add_argument("--search-url", default=os.getenv("SEARXNG_URL", ""))
    parser.add_argument("--max-rounds", type=int, default=4)
    parser.add_argument("--clock", action="store_true", help="enable the Toolbox clock tool")
    parser.add_argument("--browser-practice", action="store_true", help="enable an isolated browser form exercise")
    parser.add_argument("--show-browser", action="store_true", help="show the browser during the practice exercise")
    args = parser.parse_args()
    tools = []
    if args.search_url:
        try:
            from agi_research import search
        except ImportError:
            parser.error("Install AGi-robot/research to enable search")
        tools.append(Tool("web_search", "Search the web for source titles, URLs and snippets.",
                          {"type": "object", "properties": {"query": {"type": "string", "maxLength": 500}}, "required": ["query"], "additionalProperties": False},
                          lambda query: search(query, base_url=args.search_url)))
    if args.clock:
        try:
            from agi_toolbox import current_time
        except ImportError:
            parser.error("Install AGi-robot/toolbox to enable the clock")
        tools.append(Tool("current_time", "Get the current time in an IANA time zone.",
                          {"type": "object", "properties": {"timezone": {"type": "string"}}, "required": ["timezone"], "additionalProperties": False}, current_time))
    if args.show_browser and not args.browser_practice:
        parser.error("--show-browser requires --browser-practice")
    with ExitStack() as stack:
        if args.browser_practice:
            try:
                from agi_telekinesis import PracticeBrowser
            except ImportError:
                parser.error("Install AGi-robot/telekinesis and its Chromium browser")
            browser = stack.enter_context(PracticeBrowser(headless=not args.show_browser))
            empty = {"type": "object", "properties": {}, "additionalProperties": False}
            tools.extend([
                Tool("browser_observe", "Observe the isolated practice form.", empty, browser.observe),
                Tool("browser_type", "Fill the message field in the practice form.",
                     {"type": "object", "properties": {"text": {"type": "string", "maxLength": 200}}, "required": ["text"], "additionalProperties": False}, browser.type_message),
                Tool("browser_click_submit", "Click submit on the practice form.", empty, browser.click_submit),
            ])
        print(run(args.prompt, base_url=args.base_url, model=args.model, tools=tools,
                  api_key=os.getenv("OPENAI_API_KEY", ""), max_rounds=args.max_rounds))


if __name__ == "__main__":
    main()
