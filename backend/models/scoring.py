def compute_block_scores(results, top_k=3):
    block_scores = {}

    for item in results:
        block = item["block_id"]
        sim = float(item.get("similarity", 0.0))
        block_scores.setdefault(block, []).append(sim)

    averaged = {}
    for block, vals in block_scores.items():
        if not vals:
            continue   
        top_vals = sorted(vals, reverse=True)[:top_k]
        averaged[block] = sum(top_vals) / len(top_vals)
    

    return averaged
