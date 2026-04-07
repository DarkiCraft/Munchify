import torch
import torch.nn as nn

from config import EMBEDDING_DIM


class NCFModel(nn.Module):
    def __init__(
            self, num_users, num_items, embedding_dim=EMBEDDING_DIM, layers=None
    ):
        super(NCFModel, self).__init__()
        if layers is None:
            layers = [64, 32]
        self.user_embedding = nn.Embedding(num_users, embedding_dim)
        self.item_embedding = nn.Embedding(num_items, embedding_dim)

        # MLP
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

    def forward(self, user_indices, item_indices):
        user_emb = self.user_embedding(user_indices)
        item_emb = self.item_embedding(item_indices)

        # Concatenate user and item embeddings
        vector = torch.cat([user_emb, item_emb], dim=-1)

        feature = self.mlp(vector)
        output = self.output_layer(feature)
        prediction = self.sigmoid(output)

        return prediction.squeeze()


def train_ncf(model, train_loader, epochs=5, lr=0.001, device="cpu"):
    criterion = nn.BCELoss()  # Binary Cross Entropy since we predict probability/score
    # Note: Our labels are weights (1.0 - 5.0+), but Sigmoid is 0-1.
    # For this prototype we will treat it as regression with MSE or
    # normalize targets to 0-1.
    # Let's switch to MSELoss without Sigmoid for regression on weights,
    # OR sigmoid + BCELoss for pure probability.

    # Given the spec says "score", let's use MSELoss and remove Sigmoid from output for flexible scoring
    # Adapting the class above slightly in a separate logic or just changing it here.
    # To keep accordance with NCF paper usually it's log loss, but we have non-binary feedback.
    # Let's use MSE for simplicity on "affinity score".

    # RE-DEFINING forward for MSE approach (removing sigmoid at end)
    # Actually, let's keep it simple: 0-1 range is easier to debug.
    # We will normalize labels in the data loader or training loop.

    optimizer = torch.optim.Adam(model.parameters(), lr=lr)
    model.to(device)
    model.train()

    for epoch in range(epochs):
        total_loss = 0
        for users, items, labels in train_loader:
            users, items, labels = users.to(device), items.to(device), labels.to(device)

            # Normalize labels to 0-1 range for training stability with Sigmoid
            # Max weight is approx 5.0.
            labels = torch.clamp(labels / 5.0, 0, 1)

            optimizer.zero_grad()
            predictions = model(users, items)
            loss = criterion(predictions, labels)
            loss.backward()
            optimizer.step()
            total_loss += loss.item()

        # print(f"Epoch {epoch+1}/{epochs}, Loss: {total_loss:.4f}")

    return model
