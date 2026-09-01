# Word Cloud Generator Configuration Guide

## 1. How to Enable Word Cloud Generation
> Note: Word clouds are generated when `SAVE_DATA_OPTION` is set to `json` or `jsonl`.

Required configuration options in `config/base_config.py`:

```python
# Data storage format: json or jsonl
SAVE_DATA_OPTION = "jsonl"
```

```python
# Enable comment extraction (required for comment word cloud)
ENABLE_GET_COMMENTS = True
```

```python
# Enable word cloud generation
ENABLE_GET_WORDCLOUD = True
```

```python
# Custom words and custom dictionary grouping
CUSTOM_WORDS = {
    'custom_keyword': 'Category',
    'another_phrase': 'Term'
}
```

```python
# Stopwords list file path
STOP_WORDS_FILE = "./docs/hit_stopwords.txt"
```

```python
# Font file path for text rendering
FONT_PATH = "./docs/STZHONGS.TTF"
```

### Explanation of Settings

- **Custom Words**: `CUSTOM_WORDS` allows defining custom tokens and categories that tokenizer will treat as whole words.
- **Stopwords**: Add words to filter out into `./docs/hit_stopwords.txt` (one word per line).
- **Font Path**: `FONT_PATH` defines the TrueType font used for rendering text in images.

## 2. Generated Word Cloud Output Location

Generated files are saved in the `data/` directory under `words/`:
- `.json` files contain word frequency statistics and rankings.
- `.png` files contain the rendered word cloud graphical visualizations.
- Raw comments are stored in `data/` under `jsonl/` or `json/`.
