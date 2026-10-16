import io
import os
import sys
from typing import Dict, Optional
from PIL import Image, ImageEnhance, ImageFilter

# Ensure UTF-8 stdout encoding
if hasattr(sys.stdout, "buffer"):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.append(ROOT_DIR)

TARGET_ICO_SIZES = [16, 24, 32, 48, 64, 128, 256]


def apply_safe_zone_margin(img: Image.Image, canvas_size: int = 1024, margin_ratio: float = 0.09) -> Image.Image:
    """
    Ensures 32-bit RGBA mode and enforces an 8%-10% transparent safe-zone margin
    around the non-transparent bounding box of the artwork so drop shadows and
    rounded corners never clip on Windows taskbars or web headers.
    """
    rgba = img.convert("RGBA")
    bbox = rgba.getbbox()
    if bbox:
        cropped = rgba.crop(bbox)
    else:
        cropped = rgba

    margin_px = int(round(canvas_size * margin_ratio))
    inner_max = canvas_size - (2 * margin_px)

    w, h = cropped.size
    scale = min(inner_max / max(w, 1), inner_max / max(h, 1))
    new_w = max(1, int(round(w * scale)))
    new_h = max(1, int(round(h * scale)))

    resized = cropped.resize((new_w, new_h), Image.Resampling.LANCZOS)
    master = Image.new("RGBA", (canvas_size, canvas_size), (0, 0, 0, 0))
    offset_x = (canvas_size - new_w) // 2
    offset_y = (canvas_size - new_h) // 2
    master.paste(resized, (offset_x, offset_y), resized)
    return master


def render_optical_lod(master_img: Image.Image, size: int) -> Image.Image:
    """
    Produces an optically sized 32-bit RGBA frame for the given resolution:
    - Micro sizes (16x16, 24x24): enhances silhouette contrast and emerald saturation
      before Lanczos downsampling + edge sharpening.
    - Small sizes (<= 32px): applies ImageFilter.SHARPEN to keep micro edges crisp.
    """
    work = master_img
    if size <= 24:
        work = ImageEnhance.Contrast(work).enhance(1.16)
        work = ImageEnhance.Color(work).enhance(1.14)

    frame = work.resize((size, size), Image.Resampling.LANCZOS)
    if size <= 32:
        frame = frame.filter(ImageFilter.SHARPEN)
    return frame


def build_multi_res_ico(
    source_png: str,
    output_ico: str,
    custom_lods: Optional[Dict[int, str]] = None,
    margin_ratio: float = 0.09,
) -> Image.Image:
    """
    Generates a standard 7-layer multi-resolution Windows .ico container
    (16x16, 24x24, 32x32, 48x48, 64x64, 128x128, 256x256) in 32-bit RGBA.
    Returns the 1024x1024 safe-zone padded master image.
    """
    raw_img = Image.open(source_png).convert("RGBA")
    master_1024 = apply_safe_zone_margin(raw_img, canvas_size=1024, margin_ratio=margin_ratio)

    frames = []
    for size in TARGET_ICO_SIZES:
        if custom_lods and size in custom_lods and os.path.exists(custom_lods[size]):
            frame = (
                Image.open(custom_lods[size])
                .convert("RGBA")
                .resize((size, size), Image.Resampling.LANCZOS)
            )
        else:
            frame = render_optical_lod(master_1024, size)
        frames.append(frame)

    os.makedirs(os.path.dirname(os.path.abspath(output_ico)), exist_ok=True)
    frames[-1].save(
        output_ico,
        format="ICO",
        append_images=frames[:-1],
    )
    print(f"[OK] Generated 7-layer multi-resolution icon at: {output_ico} ({os.path.getsize(output_ico)} bytes)")
    return master_1024


def main() -> None:
    public_logo = os.path.join(ROOT_DIR, "frontend", "public", "oraculo-logo.png")
    favicon_ico = os.path.join(ROOT_DIR, "frontend", "public", "favicon.ico")
    assets_ico = os.path.join(ROOT_DIR, "assets", "app.ico")
    ext_icons_dir = os.path.join(ROOT_DIR, "chrome-extension", "icons")

    master_1024 = build_multi_res_ico(public_logo, favicon_ico, margin_ratio=0.09)

    # Copy/generate desktop launcher .ico in assets/app.ico
    os.makedirs(os.path.dirname(assets_ico), exist_ok=True)
    build_multi_res_ico(public_logo, assets_ico, margin_ratio=0.09)

    # Save optimized 512x512 RGBA web master with 9% safe-zone padding
    web_512 = master_1024.resize((512, 512), Image.Resampling.LANCZOS)
    web_512.save(public_logo, format="PNG", optimize=True)
    print(f"[OK] Updated 512x512 32-bit RGBA web master (9% safe margin): {public_logo} ({os.path.getsize(public_logo)} bytes)")

    # Synchronize Chrome Extension icons with optical sizing
    os.makedirs(ext_icons_dir, exist_ok=True)
    for ext_size in (16, 24, 32, 48, 128):
        ext_path = os.path.join(ext_icons_dir, f"icon{ext_size}.png")
        lod_frame = render_optical_lod(master_1024, ext_size)
        lod_frame.save(ext_path, format="PNG", optimize=True)
        print(f"[OK] Updated Chrome Extension LOD icon ({ext_size}x{ext_size}): {ext_path}")

    # Verify embedded .ico layers
    with Image.open(favicon_ico) as ico_check:
        sizes = sorted(ico_check.info.get("sizes", []), key=lambda s: s[0])
        print(f"[VERIFY] Verified .ico embedded layers: {sizes}")


if __name__ == "__main__":
    main()
