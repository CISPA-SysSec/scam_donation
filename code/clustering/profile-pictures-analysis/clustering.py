import umap
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import hdbscan
from sklearn import metrics

sns.set(style='white', context='notebook', rc={'figure.figsize': (14, 10)})


def dict_val_to_str(stats):
    return ",".join([str(x) for x in stats.values()])


def stats_to_str(exp_config, stats_x, stats_embedding):
    return dict_val_to_str(exp_config) + ',' + dict_val_to_str(stats_x) + ',' + dict_val_to_str(stats_embedding)


def clustering_eval(X, y_predicted):
    stats = {
        'calinski_harabasz_score': metrics.calinski_harabasz_score(X, y_predicted),
        'davies_bouldin_score': metrics.davies_bouldin_score(X, y_predicted),
        'silhouette_score': metrics.silhouette_score(X, y_predicted),
        'n_clusters': len(np.unique(y_predicted)),
        'noise_size': len(y_predicted[y_predicted == -1])
    }
    return stats


def run_umapper(x, n_neighbors=15, min_dist=0.1, n_components=2, metric='euclidean'):
    reducer = umap.UMAP(
        n_neighbors=n_neighbors,
        min_dist=min_dist,
        n_components=n_components,
        metric=metric,
        random_state=42,
        # repulsion_strength=1.0,
    )
    embedding = reducer.fit_transform(x)
    return embedding


def plot_2d_embedding(embedding, s=1, colors=None):
    plt.scatter(embedding[:, 0], embedding[:, 1], c=colors, s=s)  # , s=embedding.shape[0])
    plt.title('UMAP projection of the Clusters', fontsize=12)
    plt.show()


def cluster(embedding, metric, min_cluster_size):
    clusterer = hdbscan.HDBSCAN(metric=metric, min_cluster_size=min_cluster_size)
    cluster_labels = clusterer.fit_predict(embedding)
    return cluster_labels


def hpo_hdbscan(X, configs, exp_file):
    for metric in configs['metric']:
        for min_dist in configs['min_dist']:
            for mcs in configs['min_cluster_size']:
                for n_neighbors in configs['n_neighbors']:
                    for n_components in configs['n_components']:
                        exp_config = {
                            'n_components': n_components,
                            'n_neighbors': n_neighbors,
                            'min_cluster_size': mcs,
                            'min_dist': min_dist,
                            'metric': metric
                        }
                        print(" - ".join(f'{key}:{value}' for key, value in exp_config.items()))
                        embedding = run_umapper(X, n_neighbors=n_neighbors, n_components=n_components, min_dist=min_dist)
                        labels = cluster(embedding, metric=metric, min_cluster_size=mcs)
                        stats_embedding = clustering_eval(embedding, labels)
                        stats_x = clustering_eval(X, labels)
                        print(stats_to_str(exp_config, stats_x, stats_embedding), file=exp_file)
                        exp_file.flush()


if __name__ == "__main__":
    crypto_data = np.load('embeddings/all/scam_donation_pic_features_CLIP_all_clip-vit-large-patch14.npy')

    configs = {
        'n_neighbors': np.linspace(3, 100, 25).astype(int), #np.linspace(15, 105, 10).astype(int),
        'n_components':[2], #np.unique(np.rint(np.geomspace(2, 128, 10)).astype(int)), #np.unique(np.rint(np.geomspace(2, 256, 10)).astype(int)),

        'min_cluster_size': np.linspace(5, 100, 20).astype(int), # np.linspace(10, 50, 5).astype(int),
        'min_dist': np.geomspace(1e-02, 1, 5)[::-1],
        'metric': ['euclidean'],
    }

    with open('clustering_scammers_all_stats_CLIP.csv', 'w') as f:

        print('n_components,n_neighbors,min_cluster_size,min_dist,metric,',
              'calinski_harabasz_score_x,davies_bouldin_score_x,silhouette_score_x,n_clusters_x,noise_size_x,',
              'calinski_harabasz_score_embedding,davies_bouldin_score_embedding,silhouette_score_embedding,n_clusters_embedding,noise_size_embedding', file=f)
        hpo_hdbscan(crypto_data, configs, exp_file=f)
        f.flush()
