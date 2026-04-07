import torch
import torch.nn as nn


class NCFModel(nn.Module):
    def __init__(self, num_users: int, num_items: int, embedding_dim: int = 32, layers: list = None):
        super().__init__()
        if layers is None:
            layers = [64, 32]

        self.user_embedding = nn.Embedding(num_users, embedding_dim)
        self.item_embedding = nn.Embedding(num_items, embedding_dim)

        input_dim = embedding_dim * 2
        mlp_modules = []
        for dim in layers:
            mlp_modules.append(nn.Linear(input_dim, dim))
            mlp_modules.append(nn.ReLU())
            mlp_modules.append(nn.Dropout(0.2))
            input_dim = dim

        self.mlp = nn.Sequential(*mlp_modules)
        self.output_layer = nn.Linear(layers[-1], 1)
        self.sigmoid = nn.Sigmoid()

    def forward(self, user_indices: torch.Tensor, item_indices: torch.Tensor) -> torch.Tensor:
        user_emb = self.user_embedding(user_indices)
        item_emb = self.item_embedding(item_indices)
        vector = torch.cat([user_emb, item_emb], dim=-1)
        return self.sigmoid(self.output_layer(self.mlp(vector))).squeeze()


def train_ncf(
        model: NCFModel,
        interactions: list,
        num_items: int,
        epochs: int = 5,
        lr: float = 0.001,
        batch_size: int = 32,
        device: str = "cpu"
) -> NCFModel:
    from torch.utils.data import DataLoader, TensorDataset

    # Build training data with negative sampling
    positives = set((i.user_id, i.item_id) for i in interactions)

    users, items, labels = [], [], []
    for i in interactions:
        # Positive
        users.append(i.user_id)
        items.append(i.item_id)
        labels.append(min(1.0, i.weight / 5.0) if hasattr(i, 'weight') else 1.0)

        # Negative sample
        import random
        for _ in range(10):
            neg = random.randint(0, num_items - 1)
            if (i.user_id, neg) not in positives:
                users.append(i.user_id)
                items.append(neg)
                labels.append(0.0)
                break

    dataset = TensorDataset(
        torch.tensor(users, dtype=torch.long),
        torch.tensor(items, dtype=torch.long),
        torch.tensor(labels, dtype=torch.float32)
    )
    loader = DataLoader(dataset, batch_size=batch_size, shuffle=True)

    model.to(device)
    model.train()
    optimizer = torch.optim.Adam(model.parameters(), lr=lr)
    criterion = nn.BCELoss()

    for epoch in range(epochs):
        for u, it, l in loader:
            u, it, l = u.to(device), it.to(device), l.to(device)
            optimizer.zero_grad()
            criterion(model(u, it), l).backward()
            optimizer.step()

    model.eval()
    return model


def predict_ncf(model: NCFModel, user_id: int, num_items: int, device: str = "cpu"):
    model.eval()
    with torch.no_grad():
        all_items = torch.arange(num_items, dtype=torch.long).to(device)
        user_tensor = torch.full((num_items,), user_id, dtype=torch.long).to(device)
        scores = model(user_tensor, all_items)
    return scores.cpu().numpy()