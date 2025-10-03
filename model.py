import torch
import torch.nn as nn
import torchvision.models as models
from PIL import Image
import torchvision.transforms as transforms

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print("Using device:", device)


class ViTBlock(nn.Module):
    def __init__(self, dim=2048, depth=2, heads=4, mlp_dim=4096):
        super(ViTBlock, self).__init__()
        self.encoder = nn.ModuleList([
            nn.TransformerEncoderLayer(
                d_model=dim,
                nhead=heads,
                dim_feedforward=mlp_dim,
                dropout=0.1,
                batch_first=True
            ) for _ in range(depth)
        ])
    def forward(self, x):
        for enc in self.encoder:
            x = enc(x)
        return x

class ConViT(nn.Module):
    def __init__(self, num_classes=8):
        super(ConViT, self).__init__()
        base_model = models.resnet50(weights=models.ResNet50_Weights.IMAGENET1K_V2)
        self.feature_extractor = nn.Sequential(*list(base_model.children())[:-2])

        self.vit1 = ViTBlock(dim=2048, depth=2, heads=4)
        self.reduce = nn.AdaptiveAvgPool2d((7,7))
        self.vit2 = ViTBlock(dim=2048, depth=2, heads=4)

        self.pool = nn.AdaptiveAvgPool2d((1,1))
        self.fc = nn.Linear(2048, num_classes)

    def forward(self, x):
        feat = self.feature_extractor(x)
        b, c, h, w = feat.shape

        tokens = feat.flatten(2).permute(0,2,1)
        tokens = self.vit1(tokens)
        feat = tokens.permute(0,2,1).view(b,c,h,w)

        feat_reduced = self.reduce(feat)
        tokens = feat_reduced.flatten(2).permute(0,2,1)
        tokens = self.vit2(tokens)
        feat = tokens.permute(0,2,1).view(b,c,7,7)

        pooled = self.pool(feat).view(b, -1)
        out = self.fc(pooled)
        return out

class_names = ['bacterial_leaf_blight', 'bacterial_panicle_blight', 'blast', 
               'brown_spot', 'leaf_roller', 'normal', 'stem_borer', 'tungro']


model = ConViT(num_classes=8)
model.load_state_dict(torch.load("best_model.pth", map_location=device, weights_only=True))
model.to(device)
model.eval()


transform = transforms.Compose([
    transforms.Resize((224, 224)), 
    transforms.ToTensor(),
    transforms.Normalize([0.485,0.456,0.406],
                         [0.229,0.224,0.225])
])

# def predict(image_path):
#     image = Image.open(image_path).convert("RGB")
#     img_tensor = transform(image).unsqueeze(0).to(device)  
#     with torch.no_grad():
#         outputs = model(img_tensor)
#         _, pred = torch.max(outputs, 1)
#     return pred.item()

# # test
# result = predict("test2.jpg")
# print("Predicted class:", class_names[result])

import torch.nn.functional as F

def predict(image_path):
    image = Image.open(image_path).convert("RGB")
    img_tensor = transform(image).unsqueeze(0).to(device)  # batch 1

    with torch.no_grad():
        outputs = model(img_tensor)              # logits từ model
        probs = F.softmax(outputs, dim=1)       # chuyển sang xác suất
        pred_prob, pred_idx = torch.max(probs, 1)

    pred_idx = pred_idx.item()
    pred_prob = pred_prob.item()

    # In xác suất cho tất cả lớp
    prob_list = probs.squeeze(0).cpu().numpy()
    for i, p in enumerate(prob_list):
        print(f"{class_names[i]}: {p*100:.2f}%")

    return pred_idx, pred_prob

# Test
pred_idx, pred_prob = predict("test4.png")
print(f"\nPredicted class: {class_names[pred_idx]} ({pred_prob*100:.2f}%)")
