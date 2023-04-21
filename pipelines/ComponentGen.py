from langchain.chat_models import ChatOpenAI
from langchain.prompts.chat import (
    ChatPromptTemplate,
    SystemMessagePromptTemplate,
    AIMessagePromptTemplate,
    HumanMessagePromptTemplate,
)
from langchain.schema import AIMessage, HumanMessage, SystemMessage
import json
import prompts.component as component_prompt
import subprocess
import logging


class ComponentGen:

    """
    PipelineGen is a class that contains the methods to generate Vertex pipeline components based on the user's input.

    PipelineGen uses the OpenAI GPT-3 API to generate the code.
    It will then attempt to deploy the code to the user's Google Cloud environment and learn from failed pipeline runs.
    """

    def __init__(
        self, model_name: str, temperature: float = 0.7, review_temperature: float = 0.2
    ) -> None:
        self.system_context = f"{component_prompt.COMPONENT_SYSTEM_FULL_CONTEXT}\n{component_prompt.COMPONENT_TEMPLATE_PROMPT}"
        self.chat = ChatOpenAI(
            model_name=model_name,
            temperature=temperature,
        )
        self.review = ChatOpenAI(
            model_name=model_name,
            temperature=review_temperature,
        )

        self.template_prompt = component_prompt.COMPONENT_TEMPLATE_PROMPT
        self.review_prompt = component_prompt.REVIEW_PROMPT

    def _get_code(self, generated_text: dict) -> str:
        response_code_list = generated_text.split("```")
        if len(response_code_list) > 1:
            return response_code_list[1].removeprefix("\n")
        else:
            logging.warning(
                "Generated response snippet doesn't contain ``` code block, highly likely to be incorrect"
            )
            return response_code_list[0]

    def _generate_component_snippet(self, input_content) -> str:
        """
        Generates a KFP component based on the user's input.

        TODO: Look into autoprompt/similar and provide a better way to do n_shot by varying the prompt.
        """

        ai_message = self.chat(component_message_chain)
        return self._get_code(ai_message.content)

    def _review_component(self, input_content: str, generated_component: str) -> str:
        """
        Takes n component code snippets and returns the snippet with the highest accuracy score.
        This score is determined by the model and is based on prompt.REVIEW_NSHOT_PROMPT.
        """

        component_snippet_text = f"Component request: {input_content}\nGenerated component:\n```\n{generated_component}\n```\n"
        logging.debug(component_snippet_text)

        review_message_chain = [
            SystemMessage(content=self.review_prompt),
            HumanMessage(content=f"{component_snippet_text}"),
        ]

        review_ai_response = self.review(review_message_chain)
        return review_ai_response.content

    def update_review_prompt(self, review_prompt: str) -> None:
        """
        Updates the review prompt used by the review_n_components method.
        """
        self.review_prompt = review_prompt

    def write_to_file(self, component_code: str, component_test: str) -> None:
        """
        Writes the component code to a .py file
        """
        component_name = component_code.split("def ")[1].split("(")[0]
        test_name = f"test_{component_name}"

        with open(f"./lib/component/{component_name}.py", "w") as f:
            f.write(component_code)
        with open(f"./lib/component/{test_name}.py", "w") as f:
            f.write(component_test)

    def generate_component(self, input_content, write_test=True):
        """
        Completes an iteration of:
        - Given latest input, model generates code
        - Model code is written to file as a pipeline component
        - Component is compiled
        - Example pipeline run including only the component code is created
        - Human evaluates the pipeline run code and approves
        - pipeline is deployed and successfully runs on Vertex AI
        - Test output data against expected output.

        If the pipeline run fails, the self.message_chain is updated and the process is repeated.
        """
        if input_content == "":
            return (
                "No input description... \n Recommend trying one of the examples!",
                "",
            )

        component_message_chain = [
            SystemMessage(content=self.system_context),
            HumanMessage(content=input_content),
        ]

        # Generate component code and output to .py file
        component_ai_message = self.chat(component_message_chain)
        component_code = self._get_code(component_ai_message.content)

        if write_test:
            # Write a test for the component
            component_message_chain.append(AIMessage(content=component_code))
            component_message_chain.append(
                HumanMessage(content=component_prompt.UNIT_TEST_PROMPT)
            )

            test_ai_message = self.chat(component_message_chain)
            test_code = self._get_code(test_ai_message.content).removeprefix("python")
        else:
            test_code = ""

        accuracy_text = self._review_component(input_content, component_code)

        return component_code, test_code, accuracy_text

    def test_component(self, component_test: list) -> str:
        """
        Runs the test code to test the generated component.
        
        Returns stdout from the test run.
        """
        process = subprocess.Popen(["pytest", f"lib/component/{component_test}.py", "--disable-warnings"], stdout=subprocess.PIPE)
        full_output = process.stdout.read().decode("utf-8")
        summary = full_output.split("========================")[-2]
        return summary, full_output
    
    def display_component_code(self, selected_test_component: str):
        with open(f"./lib/component/{selected_test_component.removeprefix('test_')}.py", "r") as f:
            component = f.read()
        with open(f"./lib/component/{selected_test_component}.py", "r") as f:
            test_component = f.read()
        return component, test_component
    
    def auto_fix_component(self, selected_component, summary_output, full_output):
        # TODO
        return full_output, "Hello"


if __name__ == "__main__":
    import os

    log_dict = {
        "debug": logging.DEBUG,
        "info": logging.INFO,
        "warning": logging.WARNING,
        "error": logging.ERROR,
    }

    # Log Level default to INFO
    logging.basicConfig(
        level=log_dict.get(os.getenv("LOG_LEVEL", "INFO").lower(), "INFO")
    )
    model_name: str = os.getenv("MODEL_NAME")

    cgen = ComponentGen(
        system_prefix=prompt.COMPONENT_SYSTEM_FULL_CONTEXT,
        template_prompt=prompt.COMPONENT_TEMPLATE_PROMPT,
        model_name=model_name,
    )

    component, test_code, accuracy = cgen.generate_component(
        input_content="Write a component that takes a GCS path containing multiple images (either .png or .json) {image_path: string} from a GCS bucket and uses grabcut to segment the images into a foreground and background. The component should output the foreground and background images to the GCS bucket in folder path {output_gcs_folder: string}.",
    )

    print(f"Component Code:\n{component}")
    print(f"Test Code:\n{test_code}")
    print(f"Accuracy:\n{accuracy}")
