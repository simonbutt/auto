from pipelines.ComponentGen import ComponentGen
import prompts.component as component_prompt
import gradio as gr


class AutoGradioInterface:

    """
    AutoGradioInterface provides a simple interface for users to generate components using the Auto Gradio API.
    """

    def __init__(self, model_name: str = "gpt-3.5-turbo"):
        self.compgen = ComponentGen(
            model_name=model_name,
        )

        self._gradio_examples = [
            [
                "Write a component that ingests a .csv file from GCS bucket path {GCS_BUCKET_PATH: string} as a Google Vertex Dataset"
            ],
            [
                "Write a component that ingests all .parquet files in GCS bucket path {GCS_BUCKET_PATH: string} and uploads them into Google Cloud BigQuery, {DATASET: string}:{TABLE: string}."
            ],
            [
                "Write a component that takes a GCS path containing multiple images (either .png or .json) {image_path: string} from a GCS bucket and uses grabcut to segment the images into a foreground and background. The component should output the foreground and background images to the GCS bucket in folder path {output_gcs_folder: string}."
            ],
        ]

    def launch(self, is_public: bool = False):
        demo = gr.Interface(
            title="auto - Generate Vertex AI Pipeline Components with GPT-3.5",
            fn=self.compgen.generate_component,
            inputs=gr.Textbox(
                lines=5,
                label="Pipeline Component Description",
                placeholder="Write a component that ",
            ),
            outputs=[
                gr.Code(label="Component Code", language="python", interactive=True),
                gr.Textbox(label="Test Code", visible=False),
                gr.Textbox(label="Accuracy Prediction"),
            ],
            examples=self._gradio_examples,
        )
        demo.launch(share=is_public)


if __name__ == "__main__":
    import os
    import logging

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
    is_public: bool = os.getenv("IS_PUBLIC", "False").lower() == "true"

    interface = AutoGradioInterface()

    interface.launch(is_public)
