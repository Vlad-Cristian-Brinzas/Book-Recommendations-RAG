import re
from book_api.persistence import get_db_connection

COSTS_PER_1M_TOKENS = {
    "gpt-4.1-nano": {
        "regular": {
            "uncached_input": 0.10,
            "cached_input": 0.025,
            "output": 0.40,
        },
        "batch": {
            "uncached_input": 0.05,
            "output": 0.20,
        }
    },
    "text-embedding-3-small": {
        "regular": {
            "uncached_input": 0.02,
        },
        "batch": {
            "uncached_input": 0.01,
        }
    }
}
CURRENCY = "USD"


def compute_costs():
    """
    Computes the total costs for all responses stored in the database.

    :return: A dictionary containing the breakdown of costs for each model.
    :rtype: dict
    """
    costs = {}
    # In the end, want costs to look something like:
    # {
    #     "gpt-4.1-nano": {
    #           "regular": {
    #               "uncached_input": 1.70,
    #               "cached_input": 3.075,
    #               "nonreasoning_output": 6.80,
    #               "total": 11.575,
    #           },
    #           "batch": {
    #               "uncached_input": 0.85,
    #               "nonreasoning_output": 2.20,
    #               "total": 3.05,
    #           },
    #           "total": 14.625,
    #     },
    #     "text-embedding-3-small": {
    #           "regular": {
    #               "uncached_input": 0.34,
    #               "total": 0.34,
    #           },
    #           "batch": {
    #               "uncached_input": 1.41,
    #               "total": 1.41,
    #           },
    #           "total": 1.75,
    #     },
    #     ... (other models)
    #     "total": 16.375,
    # }
    errors = []

    with get_db_connection() as conn:
        # Group by model and batch type
        cursor = conn.cursor()
        cursor.execute('''
        SELECT model, batch,
               SUM(uncached_input_tokens),
               SUM(cached_input_tokens),
               SUM(reasoning_output_tokens),
               SUM(nonreasoning_output_tokens)
        FROM responses
        GROUP BY model, batch
        ''')
        rows = cursor.fetchall()
        # If lots of rows, might prefer fetching them in chunks
        # But for this small app, fetching all at once is fine
        for row in rows:
            (model, batch, uncached_input_tokens, cached_input_tokens,
                reasoning_output_tokens, nonreasoning_output_tokens) = row
            tier = "batch" if batch else "regular"

            # Model names get persisted with full datestamp
            # (e.g. "gpt-4.1-nano-2025-04-14")
            # So we need to strip the datestamp at least
            datestamp_pattern = r"-\d{4}-\d{2}-\d{2}$"
            model = re.sub(datestamp_pattern, "", model)
            # If no datestamp, model will be unchanged

            # Log errors if we don't have costs for this model + batch type
            if model not in COSTS_PER_1M_TOKENS:
                # Will print twice if we have batch and regular for same model
                # Not ideal, but not a big deal
                errors.append(f"{model}: no costs defined")
                continue
            if tier not in COSTS_PER_1M_TOKENS[model]:
                errors.append(f"{model}: no {tier} costs defined")
                continue

            # Otherwise, query already summed up most of the data we need
            # First compute, then store
            def cost_for_tokens(tokens, cost_per_million):
                return (tokens / 1_000_000) * cost_per_million
            pricing = COSTS_PER_1M_TOKENS[model][tier]

            uncached_input_cost = cost_for_tokens(
                uncached_input_tokens, pricing.get("uncached_input", 0)
            )
            cached_input_cost = cost_for_tokens(
                cached_input_tokens, pricing.get("cached_input", 0)
            )
            nonreasoning_output_cost = cost_for_tokens(
                nonreasoning_output_tokens, pricing.get("output", 0)
            )
            reasoning_output_cost = cost_for_tokens(
                reasoning_output_tokens, pricing.get("output", 0)
            )
            total_cost = (
                uncached_input_cost + cached_input_cost +
                nonreasoning_output_cost + reasoning_output_cost
            )

            # Store the costs in the dictionary
            if model not in costs:
                costs[model] = {}

            tier_costs = {}
            if uncached_input_cost:
                tier_costs["uncached_input"] = uncached_input_cost
            if cached_input_cost:
                tier_costs["cached_input"] = cached_input_cost
            if nonreasoning_output_cost:
                tier_costs["nonreasoning_output"] = nonreasoning_output_cost
            if reasoning_output_cost:
                tier_costs["reasoning_output"] = reasoning_output_cost
            tier_costs["total"] = total_cost
            # No need to check for total - if the query returned data,
            # it means we have at least one cost.

            costs[model][tier] = tier_costs

        # Once dictionary is populated, compute per-model and overall total
        big_total = 0
        for model, batch_types in costs.items():
            model_total = sum(
                batch_type.get("total", 0)
                for batch_type in batch_types.values()
            )
            # If we have no costs for this model, it will be 0
            # But we still want to add it to the overall total
            big_total += model_total
            batch_types["total"] = model_total
        costs["total"] = big_total

    # Print errors if any
    if errors:
        print("[ERROR] Some costs could not be computed:")
        for error in errors:
            print(f"  - {error}")

    return costs


if __name__ == "__main__":
    # If run as a script, compute and print costs
    costs = compute_costs()

    def non_total_items(dict):
        return (
            (key, value) for (key, value) in dict.items() if key != "total"
        )

    print("Costs breakdown:")
    for model, batch_options in non_total_items(costs):
        if model == "total":
            continue  # Overall total at the end

        print(f"{model}:")
        for tier, tier_costs in non_total_items(batch_options):
            if tier == "total":
                continue  # Total has no subitems

            print(f"  {tier}:")
            for cost_type, cost_value in non_total_items(tier_costs):
                if cost_type == "total":
                    continue

                print(f"    {cost_type}: {cost_value:.6f} {CURRENCY}")
            print(f"    total: {tier_costs['total']:.6f} {CURRENCY}")
        print(f"  model total: {batch_options['total']:.6f} {CURRENCY}")
    print(f"Overall total: {costs['total']:.6f} {CURRENCY}")
