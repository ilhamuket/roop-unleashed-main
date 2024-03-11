from typing import Any, List, Callable
import roop.globals
import insightface
import cv2
import numpy as np

from roop.typing import Face, Frame
from roop.utilities import resolve_relative_path



class FaceSwapInsightFace():
    model_swap_insightface = None


    processorname = 'faceswap'
    type = 'swap'


    def Initialize(self, devicename):
        if self.model_swap_insightface is None:
            model_path = resolve_relative_path('../models/inswapper_128.onnx')
            self.model_swap_insightface = insightface.model_zoo.get_model(model_path, providers=roop.globals.execution_providers)

    
    def Run(self, source_face: Face, target_face: Face, temp_frame: Frame) -> Frame:
        img_fake, M = self.model_swap_insightface.get(temp_frame, target_face, source_face, paste_back=False)
        target_face.matrix = M
        return img_fake 


    def Release(self):
        del self.model_swap_insightface
        self.model_swap_insightface = None


                



