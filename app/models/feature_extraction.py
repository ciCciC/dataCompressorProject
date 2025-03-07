"""
@misc{darcet2024visiontransformersneedregisters,
      title={Vision Transformers Need Registers},
      author={Timothée Darcet and Maxime Oquab and Julien Mairal and Piotr Bojanowski},
      year={2024},
      eprint={2309.16588},
      archivePrefix={arXiv},
      primaryClass={cs.CV},
      url={https://arxiv.org/abs/2309.16588},
}
"""


from transformers import AutoImageProcessor, AutoModel
import torch
from PIL import Image
from typing import List
from app.models.base_model import BaseModel


class FacebookDinoV2(BaseModel):

    def __init__(self):
        super().__init__()
        self._processor = None

        # NOTE: facebook/dinov2-with-registers-large model does not support MPS
        self.device = 'cuda' if torch.cuda.is_available() else 'cpu'
        self.model_id = 'facebook/dinov2-with-registers-large'

    def load_model(self):
        self._processor = AutoImageProcessor.from_pretrained(self.model_id)
        self._model = AutoModel.from_pretrained(self.model_id, use_safetensors=True).to(self.device)

    @torch.inference_mode()
    def get_embeddings(self, images: List[Image.Image]) -> torch.Tensor:
        inputs = self._processor(images=images, return_tensors="pt").to(self.device)
        embeddings = self._model(**inputs).last_hidden_state.mean(dim=1)
        return embeddings

    def compute_similarity(self, embeddings: torch.Tensor) -> float:
        cosine = torch.nn.CosineSimilarity(dim=0)
        score = cosine(*embeddings).numpy().tolist()
        return score
