import asyncio
from urllib.parse import urlparse, parse_qs

import httpx

from app.config import HOYO_BASE_URL, HOYO_PAGE_SIZE, HOYO_REQUEST_DELAY, GACHA_TYPES


class HoyoAPIError(Exception):
    pass


def parse_auth_url(url: str) -> dict:
    if urlparse(url).scheme not in ("http", "https"):
        raise HoyoAPIError("Invalid URL")

    parsed = urlparse(url)
    query = parse_qs(parsed.query)

    authkey = query.get("authkey", [None])[0]
    if not authkey:
        raise HoyoAPIError("No authkey found in URL")

    region = query.get("region", [None])[0]
    game_biz = query.get("game_biz", [None])[0]
    lang = query.get("lang", ["en"])[0]

    # The pasted URL only provides parameters; never send keys to its host.
    if game_biz not in (None, "hk4e_global", "hk4e_cn"):
        raise HoyoAPIError("This is not a Genshin Impact history URL")
    chinese = game_biz == "hk4e_cn" or parsed.hostname in (
        "hk4e-api.mihoyo.com", "public-operation-hk4e.mihoyo.com",
        "webstatic.mihoyo.com", "operation-webstatic.mihoyo.com",
    )
    base_url = ("https://public-operation-hk4e.mihoyo.com/gacha_info/api/getGachaLog"
                if chinese else HOYO_BASE_URL)

    return {
        "authkey": authkey,
        "region": region,
        "game_biz": game_biz,
        "lang": lang,
        "base_url": base_url,
    }


async def fetch_gacha_page(
    client: httpx.AsyncClient,
    authkey: str,
    gacha_type: str,
    page: int,
    end_id: str = "0",
    region: str | None = None,
    lang: str = "en",
    base_url: str | None = None,
    game_biz: str | None = None,
) -> dict:
    params = {
        "authkey_ver": "1",
        "sign_type": "2",
        "auth_appid": "webview_gacha",
        "init_type": gacha_type,
        "lang": lang,
        "authkey": authkey,
        "gacha_type": gacha_type,
        "page": str(page),
        "size": str(HOYO_PAGE_SIZE),
        "end_id": end_id,
    }
    if region:
        params["region"] = region
    if game_biz:
        params["game_biz"] = game_biz

    api_url = base_url or HOYO_BASE_URL
    try:
        resp = await client.get(api_url, params=params, timeout=30)
    except httpx.HTTPError:
        raise HoyoAPIError("Cannot reach the wish history API. Try again later.") from None

    if resp.status_code != 200:
        raise HoyoAPIError(f"API returned status {resp.status_code}")

    try:
        data = resp.json()
    except Exception:
        raise HoyoAPIError("Invalid wish history API response") from None

    if data.get("retcode") != 0:
        raise HoyoAPIError(f"Wish history API rejected the request (code {data.get('retcode')}). "
                           "Try again or reconnect your HoYoverse account.")

    result = data.get("data")
    if not result:
        raise HoyoAPIError("Empty response data")

    return result


async def fetch_all_wishes(
    authkey: str,
    gacha_type: str,
    region: str | None = None,
    lang: str = "en",
    base_url: str | None = None,
    game_biz: str | None = None,
    on_progress=None,
    existing_ids: set[str] | None = None,
) -> list[dict]:
    all_wishes = []
    page = 1
    end_id = "0"

    async with httpx.AsyncClient() as client:
        while True:
            result = await fetch_gacha_page(
                client, authkey, gacha_type, page, end_id, region, lang, base_url, game_biz
            )
            items = result.get("list", [])
            if not items:
                break

            region = region or result.get("region", region)

            encountered_existing = False
            for item in items:
                if existing_ids is not None and str(item["id"]) in existing_ids:
                    encountered_existing = True
                    break
                item["gacha_type"] = str(item.get("gacha_type", gacha_type))
                item["region"] = region
                all_wishes.append(item)

            if on_progress:
                on_progress(gacha_type, page, len(items))

            if encountered_existing:
                break
            next_id = items[-1]["id"]
            if next_id == end_id:
                raise HoyoAPIError("Wish history pagination did not advance. Try again later.")
            end_id = next_id
            page += 1
            await asyncio.sleep(HOYO_REQUEST_DELAY)

    return all_wishes


async def fetch_config_list(
    authkey: str, region: str | None = None, lang: str = "en"
) -> list[dict]:
    try:
        config_url = HOYO_BASE_URL.replace("getGachaLog", "getConfigList")
        params = {
            "authkey_ver": "1",
            "sign_type": "2",
            "auth_appid": "webview_gacha",
            "lang": lang,
            "authkey": authkey,
        }
        if region:
            params["region"] = region

        async with httpx.AsyncClient() as client:
            resp = await client.get(config_url, params=params, timeout=30)
            data = resp.json()

        if data.get("retcode") == 0:
            config_list = data.get("data", {}).get("gacha_type_list", [])
            if config_list:
                return config_list
    except Exception:
        pass

    return [{"key": k, "name": v} for k, v in GACHA_TYPES.items()]
