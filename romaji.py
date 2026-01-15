def _hiragana_to_romaji(self, mora):
    """FIX: Reverse lookup using your HIRAGANA_MAP"""
    reverse_map = {v: k for k, v in self.hiragana_map.items()}
    return reverse_map.get(mora, mora)
