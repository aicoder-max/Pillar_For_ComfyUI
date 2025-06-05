import logging

from .util.log import log
from .util.pyproject import NAME
from .util.pyproject import VERSION

IS_COMFYUI_ENVIRONMENT = False
NODE_CLASS_MAPPINGS = dict()
NODE_DISPLAY_NAME_MAPPINGS = dict()
WEB_DIRECTORY = "./js"

try:
    import folder_paths
    IS_COMFYUI_ENVIRONMENT = True
    logger = logging.getLogger(NAME)
except ImportError:
    IS_COMFYUI_ENVIRONMENT = False

if IS_COMFYUI_ENVIRONMENT:
    try:
        from .nodes.text_mult_line import TextMultLine
        from .nodes.translation import Translation
        from .nodes.joy_caption import JoyCaption
        from .nodes.joy_caption import JoyCaptionCustom

        NODE_CLASS_MAPPINGS = {
            TextMultLine.get_node_name(): TextMultLine,
            Translation.get_node_name(): Translation,
            JoyCaption.get_node_name(): JoyCaption,
            JoyCaptionCustom.get_node_name(): JoyCaptionCustom,
        }

        NODE_DISPLAY_NAME_MAPPINGS = {
            TextMultLine.get_node_name(): TextMultLine.get_dispay_name(),
            Translation.get_node_name(): Translation.get_dispay_name(),
            JoyCaption.get_node_name(): JoyCaption.get_dispay_name(),
            JoyCaptionCustom.get_node_name(): JoyCaptionCustom.get_dispay_name(),
        }

        log(f"version:{VERSION} start successfully. load node count: {len(NODE_CLASS_MAPPINGS)}.🚀🚀🚀", "CYAN")
    except Exception as e:
        log(f"Error loading {NAME} : {e}", "RED")