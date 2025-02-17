## Exploring Scammers Pictures 

## Dependencies and Reproducibility

In order to improve the reproducibility of our experiments, we released our anaconda environment, containing all dependencies and corresponding SW versions. The environment can be installed by running the following command:

    conda env create -f environment.yml

After installation, the environment can be loaded with:

    ```bash
    conda activate scamdonation_picture
    ```

## Clustering analysis

The following are commands for performing posts clustering analysis.

The default directory for storing all the account's profile pictures is "/data/datasets/scam_donation_2024/scammer_images_latest/". However, the location of the files inside the Python scripts can be changed.

1. To create the embeddings for the posts saved in txt:

    ```bash
    python clip-feature-extractor.py
    ```

2. After having created the embeddings for the posts, it is possible to run the clustering algorithm hyperparameter exploration  using:

    ```bash
    python clustering.py
    ```

3. Finally, a jupyter notebook (analysis.ipynb) can be used to explore the clustering results and export clustering samples.
