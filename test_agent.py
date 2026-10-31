import os
import json
from openai import OpenAI
from dotenv import load_dotenv

# 1. Load API Key securely
load_dotenv(os.path.join(os.path.dirname(__file__), '.env'))
api_key = os.getenv("API_KEY")

client = OpenAI(
    api_key=api_key,
    base_url="https://open.bigmodel.cn/api/paas/v4/"
)

# 2. Define a Python function (This is the Agent's "hand")
def check_deployment_status(passed_tests: int, failed_tests: int) -> str:
    if failed_tests > 0:
        return f"ABORT DEPLOYMENT. {failed_tests} tests failed. Fix them first."
    else:
        return "DEPLOYMENT APPROVED. All tests passed."

# 3. Describe the tool to the AI (This is the Agent's "menu")
tools = [
    {
        "type": "function",
        "function": {
            "name": "check_deployment_status",
            "description": "Check if it is safe to deploy to production based on test results",
            "parameters": {
                "type": "object",
                "properties": {
                    "passed_tests": {"type": "integer", "description": "Number of passed tests"},
                    "failed_tests": {"type": "integer", "description": "Number of failed tests"}
                },
                "required": ["passed_tests", "failed_tests"]
            }
        }
    }
]

# 4. Ask a question that requires the AI to use the tool
messages = [
    {"role": "user", "content": "I just ran the CI pipeline. Out of 240 tests, 236 passed and 4 failed. Should I deploy to production?"}
]

print("Thinking...\n")

# First call: Ask the AI
response = client.chat.completions.create(
    model="glm-4-flash",
    messages=messages,
    tools=tools
)

response_message = response.choices[0].message

# 5. Check if the AI decided to call our Python function
if response_message.tool_calls:
    print("🤖 AI decided to use a Tool!")
    for tool_call in response_message.tool_calls:
        function_name = tool_call.function.name
        args = json.loads(tool_call.function.arguments)
        
        print(f"🔧 AI called function: {function_name} with arguments: {args}")
        
        # 6. Execute the actual Python function
        result = check_deployment_status(passed_tests=args["passed_tests"], failed_tests=args["failed_tests"])
        print(f"🐍 Python function returned: {result}\n")
        
        # 7. Give the result back to the AI
        messages.append(response_message)
        messages.append({
            "role": "tool",
            "tool_call_id": tool_call.id,
            "name": function_name,
            "content": str(result)
        })
        
    # Second call: AI reads the tool result and talks to you
    final_response = client.chat.completions.create(
        model="glm-4-flash",
        messages=messages,
        tools=tools
    )
    print("--- Final AI Response ---")
    print(final_response.choices[0].message.content)
else:
    print("AI didn't use any tools.")
    print(response_message.content)