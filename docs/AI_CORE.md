# AI Core & Agent Framework Documentation: AIMOS

## 1. Overview

AIMOS AI Core provides a vendor-agnostic, multi-agent foundation powered by **LangGraph** and an abstract **LLM Provider Layer**.

---

## 2. LLM Provider Abstraction Layer

AIMOS is not locked into any single LLM vendor. All model providers implement the `BaseLLMProvider` interface:

```
                         +-------------------+
                         |  BaseLLMProvider  |
                         +---------+---------+
                                   |
         +-----------------+-------+-------+-----------------+
         |                 |               |                 |
         v                 v               v                 v
+-----------------+ +--------------+ +-----------+ +------------------+
| MockLLMProvider | | OpenAIProvider| |Anthropic..| | GeminiProvider   |
| (0 Cost / Test) | | (gpt-4o-mini)| |(claude.. )| | (gemini-1.5-flash)|
+-----------------+ +--------------+ +-----------+ +------------------+
```

### Factory Resolution (`LLMProviderFactory`)
- `LLMProviderFactory.get_provider("mock")` $\rightarrow$ `MockLLMProvider`
- `LLMProviderFactory.get_provider("openai")` $\rightarrow$ `OpenAIProvider` (Falls back to `MockLLMProvider` if `OPENAI_API_KEY` is missing)
- `LLMProviderFactory.get_provider("anthropic")` $\rightarrow$ `AnthropicProvider` (Falls back to `MockLLMProvider` if `ANTHROPIC_API_KEY` is missing)
- `LLMProviderFactory.get_provider("gemini")` $\rightarrow$ `GeminiProvider` (Falls back to `MockLLMProvider` if `GEMINI_API_KEY` is missing)

---

## 3. Agent Framework & LangGraph

Agents extend `BaseAgent` and use `AgentState` to manage context across execution nodes:

```
[ Input Node ] ──► [ Tool Executor Node ] ──► [ LLM Reasoner Node ] ──► [ Result Output ]
```

### Safety & Tool Isolation
- Agents **NEVER** call external APIs directly.
- Agents interact only through `BaseTool` abstractions (e.g., `ProductLookupTool`).

---

## 4. Execution Persistence & Cost Tracking

- `agent_runs`: Stores run status, execution time in ms, input payload, and structured output.
- `llm_usages`: Tracks prompt/completion/total token count and estimated cost per execution.
- `audit_logs`: Records `AGENT_STARTED`, `AGENT_COMPLETED`, and `AGENT_FAILED` events.
