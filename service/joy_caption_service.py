# Configure logging
import re
import threading

import torch
from PIL import Image
from transformers import AutoProcessor, LlavaForConditionalGeneration, BitsAndBytesConfig
from langdetect import detect
from .base_service import BaseService
from ..util.constants import DEFAULT_SYSTEM_PROMPT, DEFAULT_TEMPERATURE, DEFAULT_TOP_K, DEFAULT_TOP_P, MAX_TOKENS, MEMORY_MODE

BILINGUAL_SUFFIX = "Please reply in both Chinese and English according to this format **English:**English Description**Chinese:**Chinese Description"


class JoyCaptionService(BaseService):
    """
    A singleton service for generating captions for images using the Llava model.
    """
    _lock = threading.Lock()  # Class-level lock for thread safety

    @classmethod
    def get_model_name(cls):
        return "llama-joycaption-beta-one-hf-llava"

    def __init__(self, model_path: str, memory_mode: str):
        # Prevent re-initialization
        if not hasattr(self, '_initialized'):
            # Initialize the base class
            super().__init__(model_path)

            try:
                # Check if GPU is available
                self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
                self.logger.info(f"Using device: {self.device}")

                self.processor = AutoProcessor.from_pretrained(model_path)

                if memory_mode == "Default":
                    self.model = LlavaForConditionalGeneration.from_pretrained(model_path,
                                                                               torch_dtype="bfloat16",
                                                                               device_map="auto")
                else:
                    # Configure quantization based on memory mode
                    quantization_config_params = MEMORY_MODE.get_by_code(memory_mode)
                    quantization_config = BitsAndBytesConfig(
                        **quantization_config_params,
                        llm_int8_skip_modules=["vision_tower", "multi_modal_projector"],
                        # Transformer's Siglip implementation has bugs when quantized, so skip those.
                    )
                    self.model = LlavaForConditionalGeneration.from_pretrained(str(model_path), torch_dtype="auto",
                                                                               device_map="auto",
                                                                               quantization_config=quantization_config)

                self.logger.info(f"Loaded model {model_path} with memory mode {memory_mode}")

                self.model.eval()
                self._initialized = True

                self.logger.info(f"Model loaded with 4-bit quantization and ready for inference")
            except Exception as e:
                self.logger.error(f"Error loading model: {str(e)}")
                raise

    def cleanup(self):
        # Only clean up if initialized
        if hasattr(self, '_initialized') and self._initialized:
            self.logger.info("Starting cleanup of JoyCaptionService resources...")
            # Clean up processor
            if hasattr(self, 'processor') and self.processor is not None:
                self.logger.debug("Cleaning up processor...")
                del self.processor
                self.processor = None
                self.logger.debug("Cleaning up model and memory...")
                self._free_memory()
                # Mark as uninitialized
                self._initialized = False
                self.logger.info("Cleaned up model resources for JoyCaptionService")

    @staticmethod
    def extract_section(caption: str, markers: list, other_markers: list):
        for marker in markers:
            if marker in caption:
                parts = caption.split(marker, 1)
                if len(parts) > 1:
                    text = parts[1].strip()
                    for other_marker in other_markers:
                        if other_marker in text:
                            text = text.split(other_marker, 1)[0].strip()
                    return text
        return ""

    @staticmethod
    def parse_bilingual_caption(caption: str):
        caption = caption.strip()
        en_markers = ["**English Description:**", "**英文描述:**", "**English:**", "English Description:"]
        cn_markers = ["**Chinese Description:**", "**中文描述:**", "**Chinese:**", "Chinese Description:"]

        en_caption = JoyCaptionService.extract_section(caption, en_markers, cn_markers)
        cn_caption = JoyCaptionService.extract_section(caption, cn_markers, en_markers)

        if not en_caption and not cn_caption:
            lines = caption.split('\n')
            english_lines = []
            chinese_lines = []
            chinese_char_pattern = re.compile(r'[\u4e00-\u9fff]')
            current_section = "unknown"

            for line in lines:
                line = line.strip()
                if not line:
                    continue
                if chinese_char_pattern.search(line):
                    if current_section != "chinese":
                        current_section = "chinese"
                    chinese_lines.append(line)
                else:
                    if current_section != "english":
                        current_section = "english"
                    english_lines.append(line)

            en_caption = " ".join(english_lines).strip() if english_lines else ""
            cn_caption = " ".join(chinese_lines).strip() if chinese_lines else ""

        return (en_caption, cn_caption) if en_caption or cn_caption else (caption, caption)

    @torch.inference_mode()
    def generate(self, image: Image.Image, system: str, prompt: str, max_new_tokens: int, temperature: float,
                 top_p: float, top_k: int):
        # Limit max_new_tokens not to exceed MAX_TOKENS
        max_new_tokens = min(max_new_tokens, MAX_TOKENS)

        prompt = f"{prompt.strip()} {BILINGUAL_SUFFIX}"

        convo = [
            {"role": "system", "content": system.strip()},
            {"role": "user", "content": prompt}
        ]
        # Acquire lock to ensure thread safety
        with self._lock:
            convo_string = self.processor.apply_chat_template(convo, tokenize=False, add_generation_prompt=True)

            # Use self.device to maintain device consistency
            inputs = self.processor(text=[convo_string], images=[image], return_tensors="pt").to(self.device)

            # Use bfloat16 for pixel_values to save memory
            if torch.cuda.is_available():
                inputs['pixel_values'] = inputs['pixel_values'].to(torch.bfloat16)

            generate_ids = self.model.generate(
                **inputs,
                max_new_tokens=max_new_tokens,
                do_sample=True if temperature > 0 else False,
                suppress_tokens=None,
                use_cache=True,
                temperature=temperature,
                top_k=None if top_k == 0 else top_k,
                top_p=top_p,
            )[0]

            generate_ids = generate_ids[inputs['input_ids'].shape[1]:]
            caption = self.processor.tokenizer.decode(generate_ids, skip_special_tokens=True,
                                                      clean_up_tokenization_spaces=False).strip()

            en_caption, cn_caption = JoyCaptionService.parse_bilingual_caption(caption)
            return en_caption, cn_caption

    @torch.inference_mode()
    def tranlation(self, prompt: str):

        lang = detect(prompt)

        if lang == "zh-cn":
            lang = "English"
        else:
            lang = "Chinese"

        prompt = f"translate this passage into{lang}: {prompt.strip()} "

        convo = [
            {"role": "system", "content": "You are a translation expert".strip()},
            {"role": "user", "content": prompt}
        ]

        # Acquire lock to ensure thread safety
        with self._lock:
            convo_string = self.processor.apply_chat_template(convo, tokenize=False, add_generation_prompt=True)

            # Use self.device to maintain device consistency
            inputs = self.processor(text=[convo_string], return_tensors="pt").to(self.device)

            generate_ids = self.model.generate(
                **inputs,
                max_new_tokens=MAX_TOKENS,
                do_sample=True,
                suppress_tokens=None,
                use_cache=True,
                temperature=DEFAULT_TEMPERATURE,
                top_k=DEFAULT_TOP_K,
                top_p=DEFAULT_TOP_P,
            )[0]

            generate_ids = generate_ids[inputs['input_ids'].shape[1]:]
            content = self.processor.tokenizer.decode(generate_ids, skip_special_tokens=True,
                                                      clean_up_tokenization_spaces=False).strip()
            return content