from kfp.components import InputPath, create_component_from_func, OutputPath
from kfp.v2.dsl import component, Dataset


@component(
    base_image="python:3.8",
    packages_to_install=["great-expectations==0.13.11"],
    output_component_file=str(Path(__file__).with_suffix(".yaml")),
)
def validate_csv_using_greatexpectations(
    csv_path: Input[Dataset],
    expectation_suite_path: str,
    data_doc_path: str,
):
    """Validate a CSV dataset against a Great Expectations suite and create Data Doc (a validation report).
    This component fails if validation is not successful.

    Args:
        csv_path: Path to the CSV file with the dataset.
        expectation_suite_path: Path to Great Expectations expectation suite (in JSON format).
    """
    import json
    import os
    import sys

    import great_expectations as ge
    from great_expectations.render import DefaultJinjaPageView
    from great_expectations.render.renderer import ValidationResultsPageRenderer
    import logging

    with open(expectation_suite_path, "r") as json_file:
        expectation_suite = json.load(json_file)
    df = ge.read_csv(csv_path, expectation_suite=expectation_suite)
    result = df.validate()

    document_model = ValidationResultsPageRenderer().render(result)
    os.makedirs(os.path.dirname(data_doc_path), exist_ok=True)
    with open(data_doc_path, "w") as writer:
        writer.write(DefaultJinjaPageView().render(document_model))

    logging.info(f"Saved: {data_doc_path}")

    if not result.success:
        sys.exit(1)
