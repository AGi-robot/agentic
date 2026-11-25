# Agentic

A small experimental tool-calling loop for evaluating an OpenAI-compatible model. The host explicitly registers callable tools; the model can request only those tools. Calls and rounds are bounded. This is a standalone experiment and is not yet connected to Grace's chat or memory.

For web research, install [Research](https://github.com/OppaAI/research) and configure a SearXNG instance with JSON search enabled:

```bash
pip install -e /path/to/research
pip install -e .
grace-agent --model YOUR_MODEL --base-url http://127.0.0.1:8080/v1 --search-url http://127.0.0.1:8888 "Find sources about ROS 2 launch files."
```

Set `OPENAI_API_KEY` if the model endpoint requires a key. Without `--search-url` the CLI sends a plain model request. The model must support OpenAI-compatible function calling and its chat template must be configured accordingly. Search snippets are untrusted and may be incomplete; verify cited sources. Tool calls send search terms to the configured SearXNG instance. No browsing, memory, approval system, or write-capable tools are included.
