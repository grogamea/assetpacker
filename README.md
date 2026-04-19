# assetpacker

> CLI tool to bundle and optimize game assets for web and desktop exports

---

## Installation

```bash
pip install assetpacker
```

Or install from source:

```bash
git clone https://github.com/yourname/assetpacker.git
cd assetpacker && pip install -e .
```

---

## Usage

```bash
assetpacker [OPTIONS] INPUT_DIR OUTPUT_DIR
```

**Basic example:**

```bash
assetpacker ./assets ./dist/assets --target web --compress
```

**Options:**

| Flag | Description |
|------|-------------|
| `--target` | Export target: `web` or `desktop` (default: `web`) |
| `--compress` | Enable asset compression |
| `--format` | Output format for textures (e.g. `webp`, `png`) |
| `--watch` | Watch for file changes and repack automatically |

**Example with multiple options:**

```bash
assetpacker ./assets ./build --target desktop --format png --compress
```

---

## Features

- Bundles sprites, audio, and data files into optimized packages
- Supports web (WebGL) and desktop export targets
- Texture compression and format conversion
- Simple CLI interface with watch mode

---

## License

MIT © 2024 yourname