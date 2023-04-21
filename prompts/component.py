## COMPONENT PROMPTS
# KFP component generation system prompt
COMPONENT_SYSTEM_PROMPT = """You are an AI Python developer assistant.
- You are building a KFP Pipeline component that takes an input and produces an output based on user requested actions.
- All components are designed to be run on Vertex AI Pipelines.
- The `google-cloud-aiplatform` and `openai` packages are already installed.
- Follow the user's instructions carefully & to the letter.
- At all times follow Python and kfp best practises
- Minimize any other prose.
- The component has to follow the template and only add the following sections:`COMPONENT_NAME`, `CONTAINER_IMAGE`, `PACKAGES_TO_INSTALL`, `INPUT_VARIABLES`, `INPUT_VARIABLES_TYPE`, `INPUT_VARIABLES_DESCRIPTION`, `RETURN_VARIABLES`, `RETURN_VARIABLES_TYPE`, `RETURN_VARIABLES_DESCRIPTION`, `COMPONENT_CODE`, `BRIEF_COMPONENT_DESCRIPTION`.

"""

# KFP component generation example component
_example_prompt_input = "Write a component that validates a CSV dataset against a Great Expectations suite and create Data Doc (a validation report). This component fails if validation is not successful."
with open("examples/great_expectations_validate_csv.py") as example_file:
    _example_text = example_file.read()
COMPONENT_SYSTEM_EXAMPLE = (
    f"# Example component\n{_example_prompt_input}\n```\n{_example_text}\n```\n"
)
COMPONENT_SYSTEM_FULL_CONTEXT = f"{COMPONENT_SYSTEM_PROMPT}\n{COMPONENT_SYSTEM_EXAMPLE}"

# TODO: Incorporate kfp inputs/output datasets (https://stackoverflow.com/questions/73953744/how-to-test-kfp-components-with-pytest)
# KFP component template return structure
COMPONENT_TEMPLATE_PROMPT = """
Follow the following template to generate the code for your component:
```
from kfp.v2.dsl import Dataset, Input, Output, Model, component
from pathlib import Path


@component(
    base_image="{CONTAINER_IMAGE}",
    packages_to_install=[{PACKAGES_TO_INSTALL}],
    output_component_file=str(Path(__file__).with_suffix(".yaml")),
)
def {COMPONENT_NAME}(
    {INPUT_VARIABLES}: {INPUT_VARIABLES_TYPE},
) -> None:
    \"""{BRIEF_COMPONENT_DESCRIPTION}

    Args:
        {INPUT_VARIABLES} ({INPUT_VARIABLES_TYPE}): {INPUT_VARIABLES_DESCRIPTION}

    Returns:
        {RETURN_VARIABLES} ({RETURN_VARIABLES_TYPE}): {RETURN_VARIABLES_DESCRIPTION}
    \"""
    import logging

    logging.getLogger().setLevel(logging.INFO)
    
    import {PACKAGES_TO_INSTALL}
    {COMPONENT_CODE}
    
```
"""

UNIT_TEST_PROMPT = """
Write a unit test for the component code.
- Provide example input and output data for the component and test that the component runs successfully, providing the correct output.
- Any calls to external services, use the `mock` package to mock the response.
- Any uploads to GCS should be mocked.
- Import the component method as `from lib.component.{COMPONENT_NAME} import {COMPONENT_NAME}`.
"""

# KFP component review system prompt
REVIEW_PROMPT = """
Review the following kfp component code snippets and return a snippet_name, accuracy_score (percentage %) and accuracy_summary for each component.

The accuracy_score should be in percentage format and based on how closely the snippets follows:
- Ability to complete the users request
- The correct python packages have been added to `packages_to_install` and then imported in the component method code.
- System kfp component template
- Penalise for importing component packages at the top of the snippet and not in the component method.
- Penalise for not importing the logging package in the component
"""
