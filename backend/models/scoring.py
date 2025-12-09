def compute_block_scores(results):
    block_scores = {}

    for item in results:
        block = item["block_id"]
        sim = item["similarity"]
        block_scores.setdefault(block, []).append(sim)

    averaged = {
        block: round(sum(vals)/len(vals), 3)
        for block, vals in block_scores.items()
    }

    return averaged
