from transformers import CLIPProcessor, CLIPModel, AutoProcessor, AutoImageProcessor
from torchvision import datasets, transforms
import torch
from utils import get_scam_donation_dataloader, set_seed
from pathlib import Path
from torch.utils.data import DataLoader
import matplotlib.pyplot as plt
from torchvision.transforms import InterpolationMode
from tqdm import tqdm
import numpy as np
import os


def show(inp):
    fig = plt.gcf()
    plt.imshow(inp.permute(1, 2, 0).cpu())
    fig.show()

TEST_MODE = False

FULL_DIR = Path("/data/datasets/scam_donation_2024/scammers_images/")
SAMPLE_DIR = Path("/data/datasets/scam_donation_2024/samples/")
DATA_DIR = FULL_DIR if not TEST_MODE else SAMPLE_DIR
platform = 'all'

OUT_DIR = Path("embeddings")/ f"{platform}"
os.makedirs(f"embeddings/{platform}", exist_ok=True)

EMBEDDING_SIZE = 768 # 512  # embedding size for clip models
# MODEL_ID = "openai/clip-vit-base-patch32"
model_id = 'openai/clip-vit-large-patch14'
model_name = model_id.split('/')[-1]

SEED = 444

processing = transforms.Compose([
    transforms.Resize(256, interpolation=InterpolationMode.BICUBIC),
    transforms.CenterCrop(224),
    transforms.ToTensor(),
])

if __name__ == "__main__":

    set_seed(seed=SEED)

    dataloader = get_scam_donation_dataloader(platform=platform, data_dir=DATA_DIR, transform=processing, seed=SEED)

    # load CLIP model
    processor = CLIPProcessor.from_pretrained(model_id, do_resize=True)
    #processor = AutoProcessor.from_pretrained("openai/clip-vit-base-patch32", do_resize=True)
    model = CLIPModel.from_pretrained(model_id)

    # if you have CUDA set it to the active device like this
    device = "cuda" if torch.cuda.is_available() else "cpu"
    # move the model to the device
    model.to(device)

    data_out = {'path': [], 'samples': torch.zeros((0, 3, 224, 224)).to(device),
                  'features': torch.zeros((0, EMBEDDING_SIZE)).to(device)}

    with torch.no_grad():
        for x, path in tqdm(dataloader):
            images = processor(
                text=None,
                images=x,
                return_tensors='pt',
                do_rescale=False
            )['pixel_values'].to(device)

            img_emb = model.get_image_features(images)
            data_out['features'] = torch.vstack([data_out['features'], img_emb])
            data_out['samples'] = torch.vstack([data_out['samples'], x])
            data_out['path'].extend(path)

    np.save(file=OUT_DIR / f'scam_donation_pic_features_CLIP_{platform}_{model_name}.npy', arr=data_out['features'].to('cpu').numpy())
    np.save(file=OUT_DIR / f'scam_donation_pic_samples_CLIP_{platform}_{model_name}.npy', arr=data_out['samples'].to('cpu').numpy())
    np.save(file=OUT_DIR / f'scam_donation_pic_path_CLIP_{platform}_{model_name}.npy', arr=data_out['path'])

