from pyexpat import model
import torch
import torch.nn as nn
import torchvision.models as models
import torchvision.transforms as transforms
from torchvision.models import vgg16

'''ConVit Classifier'''
class ViTBlock(nn.Module):
    def __init__(self, dim=1024, depth=2, heads=4, mlp_dim=4096, num_patches=49):
        super(ViTBlock, self).__init__()
        self.pos_embed = nn.Parameter(torch.zeros(1, num_patches, dim))
        nn.init.trunc_normal_(self.pos_embed, std=0.02)

        self.encoder = nn.ModuleList([
            nn.TransformerEncoderLayer(
                d_model=dim,
                nhead=heads,
                dim_feedforward=mlp_dim,
                dropout=0.1,
                batch_first=True,
                norm_first=True
            ) for _ in range(depth)
        ])

    def forward(self, x):
        # x: [B, N, C]
        x = x + self.pos_embed
        for enc in self.encoder:
            x = enc(x)
        return x

class ConViT(nn.Module):
    def __init__(self, num_classes=8):
        super(ConViT, self).__init__()
        # Backbone CNN: ResNet50 pretrained ImageNet
        base_model = models.resnet50(weights=models.ResNet50_Weights.IMAGENET1K_V2)
        self.feature_extractor = nn.Sequential(*list(base_model.children())[:-3]) 
        self.vit1 = ViTBlock(dim=1024, depth=2, heads=4, num_patches=196)
        self.reduce = nn.AdaptiveAvgPool2d((7,7))
        self.vit2 = ViTBlock(dim=1024, depth=1, heads=4, num_patches=49)
        self.pool = nn.AdaptiveAvgPool2d((1,1))
        self.fc = nn.Linear(1024, num_classes)

    def forward(self, x):
      feat = self.feature_extractor(x)      # [B, 1024, 14, 14]
      b, c, h, w = feat.shape
      tokens = feat.flatten(2).permute(0,2,1)  # [B,196,1024]
      tokens = self.vit1(tokens)
      feat = tokens.permute(0,2,1).view(b,c,h,w)
      feat_reduced = self.reduce(feat)
      tokens = feat_reduced.flatten(2).permute(0,2,1) # [B,49,1024]
      tokens = self.vit2(tokens)
      feat = tokens.permute(0,2,1).view(b,c,7,7)
      pooled = self.pool(feat).view(b, -1)   # [B,1024]
      out = self.fc(pooled)
      return out

'''PlantVit'''

# ---------------------------
# small helper conv block: Conv2d -> BN -> ReLU
# ---------------------------
def conv_bn_relu(in_c, out_c, kernel_size=3, stride=1, padding=1):
    return nn.Sequential(
        nn.Conv2d(in_c, out_c, kernel_size=kernel_size, stride=stride, padding=padding, bias=False),
        nn.BatchNorm2d(out_c),
        nn.ReLU(inplace=True)
    )


# ---------------------------
# Pretrained VGG16 feature extractor (up to pool3)
# ---------------------------
class VGG16Blocks(nn.Module):
    def __init__(self, pretrained=True, to_pool3=True):
        """
        to_pool3=True -> use features up to pool3 (more semantic features): output channels = 256, spatial 28x28
        """
        super().__init__()
        vgg = vgg16(weights='IMAGENET1K_V1' if pretrained else None)
        if to_pool3:
            # children() slice to include layers up to pool3 (index 17)
            self.features = nn.Sequential(*list(vgg.features.children())[:17])  # conv.. -> pool3
            self.out_channels = 256
        else:
            # keep original behavior (pool2)
            self.features = nn.Sequential(*list(vgg.features.children())[:10])  # conv.. -> pool2
            self.out_channels = 128

    def forward(self, x):
        return self.features(x)  # [B, out_channels, H, W]


