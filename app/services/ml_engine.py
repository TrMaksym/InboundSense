from pathlib import Path
from typing import Tuple

import numpy as np
import onnxruntime
from transformers import AutoTokenizer


class MLEngine:
    def __init__(
            self,
            model_path: str = "ml_pipeline/models/classifier.onnx",
            tokenizer_path: str = "ml_pipeline/models/fine_tuned_model",
    ) -> None:
        self.model_path = Path(model_path)
        self.tokenizer_path = Path(tokenizer_path)
        self.session = None
        self.tokenizer = None
        self.labels_map = {
            0: "support",
            1: "sales",
            2: "tech",
            3: "general"
        }
        self._load()

    def _load(self):
        if self.model_path.exists() and self.tokenizer_path.exists():
            opts = onnxruntime.SessionOptions()
            opts.intra_op_num_threads = 2
            opts.execution_mode = onnxruntime.ExecutionMode.ORT_SEQUENTIAL
            opts.graph_optimization_level = onnxruntime.GraphOptimizationLevel.ORT_ENABLE_ALL

            self.session = onnxruntime.InferenceSession(
                str(self.model_path),
                sess_options=opts,
                providers=["CPUExecutionProvider"],
            )
            self.tokenizer = AutoTokenizer.from_pretrained(str(self.tokenizer_path))

    def classify(self, text: str) -> Tuple[str, float]:
        if not self.session or not self.tokenizer:
            return "general", 0.0

        inputs = self.tokenizer(
            text,
            truncation=True,
            padding=True,
            max_length=128,
            return_tensors="np",
        )

        ort_inputs = {
            "input_ids": inputs["input_ids"].astype(np.int64),
            "attention_mask": inputs["attention_mask"].astype(np.int64),
        }

        outputs = self.session.run(["logits"], ort_inputs)
        logits = outputs[0][0]

        exp_logits = np.exp(logits - np.max(logits))
        probabilities = exp_logits / exp_logits.sum()

        predicted_idx = int(np.argmax(probabilities))
        confidence = float(probabilities[predicted_idx])
        predicted_label = self.labels_map.get(predicted_idx, "general")

        return predicted_label, round(confidence, 4)

ml_engine = MLEngine()