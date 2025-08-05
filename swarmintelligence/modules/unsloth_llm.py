import os
from unsloth import FastLanguageModel
import re

class OpenSourceLLM:
    def __init__(self):
        pass

    def initialize(self, model_name="unsloth/Qwen3-14B"):
        self.token = os.environ['HF_TOKEN']
        self.model, self.tokenizer = FastLanguageModel.from_pretrained(model_name=model_name, max_seq_length=2048, load_in_4bit=True, load_in_8bit=False, full_finetuning=False, token=self.token, )

    def train(self, dataset_name="unsloth/OpenMathReasoning-mini", saved_model_name="aprendesc/test_qwen_lora"):
        from unsloth.chat_templates import standardize_sharegpt
        from datasets import load_dataset
        import pandas as pd
        from datasets import Dataset
        from trl import SFTTrainer, SFTConfig

        self.model = FastLanguageModel.get_peft_model(self.model, r=32,
                                                      target_modules=["q_proj", "k_proj", "v_proj", "o_proj", "gate_proj", "up_proj", "down_proj", ],
                                                      lora_alpha=32,
                                                      lora_dropout=0,
                                                      bias="none",
                                                      use_gradient_checkpointing="unsloth",
                                                      random_state=3407,
                                                      use_rslora=False,
                                                      loftq_config=None,
                                                      )

        reasoning_dataset = load_dataset(dataset_name, split="cot")
        non_reasoning_dataset = load_dataset("mlabonne/FineTome-100k", split="train")

        def generate_conversation(examples):
            problems = examples["problem"]
            solutions = examples["generated_solution"]
            conversations = []
            for problem, solution in zip(problems, solutions):
                conversations.append([{"role": "user", "content": problem}, {"role": "assistant", "content": solution}, ])
            return {"conversations": conversations, }

        reasoning_conversations = self.tokenizer.apply_chat_template(reasoning_dataset.map(generate_conversation, batched=True)["conversations"], tokenize=False, )
        dataset = standardize_sharegpt(non_reasoning_dataset)
        non_reasoning_conversations = self.tokenizer.apply_chat_template(dataset["conversations"], tokenize=False, )
        chat_percentage = 0.25
        non_reasoning_subset = pd.Series(non_reasoning_conversations)
        non_reasoning_subset = non_reasoning_subset.sample(int(len(reasoning_conversations) * (chat_percentage / (1 - chat_percentage))), random_state=2407, )
        data = pd.concat([pd.Series(reasoning_conversations), pd.Series(non_reasoning_subset)])
        data.name = "text"
        combined_dataset = Dataset.from_pandas(pd.DataFrame(data))
        combined_dataset = combined_dataset.shuffle(seed=3407)

        trainer = SFTTrainer(
            model=self.model,
            tokenizer=self.tokenizer,
            train_dataset=combined_dataset,
            eval_dataset=None,  # Can set up evaluation!
            args=SFTConfig(
                dataset_text_field="text",
                per_device_train_batch_size=2,
                gradient_accumulation_steps=4,
                warmup_steps=5,
                max_steps=30,
                learning_rate=2e-4,
                logging_steps=1,
                optim="adamw_8bit",
                weight_decay=0.01,
                lr_scheduler_type="linear",
                seed=3407,
                report_to="none",
            ),
        )
        trainer_stats = trainer.train()
        print(trainer_stats)
        self.model.push_to_hub(saved_model_name, token=self.token)
        self.tokenizer.push_to_hub(saved_model_name, token=self.token)

    def predict(self, history, temperature=1, max_new_tokens=2048, ):
        text = self.tokenizer.apply_chat_template(history, tokenize=False, add_generation_prompt=True, enable_thinking=True, )
        inputs = self.tokenizer(text, return_tensors="pt").to("cuda")
        output_ids = self.model.generate(input_ids=inputs['input_ids'], attention_mask=inputs['attention_mask'], max_new_tokens=max_new_tokens, temperature=temperature, top_p=0.8, top_k=20)
        answer = self.tokenizer.decode(output_ids[0], skip_special_tokens=False)
        thoughts = re.findall(r'<think>(.*?)</think>', answer, re.DOTALL)[-1]
        answer = answer.split('</think>')[-1]
        return thoughts, answer