# ---------------------------
# Inception v7 block (improved: BN + ReLU in all convs)
# ---------------------------
class InceptionV7(nn.Module):
    def __init__(self, in_channels=256, out_channels=512, branch_channels=128, dropout=0.0):
        """
        in_channels: channels from previous layer (e.g., 256 if using pool3)
        out_channels: final projected channels (e.g., 512)
        branch_channels: intermediate channels per branch (128 typical)
        """
        super().__init__()
        b = branch_channels

        # Branch 1: 1x1
        self.branch1 = conv_bn_relu(in_channels, b, kernel_size=1, stride=1, padding=0)

        # Branch 2: 1x1 -> (3x1) -> (1x3)
        self.branch2 = nn.Sequential(
            conv_bn_relu(in_channels, b, kernel_size=1, stride=1, padding=0),
            conv_bn_relu(b, b, kernel_size=(3, 1), stride=1, padding=(1, 0)),
            conv_bn_relu(b, b, kernel_size=(1, 3), stride=1, padding=(0, 1)),
        )

        # Branch 3: 1x1 -> (3x1+1x3) -> (3x1+1x3)
        self.branch3 = nn.Sequential(
            conv_bn_relu(in_channels, b, kernel_size=1, stride=1, padding=0),
            conv_bn_relu(b, b, kernel_size=(3, 1), stride=1, padding=(1, 0)),
            conv_bn_relu(b, b, kernel_size=(1, 3), stride=1, padding=(0, 1)),
            conv_bn_relu(b, b, kernel_size=(3, 1), stride=1, padding=(1, 0)),
            conv_bn_relu(b, b, kernel_size=(1, 3), stride=1, padding=(0, 1)),
        )

        # Branch 4: MaxPool 3x3 (stride 1 pad1) -> 1x1 conv
        self.branch4 = nn.Sequential(
            nn.MaxPool2d(3, stride=1, padding=1),
            conv_bn_relu(in_channels, b, kernel_size=1, stride=1, padding=0)
        )

        # Project concatenated branches to out_channels
        self.proj = conv_bn_relu(b * 4, out_channels, kernel_size=1, stride=1, padding=0)

        # Optional dropout on output of inception
        self.dropout = nn.Dropout2d(p=dropout) if dropout > 0 else nn.Identity()

    def forward(self, x):
        x1 = self.branch1(x)
        x2 = self.branch2(x)
        x3 = self.branch3(x)
        x4 = self.branch4(x)
        out = torch.cat([x1, x2, x3, x4], dim=1)
        out = self.proj(out)
        out = self.dropout(out)
        return out  # [B, out_channels, H, W]


# ---------------------------
# Reduce spatial dims to reduce token count (Conv stride)
# ---------------------------
class SpatialReducer(nn.Module):
    def __init__(self, in_channels=512, out_channels=512, stride=4):
        """
        Reduce HxW by stride (e.g., 28->7 when stride=4).
        """
        super().__init__()
        self.reduce = conv_bn_relu(in_channels, out_channels, kernel_size=3, stride=stride, padding=1)

    def forward(self, x):
        return self.reduce(x)  # [B, out_channels, H//stride, W//stride]


# ---------------------------
# Patch Encoder + Positional Embedding
# ---------------------------
class PatchEncoder(nn.Module):
    def __init__(self, in_c=512, emb_dim=32, grid_size=(7, 7)):
        super().__init__()
        self.in_c = in_c
        self.emb_dim = emb_dim
        self.grid_h, self.grid_w = grid_size
        self.num_patches = self.grid_h * self.grid_w
        self.proj = nn.Linear(in_c, emb_dim)
        # learnable pos emb
        self.pos_embed = nn.Parameter(torch.randn(1, self.num_patches, emb_dim) * 0.02)

    def forward(self, x):
        # x: [B, C, H, W] where H=W=grid_size
        B, C, H, W = x.shape
        assert H == self.grid_h and W == self.grid_w, f"Expected grid {self.grid_h}x{self.grid_w}, got {H}x{W}"
        x = x.permute(0, 2, 3, 1).reshape(B, H * W, C)  # [B, N, C]
        x = self.proj(x)  # [B, N, emb_dim]
        x = x + self.pos_embed  # add positional embedding
        return x  # [B, N, emb_dim]


# ---------------------------
# ViT Encoder (configurable)
# ---------------------------
class ViTEncoder(nn.Module):
    def __init__(self, emb_dim=32, depth=6, heads=4, mlp_dim=128, dropout=0.1):
        super().__init__()
        # ensure emb_dim divisible by heads
        assert emb_dim % heads == 0, "emb_dim must be divisible by heads"
        self.layers = nn.ModuleList([
            nn.TransformerEncoderLayer(
                d_model=emb_dim,
                nhead=heads,
                dim_feedforward=mlp_dim,
                dropout=dropout,
                batch_first=True,
                norm_first=True
            ) for _ in range(depth)
        ])
        self.final_norm = nn.LayerNorm(emb_dim)

    def forward(self, x):
        # x: [B, N, emb_dim]
        for layer in self.layers:
            x = layer(x)
        x = self.final_norm(x)
        return x  # [B, N, emb_dim]


# ---------------------------
# Attention Pooling (weighted sum of tokens)
# ---------------------------
class AttentionPool(nn.Module):
    def __init__(self, emb_dim):
        super().__init__()
        self.attn = nn.Linear(emb_dim, 1)

    def forward(self, x):
        # x: [B, N, emb_dim]
        scores = self.attn(x)         # [B, N, 1]
        weights = torch.softmax(scores, dim=1)  # [B, N, 1]
        pooled = (x * weights).sum(dim=1)  # [B, emb_dim]
        return pooled


