from transformers import AutoModelForCausalLM, AutoTokenizer


class HFModelClass:
    def __init__(self):
        pass

    def initialize(self, model):
        import huggingface_hub
        huggingface_hub.login(token='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')
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModelForCausalLM.from_pretrained(model_name, ).to("cuda")

    def predict(self, history):
        text = tokenizer.apply_chat_template(history, tokenize=False, add_generation_prompt=True, )
        model_inputs = tokenizer([text], return_tensors="pt").to("cuda")
        generated_ids = model.generate(**model_inputs, max_new_tokens=32768)
        output_ids = generated_ids[0][len(model_inputs.input_ids[0]):]
        tokenizer.decode(output_ids, skip_special_tokens=True)
        thoughts = re.findall(r'<think>(.*?)</think>', full_answer, re.DOTALL)[-1]
        answer = full_answer.split('</think>')[-1]
        return thoughts, answer