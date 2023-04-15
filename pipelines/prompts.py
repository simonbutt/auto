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
print(COMPONENT_SYSTEM_EXAMPLE)
COMPONENT_SYSTEM_FULL_CONTEXT = f"{COMPONENT_SYSTEM_PROMPT}\n{COMPONENT_SYSTEM_EXAMPLE}"

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

# KFP component review system prompt
REVIEW_NSHOT_PROMPT = """
Review the following kfp component code snippets and return a snippet_name, accuracy_score and accuracy_summary for each component.

The accuracy_score should be in percentage format and based on how closely the snippets follows:
- Ability to complete the users request
- The correct python packages have been added to `packages_to_install` and then imported in the component method code.
- System kfp component template
- Penalise for importing component packages at the top of the snippet and not in the component method.
- Penalise for not importing the logging package in the component
"""


# KFP component review return structure
REVIEW_RETURN_STRUCT = """
--------
Return the message in the following JSON list structure

[
  {
    "snippet_name": int,
    "accuracy_score": int,
    "accuracy_summary": string
  }
]
"""

# KFP pipeline generation return structure
PIPELINE_TEMPLATE_PROMPT = """
Follow the following template to generate an example pipeline to run your component:
```
from kfp.v2.dsl import pipeline
import google.cloud.aiplatform as aip

@pipeline(
    name="{PIPELINE_NAME}",
    description="",
    pipeline_root=""
)
def {COMPONENT_NAME}_pipeline(
    {INPUT_VARIABLES}: {INPUT_VARIABLES_TYPE},
):
    "A pipeline that runs {COMPONENT_NAME}"
    {PIPELINE_CODE}



pipeline_arguments={EXAMPLE_PIPELINE_ARGUMENTS}

from kfp.v2 import compiler
compiler.Compiler().compile(pipeline_func={PIPELINE_NAME},
        package_path="lib/pipelines/{PIPELINE_NAME}.json")


# Before initializing, make sure to set the GOOGLE_APPLICATION_CREDENTIALS
# environment variable to the file path of your service account.
aip.init(
    project=PROJECT_ID,
    location=PROJECT_REGION,
)

# Prepare the pipeline job
job = aip.PipelineJob(
    display_name={PIPELINE_NAME},
    template_path="lib/pipelines/{PIPELINE_NAME}.json",
    pipeline_root=pipeline_root_path,
    parameter_values={
        'project_id': PROJECT_ID
    }
)

job.submit()

```
"""
