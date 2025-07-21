import argparse
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

sys_prompt = """
Transform the short prompt into a detailed video-generation caption using this structure:
​​Opening shot type​​ (long/medium/close-up/extreme close-up/full shot)
​​Primary subject(s)​​ with vivid attributes (colors, textures, actions, interactions)
​​Dynamic elements​​ (movement, transitions, or changes over time, e.g., 'gradually lowers,' 'begins to climb,' 'camera moves toward...')
​​Scene composition​​ (background, environment, spatial relationships)
​​Lighting/atmosphere​​ (natural/artificial, time of day, mood)
​​Camera motion​​ (zooms, pans, static/handheld shots) if applicable.

Pattern Summary from Examples:
[Shot Type] of [Subject+Action] + [Detailed Subject Description] + [Environmental Context] + [Lighting Conditions] + [Camera Movement]

​One case:
Short prompt: a person is playing football
Long prompt: Medium shot of a young athlete in a red jersey sprinting across a muddy field, dribbling a soccer ball with precise footwork. The player glances toward the goalpost, adjusts their stance, and kicks the ball forcefully into the net. Raindrops fall lightly, creating reflections under stadium floodlights. The camera follows the ball’s trajectory in a smooth pan.

Note: If the subject is stationary, incorporate camera movement to ensure the generated video remains dynamic.

​​Now expand this short prompt:​​ [{}]. Please only output the final long prompt in English.
"""

ENHANCER_MODEL_CONFIG = {
    "small": "Qwen/Qwen2.5-7B-Instruct",
    "large": "Qwen/Qwen2.5-32B-Instruct",
}


class PromptEnhancer:
    def __init__(self, model_size="small", device="cuda" if torch.cuda.is_available() else "cpu"):
        model_name = ENHANCER_MODEL_CONFIG[model_size]
        self.device = device
        try:
            self.model = AutoModelForCausalLM.from_pretrained(
                model_name,
                torch_dtype="auto",
                device_map=self.device,
            )
            self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        except Exception as e:
            raise RuntimeError(f"Failed to load model {model_name}: {e}")

    def __call__(self, prompt):
        prompt = prompt.strip()
        prompt = sys_prompt.format(prompt)
        messages = [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt},
        ]
        text = self.tokenizer.apply_chat_template(
            messages, tokenize=False, add_generation_prompt=True
        )
        model_inputs = self.tokenizer([text], return_tensors="pt").to(self.model.device)
        try:
            generated_ids = self.model.generate(
                **model_inputs,
                max_new_tokens=2048,
            )
            generated_ids = [
                output_ids[len(input_ids) :]
                for input_ids, output_ids in zip(
                    model_inputs.input_ids, generated_ids
                )
            ]
            rewritten_prompt = self.tokenizer.batch_decode(
                generated_ids, skip_special_tokens=True
            )[0]
            return rewritten_prompt
        except Exception as e:
            return f"Error during prompt enhancement: {e}"


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--prompt", type=str, default="In a still frame, a stop sign")
    parser.add_argument("--model_size", type=str, default="small", choices=["small", "large"])
    parser.add_argument("--max_length", type=int, default=None)
    args = parser.parse_args()

    try:
        prompt_enhancer = PromptEnhancer(model_size=args.model_size)
        enhanced_prompt = prompt_enhancer(args.prompt)
        if args.max_length and len(enhanced_prompt) > args.max_length:
            enhanced_prompt = enhanced_prompt[: args.max_length]
        print(f"Original prompt: {args.prompt}")
        print(f"Enhanced prompt: {enhanced_prompt}")
    except RuntimeError as e:
        print(e)
