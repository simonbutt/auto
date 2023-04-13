import gradio as gr
from pipelines.PipelineGen import PipelineGen
import pipelines.prompts as prompt



class AutoGradioBlocks:

    def __init__(self, model_name: str="gpt-3.5-turbo"):
        self.pipegen = PipelineGen(
            system_prefix=prompt.COMPONNT_SYSTEM_PROMPT,
            template_prompt=prompt.COMPONENT_TEMPLATE_PROMPT,
            model_name=model_name
        )
        self._gradio_examples = [
            ["Write a component that ingests a .csv file from GCS bucket path {GCS_BUCKET_PATH: string} as a Google Vertex Dataset", 2],
            ["Write a component that ingests all .parquet files in GCS bucket path {GCS_BUCKET_PATH: string} and uploads them into Google Cloud BigQuery, {DATASET: string}:{TABLE: string}.", 1],
            ["Write a component that takes a GCS path containing multiple images (either .png or .json) {image_path: string} from a GCS bucket and uses grabcut to segment the images into a foreground and background. The component should output the foreground and background images to the GCS bucket in folder path {output_gcs_folder: string}.", 3]
        ]

    def launch(self, is_public: bool=False):
        
        demo = gr.Blocks()

        with demo:

            with gr.Row():
                gr.Markdown("""
                   # **auto** - Generate Vertex AI Pipeline Components with GPT-3.5
                   Create custom KFP components in minutes! (and soon test and deploy straight onto Vertex AI)
                """)

            with gr.TabItem("ComponentGen"):
                with gr.Row():
                    with gr.Column(scale=1, min_width=600):
                        user_input = gr.Textbox(lines=5, label="Pipeline Component Description", placeholder="Write a component that ")

                        nshot_input = gr.Slider(1, 5, value=3, label="n_shot", step=1, interactive=True, info="Provides n shot predictions and a model review step to choose the most accurate prediction")

                        #TODO: examples = gr.Examples(examples=self._gradio_examples, inputs=[compgen_input, nshot_input], fn=self.pipegen.generate_component, postprocess=False, label="Examples")
                        compgen_button = gr.Button(value="Generate Component", variant="primary")
                    
                        upload_button = gr.Button("Upload Component")
                    with gr.Column(scale=1, min_width=600):

                        compgen_output = gr.Code(language="python", label="Component Code", interactive=True)
                        compgen_accuracy = gr.Textbox(lines=2, label="Component Accuracy", interactive=False)
                        
                    upload_button.click(fn=self.pipegen.write_to_file, inputs=[compgen_output, ], outputs=[])
                    compgen_button.click(
                        fn=self.pipegen.generate_component, inputs=[user_input, nshot_input], outputs=[compgen_output, compgen_accuracy], api_name="generate_component"
                    )
            with gr.TabItem("Review Prompt"):
                review_info = "Review the following kfp component code snippets and return a snippet_name, accuracy_score and accuracy_summary for each component."
                review_prompt = gr.Textbox(lines=12, label="Component Review Prompt Instructions", info=review_info, placeholder=prompt.REVIEW_NSHOT_PROMPT, interactive=True)
                update_prompt_button = gr.Button("Update", variant="primary")
                update_prompt_button.click(fn=PipelineGen.update_review_prompt, inputs=review_prompt, outputs=[])

            with gr.TabItem("PipelineGen"):
                with gr.Row():
                    with gr.Column():
                        gr.Markdown("### Available Components")

                        get_components = lambda : [val.replace(".py", "") for val in os.listdir("lib/component/") if ".py" in val]
                        selected_components = gr.CheckboxGroup(
                            get_components(),
                            label="Components", 
                            info="The following components are available:",
                            interactive=True
                        )

                        with gr.Row():
                            
                            with gr.Column():
                                pipegen_button = gr.Button("Generate Pipeline", variant="primary")
                            with gr.Column():    
                                upload_pipeline_button = gr.Button("Upload Pipeline")
                            refresh_components = gr.Button("Refresh Components")
                            refresh_components.click(fn=get_components, inputs=[], outputs=[selected_components])
                    with gr.Column():
                        pipegen_output = gr.Code(language="python", label="Pipeline Code", interactive=True)
                    
                    file_type = gr.Text(value="pipelines", visible=False, interactive=False)
                    upload_pipeline_button.click(fn=self.pipegen.write_to_file, inputs=[pipegen_output, file_type], outputs=[])
                    pipegen_button.click(fn=self.pipegen.generate_pipeline, inputs=[selected_components], outputs=[pipegen_output])
                    

            with gr.TabItem("Deploy"):

                gr.Markdown("### Available Pipelines")
                available_pipelines = [val.replace(".py", "") for val in os.listdir("lib/pipelines/") if ".py" in val]

                selected_pipeline = gr.Radio(available_pipelines, label="Choose the pipeline to deploy")

                deploy_pipeline_button = gr.Button("Deploy")
                # deploy_pipeline_button.click(fn=PipelineGen., inputs=review_info, outputs=[])

    
    
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
    
    interface = AutoGradioBlocks()
    
    interface.launch(is_public)
    