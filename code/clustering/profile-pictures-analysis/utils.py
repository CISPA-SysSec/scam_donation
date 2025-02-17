import torch
import os
from torch.utils.data import Dataset, DataLoader
import numpy as np
import random
from torchvision import transforms
from PIL import Image, UnidentifiedImageError

class ScamDonationImgDataset(Dataset):
    def __init__(self, platform, data_dir='/data/scam_donation_2024', transform=transforms.ToTensor()):
        """
        Initialize the ScamDonationImgDataset.

        Parameters:
        - platform (str): Platform name, either 'Facebook' or 'Youtube'.
        - data_dir (str): Base directory of the dataset.
        - transform (callable, optional): A function/transform that takes in an image and returns a transformed version.
        """
        self.platform = platform
        self.data_dir = data_dir
        self.transform = transform

        #if self.platform.lower() not in ['facebook', 'youtube', '']:
        #    raise ValueError("Platform must be 'Facebook' or 'Youtube'")

        self.dataset_path = os.path.join(self.data_dir, self.platform)
        self.image_paths = self._load_image_paths()

    def _load_image_paths(self):
        """
        Load all image paths from the dataset directory.

        Returns:
        - list: A list of image file paths.
        """
        image_paths = []
        for root, _, files in os.walk(self.dataset_path):
            for file in files:
                if file.lower().endswith(('png', 'jpg', 'jpeg', 'bmp', 'gif')):
                    image_paths.append(os.path.join(root, file))
        return image_paths

    def __len__(self):
        return len(self.image_paths)

    def __getitem__(self, idx):
        img_path = self.image_paths[idx]
        try:
            image = Image.open(img_path).convert('RGB')
            if self.transform:
                image = self.transform(image)
            return image, img_path
        except UnidentifiedImageError:
            print(f"Cannot identify image file at path {img_path}.")


def _worker_init_fn(worker_id):
    """
    Worker initialization function to set the seed for each worker.
    """
    seed = torch.initial_seed() % 2**32
    np.random.seed(seed)
    random.seed(seed)
def get_scam_donation_dataloader(platform, data_dir='scam_donation_2024', transform=None, batch_size=128, shuffle=True, num_workers=4, seed=4444):
    """
    Create a DataLoader for the ScamDonationImgDataset.

    Parameters:
    - platform (str): Platform name, either 'Facebook' or 'Youtube'.
    - data_dir (str): Base directory of the dataset.
    - transform (callable, optional): A function/transform that takes in an image and returns a transformed version.
    - batch_size (int): Number of samples per batch.
    - shuffle (bool): Whether to shuffle the data.
    - num_workers (int): Number of subprocesses to use for data loading.

    Returns:
    - DataLoader: The created DataLoader.
    """
    dataset = ScamDonationImgDataset(platform=platform, data_dir=data_dir, transform=transform)

    generator = torch.Generator()
    generator.manual_seed(seed)

    return DataLoader(dataset, batch_size=batch_size, shuffle=shuffle, num_workers=num_workers, generator=generator, worker_init_fn=_worker_init_fn)


def set_seed(seed):
    """
    Set seed for reproducibility.

    Parameters:
    - seed (int): The seed to set.
    """
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    torch.cuda.manual_seed(seed)
    torch.cuda.manual_seed_all(seed)  # if you are using multi-GPU.

    # Ensure deterministic behavior on CUDA
    torch.backends.cudnn.deterministic = True
    torch.backends.cudnn.benchmark = False