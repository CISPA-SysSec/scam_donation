## Exploring Scam Donations on Social Media Platforms

## Dependencies and Reproducibility

In order to improve the reproducibility of our experiments, we released our anaconda environment, containing all dependencies and corresponding SW versions. The environment can be installed by running the following command:

    conda env create -f environment.yml

After installation, the conda environment can be loaded with:

    conda activate -f scamdonation_posts

## Posts clustering analysis

The following are commands for performing posts clustering analysis.

The default directory for storing all the account's posts is "data/all". However, the location of the files inside the Python scripts can be changed.

1. To create the embeddings for the posts saved in txt:

    ```bash
    python create_embeddings.py
    ```

    Otherwise, for posts saved in json:
    
    ```bash
    python create_embeddings_json.py
    ```

2. After having created the embeddings for the posts, it is possible to run the BERTopic framework for clustering using:

    ```bash
    python experiments/run_BERTopic.py --config=configurations/BERTopic/15_0.8_50_clustering_euclidean_full.json
    ```

    where --config defines the location of the BERTopic JSON configuration file. To change the hyperparametrization for posts clustering analysis, create a JSON configuration file in "configurations/BERTopic."

3. Finally, after having changed the PATH_RESULT variable with the path of the results obtained by the "run_BERTopic.py" script, the following command generates the CSV results files:

    ```bash
    python experiments/analyze_BERTopic.py --config=configurations/BERTopic/15_0.8_50_clustering_euclidean_full.json
    ```

    Again, --config defines the BERTopic JSON configuration file.

4. Additionally, after having changed the PATH_CSV_DATA variable with the path of the results obtained by the "analyze_BERTopic.py" script, it is possible to generate extra CSV analysis files using:

    ```bash
    python experiments/extract_results_BERTopic.py
    ```

## Sentiment Analysis

The following are commands for performing sentiment analysis on posts.

1. To create the scores for the posts:

    ```bash
    python sentiment_analysis_comments.py
    ```

2. Finally, to analyze the scores and the comments:

    ```bash
    python experiments/analyze_sentiment_analysis.py
    ```

## Llama Analyzer

The following are commands for performing posts clustering with Llama. The main directory for this analysis is "llama_analyzer".

The default directory for storing all the posts is "llama_analyzer/datasets". However, the location of the files inside the Python scripts can be changed.

1. To start the analysis:

    ```bash
    python llama_analyzer/llama_analyzer.py
    ```