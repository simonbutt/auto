import gradio as gr
from pipelines.PipelineGen import PipelineGen
import pipelines.prompts as prompt



class AutoGradioInterface:

    def __init__(self, model_name: str="gpt-3.5-turbo"):
        self.pipegen = PipelineGen(
            system_prefix=prompt.COMPONNT_SYSTEM_PROMPT,
            template_prompt=prompt.COMPONENT_TEMPLATE_PROMPT,
            model_name=model_name
        )
        self._gradio_inputs = [
            gr.inputs.Textbox(lines=5, label="Pipeline Component Description", placeholder="Write a component that "),
            gr.Slider(1, 5, value=3, label="n_shot", step=1, info="Provides n shot predictions and a model review step to choose the most accurate prediction"),
        ]
        self._gradio_outputs = [
            gr.outputs.Textbox(label="Component Code"), 
            gr.outputs.Textbox(label="Accuracy Prediction")
        ]
        self._gradio_outputs[0].style(show_copy_button=True)
        self._gradio_examples = [
            ["Write a component that ingests a .csv file from GCS bucket path {GCS_BUCKET_PATH: string} as a Google Vertex Dataset", 2],
            ["Write a component that ingests all .parquet files in GCS bucket path {GCS_BUCKET_PATH: string} and uploads them into Google Cloud BigQuery, {DATASET: string}:{TABLE: string}.", 1],
            ["Write a component that takes a GCS path containing multiple images (either .png or .json) {image_path: string} from a GCS bucket and uses grabcut to segment the images into a foreground and background. The component should output the foreground and background images to the GCS bucket in folder path {output_gcs_folder: string}.", 3]
        ]
        
    def launch(self, is_public: bool=False):
        
        demo = gr.Interface(
            title="auto - Generate Vertex AI Pipeline Components with GPT-3.5",
            fn=self.pipegen.generate_component,
            inputs=self._gradio_inputs,
            outputs=self._gradio_outputs,
            examples=self._gradio_examples
        )
        demo.launch(share=is_public)

        

if __name__ == "__main__":
    
    import os
    import logging
    
    log_dict = {
        "debug": logging.DEBUG,
        "info": logging.INFO,
        "warning": logging.WARNING,
        "error": logging.ERROR
    }
    
    
    # Log Level default to INFO
    logging.basicConfig(level=log_dict.get(os.getenv("LOG_LEVEL", "INFO").lower(), "INFO"))
    
    model_name: str = os.getenv("MODEL_NAME")
    is_public: bool = os.getenv("IS_PUBLIC", "False").lower() == "true"
    
    interface = AutoGradioInterface()
    
    interface.launch(is_public)
    