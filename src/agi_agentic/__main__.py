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
    parser.add_argument("--weather", action="store_true", help="enable Open-Meteo weather by coordinates")
    parser.add_argument("--lighting-url", default="", help="enable lighting tools using this independent lighting service URL")
    parser.add_argument("--desktop", action="store_true", help="enable approved real desktop actions")
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
    if args.weather:
        try:
            from agi_toolbox.weather import current_weather
        except ImportError:
            parser.error("Install AGi-robot/toolbox to enable weather")
        tools.append(Tool("current_weather", "Get current weather for latitude and longitude; ask the user if unknown.",
                          {"type": "object", "properties": {"latitude": {"type": "number"}, "longitude": {"type": "number"}}, "required": ["latitude", "longitude"], "additionalProperties": False}, current_weather))
    if args.lighting_url:
        try:
            from agi_toolbox.lighting import LightingClient, LIGHTING_PARAMETERS, LIGHTING_DESCRIPTION, SAVE_LIGHTING_PARAMETERS, STOP_LIGHTING_PARAMETERS
        except ImportError:
            parser.error("Install Project-AGi/toolbox with lighting support")
        lighting = LightingClient(args.lighting_url)
        empty = {"type": "object", "properties": {}, "additionalProperties": False}
        tools.extend([
            Tool("lighting_catalog", "Read editable colour names and saved lighting effects.", empty, lighting.catalog),
            Tool("save_lighting_preset", "Add or replace an effect and optional named colours in the persistent Markdown catalogue. New rhythms can use rhythm_pattern. Does not activate the effect.", SAVE_LIGHTING_PARAMETERS, lighting.save_preset),
            Tool("set_lighting", LIGHTING_DESCRIPTION, LIGHTING_PARAMETERS, lighting.set_effect),
            Tool("lighting_status", "Inspect the current lighting effect and device connection.", empty, lighting.status),
            Tool("stop_lighting", "Restore default activity lighting with a brief reason.", STOP_LIGHTING_PARAMETERS, lighting.stop),
        ])
    if args.desktop:
        if not os.isatty(0):
            parser.error("--desktop requires an interactive terminal for per-action approval")
        try:
            from agi_telekinesis.desktop import Desktop
            desktop = Desktop(lambda action: input(f"{action} [y/N] ").strip().lower() == "y")
        except ImportError:
            parser.error("Install AGi-robot/telekinesis with the desktop extra")
        empty = {"type": "object", "properties": {}, "additionalProperties": False}
        tools.extend([
            Tool("desktop_size", "Get primary screen dimensions; you cannot see the screen.", empty, desktop.screen_size),
            Tool("desktop_click", "Click a user-supplied screen coordinate after approval.",
                 {"type": "object", "properties": {"x": {"type": "integer"}, "y": {"type": "integer"}}, "required": ["x", "y"], "additionalProperties": False}, desktop.click),
            Tool("desktop_type", "Type printable ASCII into the focused window after approval.",
                 {"type": "object", "properties": {"text": {"type": "string", "maxLength": 200}}, "required": ["text"], "additionalProperties": False}, desktop.type_text),
        ])
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
