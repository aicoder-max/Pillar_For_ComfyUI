import threading
from abc import abstractmethod
import gc
import torch
from ..pillar_plus import IS_COMFYUI_ENVIRONMENT
if not IS_COMFYUI_ENVIRONMENT:
    from server import logger
else:
    import logging
    logger = logging.getLogger(__name__)

class SingletonMeta(type):
    _instances = {}
    _lock = threading.Lock()

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            with cls._lock:
                if cls not in cls._instances:
                    cls._instances[cls] = super().__call__(*args, **kwargs)
        return cls._instances[cls]

class BaseService(metaclass=SingletonMeta):

    def __init__(self, model_path):
        self.logger = logger
        self.model_path = model_path
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.model = None

    @classmethod
    def get_name(cls) -> str:
        return cls.__name__

    @classmethod
    @abstractmethod
    def get_model_name(cls):
        pass

    @abstractmethod
    def cleanup(self):
        pass

    def _free_memory(self):
        if hasattr(self, 'model') and self.model is not None:
            # Move model to CPU first if it was on GPU
            if self.device != "cpu":
                self.model.to("cpu")

            # Delete model and explicitly call garbage collector
            del self.model
            self.model = None

        # Force CUDA memory cleanup if available
        if torch.cuda.is_available():
            torch.cuda.empty_cache()

        # Run garbage collector
        gc.collect()
