import datetime

from core.BaseAgent import BaseAgent
from app.schemas.AgentExampleOutputSchema import AgentExampleOutput

### Gemini Model
PROMPT_TEMPLATE = """
# Role & Goal
You are a ... .Your primary goal is to ...

# Persona (Optional)
(Define the language to be used in responses to the user, including tone, style, and any other relevant characteristics)

# Rules & Constraints
1.
2.
3.

# Context & Resources
-   **Current Time:** The reference datetime for all relative date calculations.
    `{time}`

# Process / Steps
1.
2.
3.
4.

# Examples (Optional)
### Example 1: (Define task or condition here)
-   **(Input name or User Query or Image or Anything):** (Define Input here)
-   **Reasoning:** (Define Reasoning here).
-   **Final Output:**
    (Define Final Output here)

### Example 2: Count Medicine Boxes using the right side of the drug object
-   **Image 1:** Image 1 shows the right side of the drug
-   **Final Output:** 3
    
### Example 2: xxx
-   **Doctor Name:** dr. Dian Alhusari Sp.JP
-   **Reasoning:** Dr. Dian Alhusari holds the specialist degree Sp.JP, which is a cardiology specialization. Therefore, the medical field of expertise is `cardiology`.
-   **Final Output:** cardiology
"""

class AgentExample(BaseAgent):
    """An agent responsible for ..."""
    def __init__(self, llm, **kwargs):
        super().__init__(
            llm=llm,
            prompt_template=PROMPT_TEMPLATE,
            output_model=AgentExampleOutput,
            **kwargs
        )

    async def __call__(self, state):
        
        self.rebind_prompt_variable(
            time=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        )

        raw, parsed = await self.arun_chain(state=state)

        return parsed
