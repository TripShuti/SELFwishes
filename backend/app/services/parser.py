from collections import defaultdict

from app.config import UIGF_MERGE, GACHA_TYPES, STANDARD_5_CHARS, PITY_HARD_5, PITY_HARD_4, GACHA_TYPE_ORDER


def merge_and_sort_wishes(raw_wishes: dict[str, list[dict]]) -> dict[str, list[dict]]:
    merged: dict[str, list[dict]] = {}
    for raw_type, items in raw_wishes.items():
        uigf_type = UIGF_MERGE.get(raw_type, raw_type)
        if uigf_type not in merged:
            merged[uigf_type] = []
        merged[uigf_type].extend(items)

    for uigf_type in merged:
        merged[uigf_type].sort(key=lambda w: (w["time"], w["id"]))

    return merged


def calc_pity(wishes: list[dict], uigf_type: str) -> list[dict]:
    hard_5 = PITY_HARD_5.get(uigf_type, 90)
    hard_4 = PITY_HARD_4.get(uigf_type, 10)

    counter_5 = 0
    counter_4 = 0
    pull_num = 0

    last_was_loss = False

    for w in wishes:
        rarity = int(w["rank_type"])
        pull_num += 1
        counter_5 += 1
        counter_4 += 1

        w["pull_count"] = pull_num
        w["pity_5"] = counter_5
        w["pity_4"] = counter_4
        w["is_5050_win"] = None
        w["is_guaranteed"] = False

        if rarity == 5:
            w["pity_5"] = counter_5
            counter_5 = 0

            if uigf_type == "301":
                is_standard = w["name"] in STANDARD_5_CHARS
                if last_was_loss:
                    w["is_guaranteed"] = True
                    w["is_5050_win"] = None
                    last_was_loss = False
                else:
                    w["is_guaranteed"] = False
                    if is_standard:
                        w["is_5050_win"] = False
                        last_was_loss = True
                    else:
                        w["is_5050_win"] = True
                        last_was_loss = False

        if rarity == 4:
            w["pity_4"] = counter_4
            counter_4 = 0

        if rarity == 5:
            counter_4 = 0

    return wishes


def dedup_wishes(
    existing_ids: set[str], new_wishes: list[dict]
) -> tuple[list[dict], int]:
    deduped = []
    new_count = 0
    for w in new_wishes:
        wid = str(w.get("id", ""))
        if wid not in existing_ids:
            deduped.append(w)
            new_count += 1
    return deduped, new_count


def recalc_pity_batch(wishes: list[dict], uigf_type: str) -> list[dict]:
    last_was_loss = False
    counter_5 = 0
    counter_4 = 0

    for w in wishes:
        rarity = int(w["rank_type"])
        counter_5 += 1
        counter_4 += 1

        w["pity_5"] = counter_5
        w["pity_4"] = counter_4
        w["is_5050_win"] = None
        w["is_guaranteed"] = False

        if rarity == 5:
            w["pity_5"] = counter_5
            counter_5 = 0

            if uigf_type == "301":
                is_standard = w["name"] in STANDARD_5_CHARS
                if last_was_loss:
                    w["is_guaranteed"] = True
                    w["is_5050_win"] = None
                    last_was_loss = False
                else:
                    w["is_guaranteed"] = False
                    if is_standard:
                        w["is_5050_win"] = False
                        last_was_loss = True
                    else:
                        w["is_5050_win"] = True
                        last_was_loss = False

        if rarity == 4:
            w["pity_4"] = counter_4
            counter_4 = 0

        if rarity == 5:
            counter_4 = 0

    return wishes


def parse_into_db_rows(
    account_id: int,
    gacha_type: str,
    wishes: list[dict],
) -> list[dict]:
    rows = []
    for w in wishes:
        rows.append(
            {
                "account_id": account_id,
                "gacha_type": w.get("gacha_type", gacha_type),
                "uigf_gacha_type": UIGF_MERGE.get(str(w.get("gacha_type", gacha_type)), str(w.get("gacha_type", gacha_type))),
                "item_id": w.get("item_id", ""),
                "item_name": w["name"],
                "item_type": w.get("item_type", ""),
                "rarity": int(w["rank_type"]),
                "timestamp": w["time"],
                "wish_id": w["id"],
                "pull_count": w.get("pull_count", 0),
                "pity_5": w.get("pity_5"),
                "pity_4": w.get("pity_4"),
                "is_5050_win": w.get("is_5050_win"),
                "is_guaranteed": w.get("is_guaranteed"),
            }
        )
    return rows
