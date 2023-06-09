# Auto - GPT3.5 Powered KFP Pipelines creator

<strong>Objective:</strong> To create an intelligent agent using GPT3.5, that will develop a KFP component for a given user task. This will then be deployed and tested until successful.

Current Implementation Steps:
- Given a user input tast, the agent will generate a python code snippet of KFP component completing the task.
- If n_shot > 1, another generation step will take place where the model will review and provide accuracy scores for each component code snippet.
- The resulting code snippet will be returned to the user via a gradio interface.

## Quickstart

[direnv](https://direnv.net/) is used to manage environment variables. To use direnv:
- [Install direnv](https://direnv.net/docs/installation.html)
- `cp .envrc.example .envrc`
- Replace `OPENAI_API_KEY` with your OpenAI API key
- (<i>optional</i>) Replace `MODEL_NAME` with the name of the model you want to use. Options are {`gpt-3.5-turbo`, `gpt-4`}
- Run `direnv allow` in the root of the project.

<br>  

To install packages and run the lightweight ComponentGen gradio server:
```
# Install poetry
pip install --upgrade poetry 

# Poetry install packages
poetry install

# Run lightweight Gradio server
poetry run python pipelines/AutoGradioInterface.py
```

The gradio interface will be available at `http://localhost:7860/`

To run the WIP full application:
```
poetry run python pipelines/AutoGradioBlocks.py
```

## User Journeys

### 1. Create a KFP component for a given task

![ComponentGen](./resources/componentgen.png)

Component generation can also be done via the API. The API is available at `http://127.0.0.1:7860/run/generate_component`.  
The API accepts a POST request with the following parameters:
![ComponentGenAPI](./resources/componentapi.png)

### 2. Refine and update the component accuracy review prompt

![ReviewPrompt](./resources/reviewprompt.png)

### 3. Create a KFP pipeline to run the component

![PipelineGen](./resources/pipelinegen.png)