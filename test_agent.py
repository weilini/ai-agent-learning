import os
from openai import OpenAI
from dotenv import load_dotenv

# 1. Load API Key
load_dotenv(os.path.join(os.path.dirname(__file__), '.env'))
api_key = os.getenv("API_KEY")

client = OpenAI(
    api_key=api_key,
    base_url="https://open.bigmodel.cn/api/paas/v4/"
)

# 2. Simulate a real Pytest failure log (This is the bug we had earlier!)
test_failure_log = """
FAILED tests/test_basics.py::TestCelsiusToFahrenheit::test_extreme_temperature
assert celsius_to_fahrenheit(-273.15) == -459.67
E       assert -459.66999999999996 == -459.67
E        +  where -459.66999999999996 = celsius_to_fahrenheit(-273.15)
tests/test_basics.py:26: AssertionError
"""

# 3. Ask the AI Agent to analyze the log and suggest a fix
print("🤖 Sending test failure log to AI Agent for analysis...\n")

prompt = f"""
You are an expert QA Automation Engineer. 
I have a Pytest failure in my CI pipeline. Here is the error log:

{test_failure_log}

Please do three things:
1. Explain in simple English why this test failed.
2. Tell me exactly how to fix the Python code.
3. Suggest a better way to write the assertion.
"""

response = client.chat.completions.create(
    model="glm-4-flash",
    messages=[
        {"role": "user", "content": prompt}
    ]
)

print("--- AI Agent Root Cause Analysis ---")
print(response.choices[0].message.content)
print("------------------------------------\n")