import argparse
import json
import os
import sys
from typing import cast

from openai import OpenAI
from openai.types.chat import ChatCompletionMessageParam
from openai.types.chat.chat_completion_assistant_message_param import (
    ChatCompletionAssistantMessageParam,
)
from openai.types.chat.chat_completion_message_tool_call import (
    ChatCompletionMessageToolCall,
    ChatCompletionMessageToolCallUnion,
)
from openai.types.chat.chat_completion_message_tool_call_param import (
    ChatCompletionMessageToolCallParam,
)
from openai.types.chat.chat_completion_tool_message_param import (
    ChatCompletionToolMessageParam,
)
from openai.types.chat.chat_completion_tool_param import (
    ChatCompletionToolParam,
)
from openai.types.chat.chat_completion_user_message_param import (
    ChatCompletionUserMessageParam,
)
from openai.types.shared_params import FunctionDefinition

import app.tools as my_tools

API_KEY = os.getenv("OPENROUTER_API_KEY")
BASE_URL = os.getenv("OPENROUTER_BASE_URL", default="https://openrouter.ai/api/v1")


def parse_args() -> str:
    parser = argparse.ArgumentParser()
    parser.add_argument("-p", "--prompt", type=str, help="LLM Prompt")
    args = parser.parse_args()
    return str(args.prompt)


def get_answer(client: OpenAI, prompt: str) -> str:
    tools: list[ChatCompletionToolParam] = [
        ChatCompletionToolParam(
            type="function",
            function=FunctionDefinition(
                name="Read",
                description="Read and return the contents of a file",
                parameters={
                    "type": "object",
                    "properties": {
                        "file_path": {
                            "type": "string",
                            "description": "The path to the file to read",
                        }
                    },
                    "required": ["file_path"],
                },
            ),
        ),
        ChatCompletionToolParam(
            type="function",
            function=FunctionDefinition(
                name="Write",
                description="Write content to a file",
                parameters={
                    "type": "object",
                    "properties": {
                        "file_path": {
                            "type": "string",
                            "description": "The path of the file to write to",
                        },
                        "content": {
                            "type": "string",
                            "description": "The content to write to the file",
                        },
                    },
                    "required": ["file_path", "content"],
                },
            ),
        ),
    ]
    messages: list[ChatCompletionMessageParam] = [
        ChatCompletionUserMessageParam(role="user", content=prompt)
    ]
    chat = client.chat.completions.create(
        model="anthropic/claude-haiku-4.5",
        messages=messages,
        tools=tools,
    )
    if not chat.choices or len(chat.choices) != 1:
        raise NotImplementedError
    answer = chat.choices[0]

    while answer.finish_reason != "stop":
        tool_calls: list[ChatCompletionMessageToolCallUnion] | None = answer.message.tool_calls
        if tool_calls is None or len(tool_calls) != 1:
            raise NotImplementedError
        tool_call = cast(ChatCompletionMessageToolCall, tool_calls[0])
        function = tool_call.function
        arguments = json.loads(function.arguments)
        if function.name == "Read":
            tool_data = my_tools.read(file_path=arguments["file_path"])
        elif function.name == "Write":
            tool_data = my_tools.write(
                file_path=arguments["file_path"], content=arguments["content"]
            )
        else:
            raise NotImplementedError
        messages.append(
            ChatCompletionAssistantMessageParam(
                role="assistant",
                tool_calls=[
                    ChatCompletionMessageToolCallParam(
                        id=tool_call.id,
                        type="function",
                        function={"name": function.name, "arguments": function.arguments},
                    ),
                ],
            )
        )
        messages.append(
            ChatCompletionToolMessageParam(
                role="tool", tool_call_id=tool_call.id, content=tool_data
            )
        )
        print(f"messages = {messages}", file=sys.stderr)
        chat = client.chat.completions.create(
            model="anthropic/claude-haiku-4.5",
            messages=messages,
            tools=tools,
        )
        if not chat.choices or len(chat.choices) != 1:
            raise NotImplementedError
        answer = chat.choices[0]

    result = answer.message.content
    if result is None:
        raise NotImplementedError
    return result


def main() -> None:
    prompt = parse_args()

    if not API_KEY:
        raise RuntimeError("OPENROUTER_API_KEY is not set")

    client = OpenAI(api_key=API_KEY, base_url=BASE_URL)

    print(get_answer(client, prompt))


if __name__ == "__main__":
    main()
