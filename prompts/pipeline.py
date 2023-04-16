# KFP pipeline generation return structure
PIPELINE_TEMPLATE_PROMPT = """
Create a pipeline that runs the component you just created.
- To import the component, use the following: `from lib.components.{COMPONENT_NAME} import {COMPONENT_NAME}`
- Any sensitive information should be stored in the environment variables.
- Any non-sensitive information should be stored in the pipeline arguments. 
- Provide an example parameter_values and add a code comment specifying that user should update the example to their environment specification.
- The pipeline arguments should never include "gcp_credentials".
Follow the following template to generate the example pipeline code:
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
