# python experiments/run_clustering.py --config=configurations/clustering_prove.json

import argparse
import os
import sys
from transformers import set_seed

sys.path.append(
    os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir)))

from src.utils.load_embeddings import *
from exp_utils import *


# ------------------------------------


DEVICE = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")


def main():

    parser = argparse.ArgumentParser(description='Run experiments based on a configuration file.')
    parser.add_argument('--config', type=str, help='Path to the configuration file')

    args = parser.parse_args()

    config_file_path = args.config

    args = read_config_file(config_file_path)

    print(args)

    set_seed(args['seed'])

    info_embeddings, embeddings = load_embeddings(args['path_embeddings'], args['path_data_dir'], args['mode'])

    embedding_name = list(args['embedding'].keys())[0]
    embedding_args = list(args['embedding'].values())[0]

    embedding_method = def_decomposition(embedding_name, **embedding_args)
    embeddings_mapped = embedding_method.forward(embeddings)

    clustering_methods = [def_clustering(list(args['clustering'].keys())[i], DEVICE, **list(args['clustering'].values())[i]) for i in range(len(args['clustering']))]

    for clustering_method in clustering_methods:
        super_folder = generate_folders(f"experiments/{args['path_exp']}", parse_super_folder(clustering_method.name, args))
        save_json(args, super_folder, "config.json")

        yhat, results = exp_run_clustering(clustering_method, args['mode'], info_embeddings, embeddings_mapped)

        # save plots
        exp_save_plots(embeddings, yhat, args['visual'], super_folder)

        serialize(yhat, f"{super_folder}/yhat.pk")

        # save the results
        results.to_csv(f'{super_folder}/results.csv', index=False)


if __name__ == "__main__":
    main()