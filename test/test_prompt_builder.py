from src.modules.llm.application.prompt_builder import PromptBuilder

from src.modules.llm.domain.entities import (
    LLMRequest,
    LLMMessage,
)

from src.modules.llm.domain.value_objects import (
    ProviderName,
    Role,
)


builder = PromptBuilder()


def run_test(name, request):
    print(f"\n===== {name} =====")

    try:
        messages = builder.build(request)

        print("✅ SUCCESS")

        for message in messages:
            print(f"{message.role}: {message.content}")

    except Exception as e:
        print("❌ FAILED")
        print(e)


# ------------------------------------------
# Test 1
# Valid Request
# ------------------------------------------

run_test(
    "Valid Request",
    LLMRequest(
        provider=ProviderName.OPENAI,
        model="gpt-4o-mini",
        messages=[
            LLMMessage(
                role=Role.USER,
                content="Hello"
            )
        ]
    )
)

# ------------------------------------------
# Test 2
# Trim Spaces
# ------------------------------------------

run_test(
    "Trim Spaces",
    LLMRequest(
        provider=ProviderName.OPENAI,
        model="gpt-4o-mini",
        messages=[
            LLMMessage(
                role=Role.USER,
                content="     Hello GPT     "
            )
        ]
    )
)

# ------------------------------------------
# Test 3
# Empty Message
# ------------------------------------------

run_test(
    "Empty Message",
    LLMRequest(
        provider=ProviderName.OPENAI,
        model="gpt-4o-mini",
        messages=[
            LLMMessage(
                role=Role.USER,
                content="       "
            )
        ]
    )
)

# ------------------------------------------
# Test 4
# Assistant First
# ------------------------------------------

run_test(
    "Assistant First",
    LLMRequest(
        provider=ProviderName.OPENAI,
        model="gpt-4o-mini",
        messages=[
            LLMMessage(
                role=Role.ASSISTANT,
                content="Hello"
            )
        ]
    )
)

# ------------------------------------------
# Test 5
# Two System Messages
# ------------------------------------------

run_test(
    "Two System Messages",
    LLMRequest(
        provider=ProviderName.OPENAI,
        model="gpt-4o-mini",
        messages=[
            LLMMessage(
                role=Role.SYSTEM,
                content="A"
            ),
            LLMMessage(
                role=Role.SYSTEM,
                content="B"
            ),
        ]
    )
)

# ------------------------------------------
# Test 6
# System Not First
# ------------------------------------------

run_test(
    "System Not First",
    LLMRequest(
        provider=ProviderName.OPENAI,
        model="gpt-4o-mini",
        messages=[
            LLMMessage(
                role=Role.USER,
                content="Hello"
            ),
            LLMMessage(
                role=Role.SYSTEM,
                content="You are helpful"
            ),
        ]
    )
)