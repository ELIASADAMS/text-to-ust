def _hiragana_to_romaji(self, mora):
    """Reverse lookup using HIRAGANA_MAP"""
    reverse_map = {v: k for k, v in self.hiragana_map.items()}
    return reverse_map.get(mora, mora)
