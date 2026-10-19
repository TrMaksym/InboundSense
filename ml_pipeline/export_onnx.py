from pathlib import Path
import torch
from transformers import AutoModelForSequenceClassification, AutoTokenizer

BASE_DIR = Path(__file__).resolve().parent
FINE_TUNED_DIR = BASE_DIR / "models" / "fine_tuned_model"
ONNX_OUTPUT_PATH = BASE_DIR / "models" / "classifier.onnx"


def export() -> None:
    print(f"Loading fine-tuned model from: {FINE_TUNED_DIR}...")
    tokenizer = AutoTokenizer.from_pretrained(FINE_TUNED_DIR)
    model = AutoModelForSequenceClassification.from_pretrained(FINE_TUNED_DIR)
    model.eval()

    dummy_text = "Testing classification pipeline export."
    inputs = tokenizer(
        dummy_text,
        return_tensors="pt",
        padding=True,
        truncation=True,
        max_length=128,
    )

    print(f"Exporting ONNX computational graph to: {ONNX_OUTPUT_PATH}...")
    torch.onnx.export(
        model,
        (inputs["input_ids"], inputs["attention_mask"]),
        f=str(ONNX_OUTPUT_PATH),
        input_names=["input_ids", "attention_mask"],
        output_names=["logits"],
        dynamic_axes={
            "input_ids": {0: "batch_size", 1: "sequence_length"},
            "attention_mask": {0: "batch_size", 1: "sequence_length"},
            "logits": {0: "batch_size"},
        },
        opset_version=17,
        dynamo=False,
    )
    print("Model successfully exported to ONNX format.")


if __name__ == "__main__":
    export()