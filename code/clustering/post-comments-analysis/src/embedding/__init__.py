from src.embedding.projection import ProjectionAlgorithm
from src.embedding.projection_umap import ProjectUMAP
from src.embedding.projection_pca import ProjectPCA
from src.embedding.projection_tsne import ProjectTSNE
from src.embedding.projection_identity import ProjectIdentity

__all__ = ['ProjectionAlgorithm', 'ProjectUMAP','ProjectPCA', 'ProjectTSNE', 'ProjectIdentity']