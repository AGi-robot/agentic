# Agentic

A small experimental tool-calling loop for evaluating an OpenAI-compatible model. The host explicitly registers callable tools; the model can request only those tools. Calls and rounds are bounded. This is a standalone experiment and is not yet connected to AIVA's chat or memory.

For web research, install [Research](https://github.com/Project-AGi/research) and configure a SearXNG instance with JSON search enabled:

```bash
pip install -e /path/to/research
pip install -e .
aiva-agent --model YOUR_MODEL --base-url http://127.0.0.1:8080/v1 --search-url http://127.0.0.1:8888 "Find sources about ROS 2 launch files."
```

Install [Toolbox](https://github.com/Project-AGi/toolbox) and use `--clock` to enable its time tool. To try browser control, install [Telekinesis](https://github.com/Project-AGi/telekinesis), run `python -m playwright install chromium`, and try:

```bash
aiva-agent --model YOUR_MODEL --browser-practice --show-browser --max-rounds 6 "Enter Hello AIVA in the form and submit it, then report the result."
```

The browser exercise uses an isolated built-in page. It cannot access real websites or your desktop. Set `OPENAI_API_KEY` if the model endpoint requires a key. The model must support OpenAI-compatible function calling and its chat template must be configured accordingly. Search snippets are untrusted and may be incomplete; verify cited sources. Search terms go to the configured SearXNG instance. AIVA chat and memory are not yet connected.

Use `--weather` for Open-Meteo current weather by latitude and longitude. Use `--desktop` after installing Telekinesis with `pip install -e '/path/to/telekinesis[desktop]'` to expose primary-screen size, clicks and ASCII typing on the actual desktop. Each click and typing action requires confirmation in the terminal. Provide coordinates yourself: this runner does not send screenshots to the model. PyAutoGUI's corner fail-safe is enabled.

## Expressive lighting tool

Install the matching Toolbox lighting client and run the independent Toolbox lighting service (`aiva-lighting`):

```bash
python -m agi_agentic 'Hello AIVA, how are you?' --model MODEL_NAME --lighting-url http://127.0.0.1:8854
```

This exposes `set_lighting`, `lighting_status`, and `stop_lighting` with automatic tool choice. The model chooses whether to use lighting. No occasion or mood triggers are imposed. Colours, transitions, rainbow, brightness and rhythms follow [Toolbox's lighting contract](https://github.com/Project-AGi/toolbox/blob/dev/LIGHTING.md).

The same flag also offers `lighting_catalog` and `save_lighting_preset` so the model can read and expand the editable Markdown catalogue, including new colours and programmable rhythm patterns.

Set/save/stop tools require a brief reason and saved effects can describe a personal signal's meaning. Use `preset='default'` to restore activity lighting. Regular chat's persistent reason memory is handled by Interactive and Memory; this standalone CLI does not write AIVA's conversation database.
