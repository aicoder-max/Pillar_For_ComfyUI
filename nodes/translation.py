from .extension_node import ExtensionNode
from ..dto.translate_dto import TranslationRequest
from ..util.constants import DEFAULT_BASE_URL, EXEC_OPTIONS, MEMORY_MODE

DEFAULT_USER = "anonymous"
ERROR_INVALID_BASE_URL = "Error: Please provide a valid base_url for remote execution"

class Translation(ExtensionNode):

    from typing import Tuple, Dict, Any

    @classmethod
    def INPUT_TYPES(cls) -> Dict[str, Any]:
        return {
            "required": {
                "exec_opt": (EXEC_OPTIONS.labels(),),
                "base_url": ("STRING", {"default": DEFAULT_BASE_URL, "multiline": False, "placeholder": ""}),
                "text": ("STRING", {"multiline": True, "placeholder": "请输入要翻译的内容..."}),
            }
        }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("text",)
    FUNCTION = "translate_text"
    DESCRIPTION = "JoyCaption模型翻译"

    def _remote_translate(self, base_url: str, text: str) -> str:
        if not base_url or base_url == DEFAULT_BASE_URL:
            self._log.log_node_warn(self.get_node_name(),self.ERROR_INVALID_BASE_URL)
            return text

        from ..client.joy_caption_service_client import JoyCaptionServiceClient
        client = JoyCaptionServiceClient()
        request = TranslationRequest(
            text=text,
        )
        return client.translate(base_url, request)

    def _local_translate(self, text: str) -> str:
        check_path = self._download_model_from_hf(
            "fancyfeast/llama-joycaption-beta-one-hf-llava",
            "LLavacheckpoints", False, False
        )

        from ..service.joy_caption_service import JoyCaptionService

        # Use an instance variable to cache the service
        if not hasattr(self, "_joy_caption_service") or self._joy_caption_service is None:
            self._joy_caption_service = JoyCaptionService(str(check_path), "Maximum Savings (4-bit)")
        service = self._joy_caption_service

        return service.tranlation(text)

    def translate_text(self, **kwargs) -> Tuple[str]:
        exec_mode = EXEC_OPTIONS.get_by_label(kwargs["exec_opt"])
        text = kwargs["text"]

        try:
            if exec_mode == "remote":
                text_translated = self._remote_translate(kwargs["base_url"],text)
            else:
                text_translated = self._local_translate(text)
        except Exception as e:
            self._log.log_node_warn(self.get_node_name(),f"Translation error ({exec_mode}): {str(e)}")
            text_translated = text

        return (text_translated,)
