# Agentic

A small experimental tool-calling loop for evaluating an OpenAI-compatible model. The host explicitly registers callable tools; the model can request only those tools. Calls and rounds are bounded. This is a standalone experiment and is not yet connected to Grace's chat or memory.

For web research, install [Research](https://github.com/AGi-robot/research) and configure a SearXNG instance with JSON search enabled:

```bash
pip install -e /path/to/research
pip install -e .
grace-agent --model YOUR_MODEL --base-url http://127.0.0.1:8080/v1 --search-url http://127.0.0.1:8888 "Find sources about ROS 2 launch files."
```

Install [Toolbox](https://github.com/AGi-robot/toolbox) and use `--clock` to enable its time tool. To try browser control, install [Telekinesis](https://github.com/AGi-robot/telekinesis), run `python -m playwright install chromium`, and try:

```bash
grace-agent --model YOUR_MODEL --browser-practice --show-browser --max-rounds 6 "Enter Hello Grace in the form and submit it, then report the result."
```

The browser exercise uses an isolated built-in page. It cannot access real websites or your desktop. Set `OPENAI_API_KEY` if the model endpoint requires a key. The model must support OpenAI-compatible function calling and its chat template must be configured accordingly. Search snippets are untrusted and may be incomplete; verify cited sources. Search terms go to the configured SearXNG instance. Grace chat and memory are not yet connected.

Use `--weather` for Open-Meteo current weather by latitude and longitude. Use `--desktop` after installing Telekinesis with `pip install -e '/path/to/telekinesis[desktop]'` to expose primary-screen size, clicks and ASCII typing on the actual desktop. Each click and typing action requires confirmation in the terminal. Provide coordinates yourself: this runner does not send screenshots to the model. PyAutoGUI's corner fail-safe is enabled.