# ---------------------------
# Full PlantXViT v2 (optimized)
# ---------------------------
class PlantXViT_v2(nn.Module):
    def __init__(
        self,
        num_classes=8,
        emb_dim=32,
        pretrained_vgg=True,
        use_pool3=True,
        inception_out_channels=512,
        reducer_stride=4,
        vit_depth=6,
        vit_heads=4,
        vit_mlp=128,
        vit_dropout=0.1,
        classifier_dropout=0.3
    ):
        super().__init__()

        # 1) VGG blocks (pretrained). By default use up to pool3 for richer features
        self.vgg = VGG16Blocks(pretrained=pretrained_vgg, to_pool3=use_pool3)
        vgg_out_c = self.vgg.out_channels  # 256 if pool3, else 128

        # 2) Inception block (take vgg_out_c -> inception_out_channels)
        self.inception = InceptionV7(in_channels=vgg_out_c, out_channels=inception_out_channels, branch_channels=128, dropout=0.0)

        # 3) spatial reducer to shrink patch grid (e.g., 28->7 with stride=4)
        self.reducer = SpatialReducer(in_channels=inception_out_channels, out_channels=inception_out_channels, stride=reducer_stride)
        # calculate grid size after reduction: if input 28 and stride 4 -> 7
        # We'll set grid_size = (H_after, W_after)
        # For standard 224 input and pool3 -> 28 -> stride4 -> 7
        grid_size = (7, 7)

        # 4) Patch encoder + positional embeddings
        self.patch_encoder = PatchEncoder(in_c=inception_out_channels, emb_dim=emb_dim, grid_size=grid_size)

        # 5) ViT encoder
        self.transformer = ViTEncoder(emb_dim=emb_dim, depth=vit_depth, heads=vit_heads, mlp_dim=vit_mlp, dropout=vit_dropout)

        # 6) Pooling (attention) + classifier head
        self.attn_pool = AttentionPool(emb_dim)
        self.norm = nn.LayerNorm(emb_dim)
        self.dropout = nn.Dropout(classifier_dropout)
        self.classifier = nn.Linear(emb_dim, num_classes)

    def forward(self, x):
        # x: [B, 3, 224, 224]
        x = self.vgg(x)              # [B, vgg_out_c, Hv, Wv] e.g., [B,256,28,28]
        x = self.inception(x)        # [B, inception_out, Hv, Wv] e.g., [B,512,28,28]
        x = self.reducer(x)          # [B, inception_out, Hr, Wr] e.g., [B,512,7,7]
        x = self.patch_encoder(x)    # [B, N=49, emb_dim]
        x = self.transformer(x)      # [B, N, emb_dim]
        x = self.attn_pool(x)        # [B, emb_dim]
        x = self.norm(x)
        x = self.dropout(x)
        x = self.classifier(x)       # [B, num_classes]
        return x


class_names = ['Bacterial Leaf Blight', 'Bacterial Panicle Blight', 'Blast', 
               'Brown Spot', 'Leaf Roller', 'Normal', 'Stem Borer', 'Tungro']

def get_class_name(idx):
    if 0 <= idx < len(class_names):
        return class_names[idx]
    else:
        return "unknown"

# Load model
def load_model_classifier_plantVit(MODEL_CLASSIFIER_NAME, device):
    model_plantvit_cls = PlantXViT_v2(
        num_classes=8,
        emb_dim=32,
        pretrained_vgg=True,
        use_pool3=True,
        inception_out_channels=512,
        reducer_stride=4,
        vit_depth=6,
        vit_heads=4,
        vit_mlp=128,
        vit_dropout=0.1,
        classifier_dropout=0.3
    )
    checkpoint = torch.load(MODEL_CLASSIFIER_NAME, map_location=device, weights_only=False)
    model_plantvit_cls.load_state_dict(checkpoint["model_state"])
    model_plantvit_cls.to(device)
    model_plantvit_cls.eval()
    return model_plantvit_cls

def load_model_classifier_conVit(MODEL_CLASSIFIER_NAME, device):
    model_convit_cls = ConViT(num_classes=8)
    model_convit_cls.load_state_dict(torch.load(MODEL_CLASSIFIER_NAME, map_location=device, weights_only=True))
    model_convit_cls.to(device)
    model_convit_cls.eval()
    return model_convit_cls

def transform_image_cls():
    transform = transforms.Compose([
        transforms.Resize((224, 224)), 
        transforms.ToTensor(),
        transforms.Normalize([0.485,0.456,0.406],
                            [0.229,0.224,0.225])
    ])
    return transform