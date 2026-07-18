# Profile Asset Scripts

This folder contains Python scripts to fetch contribution data and render dynamic profile SVG assets for the GitHub README.

## 🛠 Setup

Ensure you have the dependencies installed:
```bash
pip install -r scripts/requirements.txt
```

---

## 📸 Updating the ASCII Portrait

If you want to update the ASCII portrait with your own photo:

1. **Place your photo** inside the `assets/` directory (e.g., `assets/source-photo.jpg` or `assets/profile.png`).
2. **Prepare the photo** (converts to optimized grayscale and boosts contrast):
   ```bash
   python scripts/prep_photo.py assets/source-photo.jpg
   ```
   *This saves the prepped image directly to `assets/source-prepped.png`.*
3. **Generate the ASCII SVG**:
   ```bash
   python scripts/make_ascii_svg.py
   ```
   *This generates the animated, gradient-colored ASCII SVG at `assets/mahesh-ascii.svg`.*

---

## 📊 Refreshing All Profile Assets

To manually refresh all generated SVGs:

```bash
# 1. Fetch latest contribution data from GitHub
python scripts/fetch_contributions.py

# 2. Render contribution heatmap SVG
python scripts/render_heatmap_svg.py

# 3. Render neofetch-style Info Card SVG
python scripts/make_info_card.py

# 4. Render ASCII portrait SVG
python scripts/make_ascii_svg.py
```

### Automation
A GitHub Action (`.github/workflows/update-profile-art.yml`) runs the contribution scraper and heatmap renderer automatically every day at ~06:17 UTC to keep your stats up-to-date.
