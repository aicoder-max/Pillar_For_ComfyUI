import io
from typing import Any, Dict
from torchvision.utils import save_image
from PIL import Image
from .extension_node import ExtensionNode
from ..client.joy_caption_service_client import JoyCaptionServiceClient
from ..util.constants import CAPTION_LENGTH_CHOICES, CAPTION_TYPE, DEFAULT_BASE_URL, DEFAULT_MAX_NEW_TOKENS, \
    DEFAULT_SYSTEM_PROMPT, DEFAULT_TEMPERATURE, DEFAULT_TOP_K, DEFAULT_TOP_P, EXEC_OPTIONS, EXTRA_OPTIONS, \
    MEMORY_MODE, MIN_TEMPERATURE, MIN_TOKENS, MIN_TOP_K, MIN_TOP_P, \
    TEMPERATURE_STEP, TOP_P_STEP, MAX_TOKENS, MAX_TEMPERATURE, MAX_TOP_P, MAX_TOP_K

def build_prompt(caption_type: str, caption_length: str | int, extra_options: list[str], name_input: str) -> tuple[
    str, str]:
    caption_type_code = CAPTION_TYPE.get_by_label(caption_type)
    caption_length_code = CAPTION_LENGTH_CHOICES.get_by_label(caption_length)
    caption_templates = CAPTION_TYPE.get_by_code(caption_type_code)

    code = caption_length_code if caption_length_code else "any"

    if code == "any":
        map_idx = 0
    elif isinstance(code, str) and code.isdigit():
        map_idx = 1
    else:
        map_idx = 2

    prompt_code = caption_templates[map_idx]
    prompt_label = f"{caption_type}, {caption_length}"

    # 添加额外选项
    extra_options_codes = []
    extra_options_labels = []

    if extra_options:
        for opt in extra_options:
            if opt:
                code = EXTRA_OPTIONS.get_by_label(opt)
                if code:
                    extra_options_codes.append(code)
                    extra_options_labels.append(opt)

        if extra_options_codes:
            prompt_code += " " + " ".join(extra_options_codes)

            if extra_options_labels:
                prompt_label += "\n"
                for option in extra_options_labels:
                    prompt_label += f"- {option}\n"

    prompt_code = prompt_code.format(
        name=name_input or "{NAME}",
        length=caption_length,
        word_count=caption_length,
    )

    if name_input:
        prompt_label += f"- Name: {name_input}"

    return prompt_code, prompt_label


# Shared client instance
_joy_caption_client = None


def _validate_image_tensor(image_tensor):
    """
    Validate and prepare image tensor for processing.

    Args:
        image_tensor: Input image tensor to validate

    Returns:
        Validated tensor image

    Raises:
        ValueError: If the image tensor is invalid
    """
    if image_tensor is None or not hasattr(image_tensor, "shape"):
        raise ValueError("Invalid image tensor: missing shape attribute")

    if len(image_tensor.shape) != 4:
        raise ValueError(f"Expected 4D image tensor, got shape {image_tensor.shape}")

    if image_tensor.shape[0] == 0:
        raise ValueError("Empty image tensor")

    return image_tensor[0].permute(2, 0, 1)

def tensor_to_bytes(image_tensor) -> bytes:
    """
    Convert a PyTorch image tensor to JPEG bytes.

    Args:
        image_tensor: Input image tensor (batch_size, height, width, channels)

    Returns:
        Bytes of the converted image

    Raises:
        ValueError: If the image tensor is invalid
    """
    # Validate input
    tensor_image = _validate_image_tensor(image_tensor)
    buffer = io.BytesIO()

    save_image(tensor_image, buffer, "JPEG")
    buffer.seek(0)
    return buffer.getvalue()

def _get_joy_caption_client() -> JoyCaptionServiceClient:
    global _joy_caption_client
    if _joy_caption_client is None:
        _joy_caption_client = JoyCaptionServiceClient()
    return _joy_caption_client


from ..dto.joy_caption_dto import JoyCaptionRequest


def _process_remote_request(self,base_url: str, image: Any, system_prompt: str, prompt: str,
                            max_new_tokens: int, temperature: float, top_p: float,
                            top_k: int) -> Dict[str, str]:

    if not base_url or base_url == DEFAULT_BASE_URL:
        error_msg = "Error: Please provide a valid base_url for remote execution"
        return {
            "enCaption": error_msg,
            "cnCaption": error_msg
        }

    try:
        client = _get_joy_caption_client()
        request = JoyCaptionRequest.as_form(tensor_to_bytes(image),system_prompt,prompt,max_new_tokens,temperature,top_p,top_k)
        return client.generate_caption(base_url=base_url, request=request)
    except Exception as e:
        import traceback
        traceback.format_exc()
        self._log.log_node_warn(self.get_node_name(),f"Error in remote caption generation: {str(e)}")
        error_msg = f"Error generating caption: {str(e)}"
        return {
            "enCaption": error_msg,
            "cnCaption": error_msg
        }


from ..service.joy_caption_service import JoyCaptionService

def _process_local_request(self, image: Any, system_prompt: str, prompt: str, memory_mode: str,
                           max_new_tokens: int, temperature: float, top_p: float,
                           top_k: int):
    try:
        checkpoint_path = self._download_model_from_hf("fancyfeast/llama-joycaption-beta-one-hf-llava",
                                                       "LLavacheckpoints", False, False)
        memory_mode_code = MEMORY_MODE.get_by_label(memory_mode)
        service = JoyCaptionService(str(checkpoint_path), memory_mode_code)

        image = Image.open(io.BytesIO(tensor_to_bytes(image)))

        en_caption, cn_caption = service.generate(image, system_prompt, prompt, max_new_tokens, temperature, top_p,
                                                  top_k)
        return en_caption, cn_caption

    except Exception as e:
        self._log.log_node_warn(self.get_node_name(),f"Error in local caption generation: {str(e)}")
        error_msg = f"Error generating caption: {str(e)}"
        return error_msg, error_msg


