def compute_block_scores(results):
    block_scores = {}

    for item in results:
        block = item["block_id"]
        sim = float(item.get("similarity", 0.0))
        block_scores.setdefault(block, []).append(sim)

    # ✅ moyenne simple, sans arrondi prématuré
    averaged = {
        block: sum(vals) / len(vals)
        for block, vals in block_scores.items()
        if vals
    }

    return averaged
