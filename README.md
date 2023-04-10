# Auto - GPT3.5 Powered KFP Pipelines creator

<strong>Objective:</strong> To create an intelligent agent using GPT3.5, that will develop a KFP component for a given user task. This will then be deployed and tested until successful.

Current Implementation Steps:
- Given a user input tast, the agent will generate a python code snippet of KFP component completing the task.
- If n_shot > 1, another generation step will take place where the model will review and provide accuracy scores for each component code snippet.
- The resulting code snippet will be returned to the user. If n_shot > 1, it'll also contain the accuracy scores and summary of component accuracy. 