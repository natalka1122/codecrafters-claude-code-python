import argparse
import json
import os
from typing import cast

from openai import OpenAI
from openai.types.chat.chat_completion_message_tool_call import (
    ChatCompletionMessageToolCall,
    ChatCompletionMessageToolCallUnion,
)
from openai.types.chat.chat_completion_tool_param import (
    ChatCompletionToolParam,
)
from openai.types.shared_params import FunctionDefinition

API_KEY = os.getenv("OPENROUTER_API_KEY")
BASE_URL = os.getenv("OPENROUTER_BASE_URL", default="https://openrouter.ai/api/v1")


def parse_args() -> str:
    parser = argparse.ArgumentParser()
    parser.add_argument("-p", "--prompt", type=str, help="LLM Prompt")
    args = parser.parse_args()
    return str(args.prompt)


def read_tool(file_path: str) -> str:
    with open(file=file_path, mode="r") as f:
        return "\n".join(f.readlines())


def main() -> None:
    prompt = parse_args()

    if not API_KEY:
        raise RuntimeError("OPENROUTER_API_KEY is not set")

    client = OpenAI(api_key=API_KEY, base_url=BASE_URL)

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
        )
    ]
    chat = client.chat.completions.create(
        model="anthropic/claude-haiku-4.5",
        messages=[{"role": "user", "content": prompt}],
        tools=tools,
    )

    if not chat.choices or len(chat.choices) != 1:
        raise NotImplementedError

    tool_calls: list[ChatCompletionMessageToolCallUnion] | None = chat.choices[0].message.tool_calls
    if tool_calls is None:
        print(chat.choices[0].message.content)
        return
    if len(tool_calls) != 1:
        raise NotImplementedError
    tool_call = cast(ChatCompletionMessageToolCall, tool_calls[0])
    function = tool_call.function
    if function.name != "Read":
        raise NotImplementedError

    arguments = json.loads(function.arguments)
    print(read_tool(file_path=arguments["file_path"]))


if __name__ == "__main__":
    main()
