from pathlib import Path
import pandas as pd
import torch
from transformers import (
    AutoModelForSequenceClassification,
    AutoTokenizer,
    Trainer,
    TrainingArguments,
)


class TextDataset(torch.utils.data.Dataset):

  def __init__(self, encodings, labels):
    self.encodings = encodings
    self.labels = labels

  def __getitem__(self, idx):
    item = {key: val[idx].clone().detach() for key, val in self.encodings.items()}
    item["labels"] = torch.tensor(self.labels[idx])
    return item

  def __len__(self):
    return len(self.labels)


def train():
  base_dir = Path(__file__).resolve().parent
  dataset_path = base_dir / "dataset" / "trains.csv"
  output_model_dir = base_dir / "models" / "fine_tuned_model"

  df = pd.read_csv(dataset_path)
  texts = df["text"].tolist()
  labels = df["label"].tolist()

  model_name = "distilbert/distilbert-base-uncased"

  tokenizer = AutoTokenizer.from_pretrained(model_name)
  encodings = tokenizer(
      texts, truncation=True, padding=True, max_length=128, return_tensors="pt"
  )
  dataset = TextDataset(encodings, labels)

  model = AutoModelForSequenceClassification.from_pretrained(
      model_name, num_labels=4
  )

  training_args = TrainingArguments(
      output_dir=str(base_dir / "training_output"),
      num_train_epochs=3,
      per_device_train_batch_size=4,
      logging_steps=2,
      save_strategy="no",
      use_cpu=True,
  )

  trainer = Trainer(
      model=model,
      args=training_args,
      train_dataset=dataset,
  )

  print("Start training...")
  trainer.train()

  model.save_pretrained(output_model_dir)
  tokenizer.save_pretrained(output_model_dir)
  print(f"Model saved in: {output_model_dir}")


if __name__ == "__main__":
  train()