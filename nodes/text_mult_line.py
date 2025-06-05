from .extension_node import ExtensionNode

class TextMultLine(ExtensionNode):
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "text": ("STRING", {"placeholder": "请输入文本...","multiline": False})
            },
            "hidden": {"prompt": "PROMPT", "extra_pnginfo": "EXTRA_PNGINFO", "unique_id": "UNIQUE_ID"},
        }

    OUTPUT_NODE = True
    RETURN_TYPES = ("STRING", "STRING")
    RETURN_NAMES = ("text", "unique_id")
    DESCRIPTION = "多行文本预览"
    FUNCTION = "doit"

    @staticmethod
    def doit(text, prompt=None, extra_pnginfo=None, unique_id=None):
        return {"ui": {"string": [text, unique_id, ]}, "result": (text, unique_id,)}