"""Real-ESRGAN (x4plus) für weiche Quellbilder – CPU, gekachelt.

Architektur RRDBNet nach xinntao/Real-ESRGAN (BSD-3-Clause), Gewichte RealESRGAN_x4plus.pth
(https://github.com/xinntao/Real-ESRGAN/releases/download/v0.1.0/RealESRGAN_x4plus.pth).
Braucht: pip install torch --index-url https://download.pytorch.org/whl/cpu
"""
import urllib.request
from pathlib import Path

import numpy as np
import torch
from torch import nn
from torch.nn import functional as F

WEIGHTS = Path.home() / ".cache" / "sr" / "RealESRGAN_x4plus.pth"
WEIGHTS_URL = "https://github.com/xinntao/Real-ESRGAN/releases/download/v0.1.0/RealESRGAN_x4plus.pth"


class ResidualDenseBlock(nn.Module):
    def __init__(self, nf=64, gc=32):
        super().__init__()
        self.conv1 = nn.Conv2d(nf, gc, 3, 1, 1)
        self.conv2 = nn.Conv2d(nf + gc, gc, 3, 1, 1)
        self.conv3 = nn.Conv2d(nf + 2 * gc, gc, 3, 1, 1)
        self.conv4 = nn.Conv2d(nf + 3 * gc, gc, 3, 1, 1)
        self.conv5 = nn.Conv2d(nf + 4 * gc, nf, 3, 1, 1)
        self.lrelu = nn.LeakyReLU(0.2, inplace=True)

    def forward(self, x):
        x1 = self.lrelu(self.conv1(x))
        x2 = self.lrelu(self.conv2(torch.cat((x, x1), 1)))
        x3 = self.lrelu(self.conv3(torch.cat((x, x1, x2), 1)))
        x4 = self.lrelu(self.conv4(torch.cat((x, x1, x2, x3), 1)))
        x5 = self.conv5(torch.cat((x, x1, x2, x3, x4), 1))
        return x5 * 0.2 + x


class RRDB(nn.Module):
    def __init__(self, nf, gc=32):
        super().__init__()
        self.rdb1 = ResidualDenseBlock(nf, gc)
        self.rdb2 = ResidualDenseBlock(nf, gc)
        self.rdb3 = ResidualDenseBlock(nf, gc)

    def forward(self, x):
        return self.rdb3(self.rdb2(self.rdb1(x))) * 0.2 + x


class RRDBNet(nn.Module):
    def __init__(self, nf=64, nb=23, gc=32):
        super().__init__()
        self.conv_first = nn.Conv2d(3, nf, 3, 1, 1)
        self.body = nn.Sequential(*[RRDB(nf, gc) for _ in range(nb)])
        self.conv_body = nn.Conv2d(nf, nf, 3, 1, 1)
        self.conv_up1 = nn.Conv2d(nf, nf, 3, 1, 1)
        self.conv_up2 = nn.Conv2d(nf, nf, 3, 1, 1)
        self.conv_hr = nn.Conv2d(nf, nf, 3, 1, 1)
        self.conv_last = nn.Conv2d(nf, 3, 3, 1, 1)
        self.lrelu = nn.LeakyReLU(0.2, inplace=True)

    def forward(self, x):
        feat = self.conv_first(x)
        feat = feat + self.conv_body(self.body(feat))
        feat = self.lrelu(self.conv_up1(F.interpolate(feat, scale_factor=2, mode="nearest")))
        feat = self.lrelu(self.conv_up2(F.interpolate(feat, scale_factor=2, mode="nearest")))
        return self.conv_last(self.lrelu(self.conv_hr(feat)))


_model = None


def _load():
    global _model
    if _model is None:
        if not WEIGHTS.exists():
            WEIGHTS.parent.mkdir(parents=True, exist_ok=True)
            urllib.request.urlretrieve(WEIGHTS_URL, WEIGHTS)
        state = torch.load(WEIGHTS, map_location="cpu", weights_only=True)
        state = state.get("params_ema", state.get("params", state))
        _model = RRDBNet()
        _model.load_state_dict(state, strict=True)
        _model.eval()
    return _model


@torch.no_grad()
def upscale_x4(img_bgr8, tile=192, pad=12):
    """BGR-uint8-Bild vierfach vergrößern (gekachelt, damit der Speicher reicht)."""
    model = _load()
    rgb = img_bgr8[:, :, ::-1].astype(np.float32) / 255
    x = torch.from_numpy(np.ascontiguousarray(rgb.transpose(2, 0, 1)))[None]
    _, _, h, w = x.shape
    out = torch.zeros((1, 3, h * 4, w * 4))
    for y0 in range(0, h, tile):
        for x0 in range(0, w, tile):
            y1, x1 = min(y0 + tile, h), min(x0 + tile, w)
            py0, px0 = max(y0 - pad, 0), max(x0 - pad, 0)
            py1, px1 = min(y1 + pad, h), min(x1 + pad, w)
            res = model(x[:, :, py0:py1, px0:px1])
            oy, ox = (y0 - py0) * 4, (x0 - px0) * 4
            out[:, :, y0 * 4:y1 * 4, x0 * 4:x1 * 4] = res[:, :, oy:oy + (y1 - y0) * 4, ox:ox + (x1 - x0) * 4]
    res = out[0].clamp(0, 1).numpy().transpose(1, 2, 0)[:, :, ::-1]
    return (res * 255 + 0.5).astype(np.uint8)
