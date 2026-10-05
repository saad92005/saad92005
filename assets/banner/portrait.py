"""Stage 1: photo + logo outlines -> dot data (.npy). Source of truth for the banner.

    python portrait.py photo.jpg     # writes data/*.npy and prints quality metrics

The source photo is intentionally not committed; data/*.npy is the source of truth.
"""
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageEnhance, ImageFilter, ImageOps
from scipy import ndimage
from scipy.optimize import linear_sum_assignment
from scipy.spatial import cKDTree

GW, GH = 300, 340            # dither grid
N_TRAVEL = 900
OUT = Path(__file__).parent / "data"
rng = np.random.default_rng(7)


def crop_head_shoulders(im):
    # Head + shoulders, not a tight face crop. Face centre in the source is ~x=820.
    w, h = im.size
    ch = h
    cw = int(ch * GW / GH)
    cx = 820
    return im.crop((cx - cw // 2, 0, cx + cw // 2, ch))


def subject_mask(rgb):
    """Background = near the backdrop colour (sampled from the top corners)."""
    a = np.asarray(rgb).astype(float)
    bg = np.concatenate([a[:12, :12].reshape(-1, 3), a[:12, -12:].reshape(-1, 3)]).mean(0)
    dist = np.linalg.norm(a - bg, axis=2)
    m = dist > 28
    m = ndimage.binary_closing(m, iterations=3)
    m = ndimage.binary_fill_holes(m)
    lab, n = ndimage.label(m)
    if n > 1:
        sizes = ndimage.sum(m, lab, range(1, n + 1))
        m = lab == (1 + int(np.argmax(sizes)))
    return m


def prep_gray(rgb):
    g = ImageOps.grayscale(rgb)
    g = ImageOps.autocontrast(g, cutoff=1)
    g = ImageEnhance.Contrast(g).enhance(1.3)
    g = g.filter(ImageFilter.UnsharpMask(radius=3, percent=140))
    return np.asarray(g).astype(float) / 255.0


def fs_dither(v, mask=None):
    """1-bit Floyd-Steinberg, serpentine. v in [0,1]; returns bool 'ink' where v rounds to 1.
    With a mask, error never diffuses outside it (hard-clears bleed at the edge)."""
    v = v.copy()
    h, w = v.shape
    out = np.zeros_like(v, dtype=bool)
    for y in range(h):
        xs = range(w) if y % 2 == 0 else range(w - 1, -1, -1)
        d = 1 if y % 2 == 0 else -1
        for x in xs:
            if mask is not None and not mask[y, x]:
                continue
            old = v[y, x]
            new = 1.0 if old >= 0.5 else 0.0
            out[y, x] = new > 0
            e = old - new
            for dx, dy, wgt in ((d, 0, 7 / 16), (-d, 1, 3 / 16), (0, 1, 5 / 16), (d, 1, 1 / 16)):
                nx, ny = x + dx, y + dy
                if 0 <= nx < w and ny < h and (mask is None or mask[ny, nx]):
                    v[ny, nx] += e * wgt
    return out


def logo_points(png_path, n, box):
    """Blue-noise-ish sample of n points inside a rendered logo, fitted into box (x0,y0,x1,y1)."""
    a = np.asarray(Image.open(png_path).convert("RGBA"))[:, :, 3] > 128
    ys, xs = np.nonzero(a)
    idx = rng.choice(len(xs), n * 6, replace=False)
    pts = np.stack([xs[idx], ys[idx]], 1).astype(float)
    # Lloyd-style relaxation over the filled pixels for even coverage
    cand = np.stack([xs, ys], 1).astype(float)
    sel = pts[:n].copy()
    for _ in range(8):
        sub = cand[rng.choice(len(cand), min(len(cand), 60000), replace=False)]
        nearest = cKDTree(sel).query(sub)[1]
        for k in range(n):
            m = nearest == k
            if m.any():
                sel[k] = sub[m].mean(0)
    # fit into box
    (x0, y0, x1, y1) = box
    mn, mx = cand.min(0), cand.max(0)
    s = min((x1 - x0) / (mx - mn)[0], (y1 - y0) / (mx - mn)[1])
    off = np.array([x0 + ((x1 - x0) - (mx - mn)[0] * s) / 2, y0 + ((y1 - y0) - (mx - mn)[1] * s) / 2])
    return (sel - mn) * s + off


def ot_match(a, b):
    cost = ((a[:, None, :] - b[None, :, :]) ** 2).sum(-1)
    r, c = linear_sum_assignment(cost)
    return b[c[np.argsort(r)]]


def evenness(groups, xy, k=4):
    """Mean coefficient of variation of each intro group's spread over a kxk grid (0 = perfectly even)."""
    cells = (np.minimum(xy[:, 0] * k // GW, k - 1) * k + np.minimum(xy[:, 1] * k // GH, k - 1)).astype(int)
    total = np.bincount(cells, minlength=k * k).astype(float)
    cvs = []
    for g in np.unique(groups):
        cnt = np.bincount(cells[groups == g], minlength=k * k) / max(1, (groups == g).sum())
        exp = total / total.sum()
        cvs.append(np.abs(cnt - exp).sum() / 2)
    return float(np.mean(cvs))


def straightness(bands, xy):
    """Share of band-boundary edges between 4-neighbours lying on long straight runs (grid trap detector)."""
    grid = -np.ones((GH, GW), int)
    grid[xy[:, 1], xy[:, 0]] = bands
    hb = (grid[:, 1:] != grid[:, :-1]) & (grid[:, 1:] >= 0) & (grid[:, :-1] >= 0)
    vb = (grid[1:, :] != grid[:-1, :]) & (grid[1:, :] >= 0) & (grid[:-1, :] >= 0)
    # a straight boundary = same boundary column continuing on the next row
    straight = (hb[1:, :] & hb[:-1, :]).sum() + (vb[:, 1:] & vb[:, :-1]).sum()
    return float(straight / max(1, hb.sum() + vb.sum()) * 0.25)


def main(photo):
    OUT.mkdir(exist_ok=True)
    im = Image.open(photo).convert("RGB")
    crop = crop_head_shoulders(im).resize((GW, GH), Image.LANCZOS)
    gray = prep_gray(crop)
    mask = subject_mask(crop)

    # Dark mode: dots = lit parts of the subject only. Light mode: dots = dark parts of the photo.
    dark = fs_dither(gray, mask) & mask
    # Cap ink density at ~70% so large dark areas (the suit) keep dither texture instead of going solid
    light = fs_dither((1.0 - gray) * 0.7)
    np.save(OUT / "dark.npy", dark)
    np.save(OUT / "light.npy", light)
    np.save(OUT / "mask.npy", mask)
    print(f"dots: dark {dark.sum():,} · light {light.sum():,} · subject {mask.mean():.0%} of frame")

    for name, d in (("dark", dark), ("light", light)):
        ys, xs = np.nonzero(d)
        xy = np.stack([xs, ys], 1)
        # Intro: 60 interleaved random groups (never spatial)
        intro = rng.integers(0, 60, len(xy))
        # Loop drift bands: per-dot noise (sigma 4) BEFORE grouping, or quantised linear drift = grid
        noisy = xy + rng.normal(0, 4, xy.shape)
        # Irregular cells: nearest of 94 random seeds (Voronoi), so seams are never axis-aligned
        seeds = xy[rng.choice(len(xy), 94, replace=False)] + rng.normal(0, 6, (94, 2))
        bands = cKDTree(seeds).query(noisy)[1]
        np.save(OUT / f"{name}_xy.npy", xy)
        np.save(OUT / f"{name}_intro.npy", intro)
        np.save(OUT / f"{name}_bands.npy", bands)
        print(f"  {name}: evenness {evenness(intro, xy):.3f} (good ≈0.05) · "
              f"straight-boundary {straightness(bands, xy):.3f} (organic ≈0.01, grid ≈0.17) · bands {len(np.unique(bands))}")

        # Travellers: start/end on portrait dots, morph through the three logos
        start = xy[rng.choice(len(xy), N_TRAVEL, replace=False)].astype(float)
        box = (40, 50, 260, 290)
        logos = [logo_points(Path(__file__).parent / "logos" / f"{n}.png", N_TRAVEL, box) for n in ("python", "typescript", "flutter")]
        path = [start]
        for L in logos:
            path.append(ot_match(path[-1], L))
        np.save(OUT / f"{name}_travel.npy", np.stack(path))  # (4, N, 2): portrait, py, ts, flutter


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "photo.jpg")
