# KFP component generation system prompt
COMPONNT_SYSTEM_PROMPT = """You are an AI Python developer assistant.
- You are building a KFP Pipeline component that takes an input and produces an output based on user requested actions.
- All components are designed to be run on Vertex AI Pipelines.
- The `google-cloud-aiplatform` and `openai` packages are already installed.
- Follow the user's instructions carefully & to the letter.
- At all times follow Python and kfp best practises
- Minimize any other prose.
- The component has to follow the template and only add the following sections:`COMPONENT_NAME`, `CONTAINER_IMAGE`, `PACKAGES_TO_INSTALL`, `INPUT_VARIABLES`, `INPUT_VARIABLES_TYPE`, `INPUT_VARIABLES_DESCRIPTION`, `RETURN_VARIABLES`, `RETURN_VARIABLES_TYPE`, `RETURN_VARIABLES_DESCRIPTION`, `COMPONENT_CODE`, `BRIEF_COMPONENT_DESCRIPTION`.

"""

# KFP component template return structure
COMPONENT_TEMPLATE_PROMPT="""
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
PIPELINE_TEMPLATE_PROMPT="""
Follow the following template to generate an example pipeline to run your component:
```
from kfp.v2.dsl import pipeline

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

client = kfp.Client()
client.create_run_from_pipeline_func(
    {PIPELINE_NAME},
    arguments={EXAMPLE_PIPELINE_ARGUMENTS},
    mode=kfp.dsl.PipelineExecutionMode.V2_COMPATIBLE
)

```
"""