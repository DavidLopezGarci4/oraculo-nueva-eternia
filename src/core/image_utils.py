"""
Shared image resolution, safe WebP conversion, and confirmed-upload URL sync helpers.
Prevents 'LA'-mode Pillow IndexError, handles CI-polluted Excel paths, and verifies WebP magic bytes.
"""
from __future__ import annotations

import io
import logging
import os
import re
import urllib.parse
from pathlib import Path
from typing import Dict, Optional

logger = logging.getLogger("ImageUtils")

VALID_IMAGE_EXTENSIONS = (".webp", ".jpg", ".jpeg", ".png")


def has_webp_magic(file_path: Path | str) -> bool:
    """Returns True only if the file begins with genuine RIFF...WEBP magic bytes."""
    try:
        with open(file_path, "rb") as fh:
            header = fh.read(12)
        return len(header) >= 12 and header[:4] == b"RIFF" and header[8:12] == b"WEBP"
    except OSError:
        return False


def encode_webp_bytes(raw_bytes: bytes, dest_path: Path | str, quality: int = 85) -> None:
    """Converts arbitrary image bytes (including 'LA', 'RGBA', transparent 'P') into genuine WebP."""
    from PIL import Image

    with Image.open(io.BytesIO(raw_bytes)) as img:
        has_alpha = img.mode in ("RGBA", "LA") or (img.mode == "P" and "transparency" in img.info)
        if has_alpha:
            rgba = img.convert("RGBA")
            background = Image.new("RGB", rgba.size, (255, 255, 255))
            background.paste(rgba, mask=rgba.split()[3])
            img = background
        elif img.mode != "RGB":
            img = img.convert("RGB")
        img.save(str(dest_path), "WEBP", quality=quality)


def encode_webp_file(src_path: Path | str, dest_path: Path | str, quality: int = 85) -> None:
    """Converts a local image file (including 'LA', 'RGBA', transparent 'P') into genuine WebP."""
    from PIL import Image

    with Image.open(str(src_path)) as img:
        has_alpha = img.mode in ("RGBA", "LA") or (img.mode == "P" and "transparency" in img.info)
        if has_alpha:
            rgba = img.convert("RGBA")
            background = Image.new("RGB", rgba.size, (255, 255, 255))
            background.paste(rgba, mask=rgba.split()[3])
            img = background
        elif img.mode != "RGB":
            img = img.convert("RGB")
        img.save(str(dest_path), "WEBP", quality=quality)


def resolve_catalog_image_path(
    image_path_str: str | None,
    project_root: Path,
    default_subdir: str = "images",
) -> Path | None:
    """
    Normalizes Excel `Image Path` values (e.g. '/app/data/MOTU/...' or
    '/home/runner/work/.../data/MOTU/...') strictly inside `<project_root>/data/MOTU/...`.
    """
    if not image_path_str:
        return None

    normalized = str(image_path_str).strip().replace("\\", "/")
    if not normalized or normalized.lower() == "nan":
        return None

    root_resolved = project_root.resolve()
    marker = "data/motu/"
    lower_norm = normalized.lower()
    idx = lower_norm.find(marker)

    if idx != -1:
        rel_part = normalized[idx:].lstrip("/")
        candidate = (root_resolved / rel_part).resolve()
    else:
        filename = os.path.basename(normalized)
        if not filename:
            return None
        candidate = (root_resolved / "data" / "MOTU" / default_subdir / filename).resolve()

    if not candidate.is_relative_to(root_resolved):
        return None
    return candidate


def find_existing_image_with_sibling(candidate_path: Path) -> Path | None:
    """Returns candidate_path if present, or any valid sibling image with matching stem."""
    if candidate_path.is_file() and candidate_path.stat().st_size > 0:
        return candidate_path

    parent = candidate_path.parent
    if not parent.is_dir():
        return None

    stem = candidate_path.stem
    for ext in VALID_IMAGE_EXTENSIONS:
        sibling = parent / f"{stem}{ext}"
        if sibling.is_file() and sibling.stat().st_size > 0:
            return sibling
    return None


def apply_confirmed_cloud_image_urls(
    session,
    uploaded_urls: Dict[str, str],
    stem_to_product_id: Optional[Dict[str, int]] = None,
    is_vintage: bool = False,
) -> int:
    """
    Updates ProductModel.image_url ONLY for entries confirmed as uploaded to Supabase Storage.
    """
    if not uploaded_urls:
        return 0

    from src.domain.models import ProductModel

    updated = 0
    assigned_pids: set[int] = set()

    if stem_to_product_id:
        for stem, public_url in uploaded_urls.items():
            pid = stem_to_product_id.get(stem)
            if pid:
                row = session.query(ProductModel).filter(ProductModel.id == pid).first()
                if row and row.image_url != public_url:
                    row.image_url = public_url
                    updated += 1
                assigned_pids.add(pid)

    # Fallback match by figure_id suffix or existing URL stem for remaining confirmed uploads
    remaining = {s: u for s, u in uploaded_urls.items() if not stem_to_product_id or s not in stem_to_product_id}
    if remaining:
        query = session.query(ProductModel)
        if is_vintage:
            query = query.filter(ProductModel.is_vintage.is_(True))
        else:
            query = query.filter(ProductModel.is_vintage.is_not(True))

        for prod in query.all():
            if prod.id in assigned_pids:
                continue
            matched_url = None
            if prod.image_url:
                cur_stem = os.path.splitext(os.path.basename(urllib.parse.urlparse(prod.image_url).path))[0]
                if cur_stem in remaining:
                    matched_url = remaining[cur_stem]
            if not matched_url and prod.figure_id:
                safe_fid = re.escape(str(prod.figure_id).strip())
                suffix_re = re.compile(rf"(?:^|-){safe_fid}$")
                for stem, public_url in remaining.items():
                    if suffix_re.search(stem):
                        matched_url = public_url
                        break
            if matched_url and prod.image_url != matched_url:
                prod.image_url = matched_url
                updated += 1

    if updated:
        session.commit()
    return updated
