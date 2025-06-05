import re
import folder_paths
from comfy.comfy_types import ComfyNodeABC
from pathlib import Path
from typing import Dict, Any, Tuple, ClassVar
from ..util.pyproject import CATEGORY_NAME
from ..util import log

class ExtensionNode(ComfyNodeABC):
    RETURN_TYPES: ClassVar[Tuple[str, ...]] = ()
    RETURN_NAMES: ClassVar[Tuple[str, ...]] = ()
    FUNCTION: ClassVar[str] = ""
    CATEGORY: ClassVar[str] = CATEGORY_NAME
    OUTPUT_NODE = True
    DESCRIPTION: ClassVar[str] = ""
    _log = None

    @classmethod
    def INPUT_TYPES(cls) -> Dict[str, Any]:
        return {"required": {}, "optional": {}}

    def __init__(self):
        self._log = log

    @classmethod
    def get_node_name(cls) -> str:
        return f"{cls.CATEGORY}_{cls.__name__}"

    @classmethod
    def get_dispay_name(cls) -> str:
        return f"Pillar{cls.__name__}"

    def _download_model_from_hf(self, repo_id: str, folder_name: str, force_download: bool = False,
                                local_files_only: bool = False) -> Path:
        try:
            model_save_path = Path(folder_paths.models_dir) / folder_name / Path(repo_id).stem
            if not model_save_path.exists() or force_download:
                try:
                    from huggingface_hub import snapshot_download
                    log.log_node_info(self.get_node_name(), f"Downloading model from {repo_id} to {model_save_path}...")
                    snapshot_download(
                        repo_id=repo_id,
                        local_dir=str(model_save_path),
                        force_download=force_download,
                        local_files_only=local_files_only
                    )
                    self._log.log_node_info(self.get_node_name(),
                                            f"Model successfully downloaded to {model_save_path}.")
                except FileNotFoundError:
                    error_msg = f"File not found during download of {repo_id}."
                    self._log.log_node_warn(self.get_node_name(), error_msg)
                    raise RuntimeError(error_msg)
                except PermissionError:
                    error_msg = f"Permission denied when trying to download {repo_id} to {model_save_path}."
                    self._log.log_node_warn(self.get_node_name(), error_msg)
                    raise RuntimeError(error_msg)
                except Exception as e:
                    error_msg = f"Unexpected error downloading model {repo_id}: {str(e)}"
                    self._log.log_node_warn(self.get_node_name(), error_msg)
                    raise RuntimeError(error_msg)

            return model_save_path
        except Exception as e:
            self._log.log_node_warn(self.get_node_name(), f"Unexpected error processing model {repo_id}: {str(e)}")
            raise RuntimeError(f"Failed to process model {repo_id}: {str(e)}")
