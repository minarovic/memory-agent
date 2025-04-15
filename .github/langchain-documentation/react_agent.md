>> from langchain_openai import ChatOpenAI
>>> from langgraph.prebuilt import create_react_agent


... def check_weather(location: str) -> str:
...     '''Return the weather forecast for the specified location.'''
...     return f"It's always sunny in {location}"
>>>
>>> tools = [check_weather]
>>> model = ChatOpenAI(model="gpt-4o")
>>> graph = create_react_agent(model, tools=tools)
>>> inputs = {"messages": [("user", "what is the weather in sf")]}
>>> for s in graph.stream(inputs, stream_mode="values"):
...     message = s["messages"][-1]
...     if isinstance(message, tuple):
...         print(message)
...     else:
...         message.pretty_print()
('user', 'what is the weather in sf')
================================== Ai Message ==================================
Tool Calls:
check_weather (call_LUzFvKJRuaWQPeXvBOzwhQOu)
Call ID: call_LUzFvKJRuaWQPeXvBOzwhQOu
Args:
    location: San Francisco
================================= Tool Message =================================
Name: check_weather
It's always sunny in San Francisco
================================== Ai Message ==================================
The weather in San Francisco is sunny.
Add a system prompt for the LLM:

>>> system_prompt = "You are a helpful bot named Fred."
>>> graph = create_react_agent(model, tools, prompt=system_prompt)
>>> inputs = {"messages": [("user", "What's your name? And what's the weather in SF?")]}
>>> for s in graph.stream(inputs, stream_mode="values"):
...     message = s["messages"][-1]
...     if isinstance(message, tuple):
...         print(message)
...     else:
...         message.pretty_print()
('user', "What's your name? And what's the weather in SF?")
================================== Ai Message ==================================
Hi, my name is Fred. Let me check the weather in San Francisco for you.
Tool Calls:
check_weather (call_lqhj4O0hXYkW9eknB4S41EXk)
Call ID: call_lqhj4O0hXYkW9eknB4S41EXk
Args:
    location: San Francisco
================================= Tool Message =================================
Name: check_weather
It's always sunny in San Francisco
================================== Ai Message ==================================
The weather in San Francisco is currently sunny. If you need any