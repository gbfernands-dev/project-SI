"""Converte imagens fotográficas do catálogo para WebP quando houver economia."""

from pathlib import Path

from PIL import Image


CATALOG_ROOT = Path(__file__).resolve().parents[1] / "catalogo-godzilla-ugb"


def rgb_on_white(image: Image.Image) -> Image.Image:
    if image.mode in {"RGBA", "LA"} or "transparency" in image.info:
        rgba = image.convert("RGBA")
        background = Image.new("RGB", rgba.size, "white")
        background.paste(rgba, mask=rgba.getchannel("A"))
        return background
    return image.convert("RGB")


def optimize_catalog() -> tuple[int, int]:
    converted = 0
    bytes_saved = 0
    for source in sorted(CATALOG_ROOT.rglob("*.png")):
        if "guia-de-" in source.name:
            continue
        target = source.with_suffix(".webp")
        with Image.open(source) as image:
            rgb_on_white(image).save(target, "WEBP", quality=90, method=6)
        if target.stat().st_size >= source.stat().st_size:
            target.unlink()
            continue
        bytes_saved += source.stat().st_size - target.stat().st_size
        source.unlink()
        converted += 1
    return converted, bytes_saved


if __name__ == "__main__":
    image_count, saved = optimize_catalog()
    print(f"Imagens convertidas: {image_count}; economia: {saved / 1024 / 1024:.2f} MiB")