class JoyCaption(ExtensionNode):
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "exec_opt": (EXEC_OPTIONS.labels(),),
                "base_url": ("STRING", {"multiline": False, "default": DEFAULT_BASE_URL}),
                "image": ("IMAGE",),
                "memory_mode": (MEMORY_MODE.labels(),),
                "caption_type": (CAPTION_TYPE.labels(),),
                "caption_length": (CAPTION_LENGTH_CHOICES.labels(),),
                "extra_option1": (EXTRA_OPTIONS.labels(),),
                "extra_option2": (EXTRA_OPTIONS.labels(),),
                "extra_option3": (EXTRA_OPTIONS.labels(),),
                "person_name": ("STRING", {"default": "", "multiline": False,
                                           "placeholder": "only needed if you use the 'If there is a person/character in the image you must refer to them as {name}.' extra option."}),
                "max_new_tokens": ("INT", {"default": DEFAULT_MAX_NEW_TOKENS, "min": MIN_TOKENS, "max": MAX_TOKENS}),
                "temperature": ("FLOAT",
                                {"default": DEFAULT_TEMPERATURE, "min": MIN_TEMPERATURE, "max": MAX_TEMPERATURE,
                                 "step": TEMPERATURE_STEP}),
                "top_p": ("FLOAT", {"default": DEFAULT_TOP_P, "min": MIN_TOP_P, "max": MAX_TOP_P, "step": TOP_P_STEP}),
                "top_k": ("INT", {"default": DEFAULT_TOP_K, "min": MIN_TOP_K, "max": MAX_TOP_K}),
            }
        }

    RETURN_TYPES = ("STRING", "STRING", "STRING")
    RETURN_NAMES = ("query", "en_caption", "cn_caption")
    DESCRIPTION = "JoyCaption生成图片描述"
    FUNCTION = "generate"

    def generate(self, exec_opt, base_url, image, memory_mode, caption_type, caption_length, extra_option1,
                 extra_option2, extra_option3, person_name, max_new_tokens, temperature, top_p, top_k):

        extras = [extra_option1, extra_option2, extra_option3]
        extras = [extra for extra in extras if extra]
        system_prompt = DEFAULT_SYSTEM_PROMPT

        exec_mode = EXEC_OPTIONS.get_by_label(exec_opt)

        prompt_code, prompt_label = build_prompt(caption_type, caption_length, extras, person_name)

        if exec_mode == "remote":
            caption_result = _process_remote_request(self,base_url, image, system_prompt, prompt_code, max_new_tokens,
                                                     temperature, top_p, top_k)

            en_caption = caption_result.get("enCaption", "")
            cn_caption = caption_result.get("cnCaption", "")

        else:
            en_caption, cn_caption = _process_local_request(self, image, system_prompt, prompt_code, memory_mode,
                                                            max_new_tokens, temperature, top_p, top_k)

        return prompt_label, en_caption, cn_caption


class JoyCaptionCustom(ExtensionNode):
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "exec_opt": (EXEC_OPTIONS.labels(),),
                "base_url": ("STRING", {"multiline": False, "default": DEFAULT_BASE_URL}),
                "image": ("IMAGE",),
                "memory_mode": (MEMORY_MODE.labels(),),
                "system_prompt": ("STRING", {"multiline": False,"default": DEFAULT_SYSTEM_PROMPT}),
                "user_query": ("STRING", {"multiline": True, "default": "Write a detailed description for this image."}),
                # generation params
                "max_new_tokens": ("INT", {"default": DEFAULT_MAX_NEW_TOKENS, "min": MIN_TOKENS, "max": MAX_TOKENS}),
                "temperature": ("FLOAT",
                                {"default": DEFAULT_TEMPERATURE, "min": MIN_TEMPERATURE, "max": MAX_TEMPERATURE,
                                 "step": TEMPERATURE_STEP}),
                "top_p": ("FLOAT", {"default": DEFAULT_TOP_P, "min": MIN_TOP_P, "max": MAX_TOP_P, "step": TOP_P_STEP}),
                "top_k": ("INT", {"default": DEFAULT_TOP_K, "min": MIN_TOP_K, "max": MAX_TOP_K}),
            },
        }

    RETURN_TYPES = ("STRING", "STRING", "STRING")
    RETURN_NAMES = ("query", "en_caption", "cn_caption")
    DESCRIPTION = "JoyCaption生成图片描述,自定义提示词."
    FUNCTION = "generate"

    def generate(self, exec_opt, base_url, image, memory_mode, system_prompt, user_query, max_new_tokens, temperature,
                 top_p, top_k):

        exec_mode = EXEC_OPTIONS.get_by_label(exec_opt)

        if exec_mode == "remote":

            caption_result = _process_remote_request(self,base_url, image, system_prompt, user_query, max_new_tokens,
                                                     temperature, top_p, top_k)

            en_caption = caption_result.get("enCaption", "")
            cn_caption = caption_result.get("cnCaption", "")

        else:
            en_caption, cn_caption = _process_local_request(self, image, system_prompt, user_query, memory_mode,
                                                            max_new_tokens, temperature, top_p, top_k)

        return user_query, en_caption, cn_caption