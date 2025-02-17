import os
from datetime import datetime

import csv

import torch

from transformers import set_seed


MODEL_NAME = 'cardiffnlp/twitter-roberta-base-sentiment-latest'

OUTPUT_DIRECTORY = f"sentiment_all/{MODEL_NAME.split('/')[-1]}/data/datasets/scam_donation_2024_copy/comment/youtube"

DATE = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
PATH_RESULT = f"experiments/results/sentiment_analysis/{MODEL_NAME}/{DATE}"

# -----

if not os.path.exists(PATH_RESULT):
    os.makedirs(PATH_RESULT)

# -----

SEED = 1112


def save_sentiment_analysis_csv(path_files, path_result_csv):
    file_names = [f for f in os.listdir(path_files) if os.path.isfile(os.path.join(path_files, f))]

    with open(path_result_csv, mode='w', newline='') as file:
        writer = csv.writer(file)

        writer.writerow(['file_path', 'file_name', 'sentence', 'best_rank', 'complete_ranking'])

        for i, file_name in enumerate(file_names):

            obj_sa = torch.load(path_files + '/' + file_name)
            txt_path = obj_sa["txt_path"]
            txt_name = obj_sa["file_name"]

            for sentence, rank_list in zip(obj_sa["sentences"], obj_sa["ranking_list"]):

                writer.writerow([txt_path, txt_name, sentence, rank_list[0], rank_list])

def main():
    set_seed(SEED)

    path_result_csv = f"{PATH_RESULT}/sentiment_analysis.csv"

    save_sentiment_analysis_csv(OUTPUT_DIRECTORY, path_result_csv)

if __name__ == "__main__":
    main()