import os
import tempfile
import unittest

import httpx

_data = tempfile.TemporaryDirectory()
os.environ['DATA_DIR'] = _data.name

from app.database import Base, engine, async_session
from app.main import app
from app.models import Account, Wish


class WishFilterTests(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        async with engine.begin() as connection:
            await connection.run_sync(Base.metadata.drop_all)
            await connection.run_sync(Base.metadata.create_all)
        async with async_session() as db:
            db.add_all([Account(id=1, name='Main'), Account(id=2, name='Alt')])
            await db.flush()
            for i, (account, name, rarity, banner) in enumerate([
                (1, 'Emerald Orb', 3, '200'), (1, 'The Widsith', 4, '301'),
                (1, 'Arlecchino', 5, '301'), (1, '100% Sword', 3, '200'),
                (2, 'Emerald Orb', 3, '200'),
            ]):
                db.add(Wish(account_id=account, wish_id=str(i), item_id=str(14000+i),
                            item_name=name, item_type='Weapon', rarity=rarity,
                            gacha_type=banner, uigf_gacha_type=banner,
                            timestamp=f'2026-10-01 10:00:0{i}', pull_count=i))
            await db.commit()
        self.client = httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url='http://test')

    async def asyncTearDown(self):
        await self.client.aclose()
        await engine.dispose()

    async def test_search_is_case_insensitive_scoped_and_exposes_id(self):
        response = await self.client.get('/api/wishes', params={'account_id': 1, 'search': '  EMERALD '})
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['total'], 1)
        self.assertEqual(data['items'][0]['item_id'], '14000')

    async def test_combined_filters_and_pagination_count(self):
        response = await self.client.get('/api/wishes', params={
            'account_id': 1, 'gacha_type': '301', 'rarity': 4, 'search': 'wid', 'size': 1,
        })
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['total'], 1)
        self.assertEqual(response.json()['items'][0]['item_name'], 'The Widsith')
        response = await self.client.get('/api/wishes', params={'account_id': 1, 'size': 2, 'page': 2})
        self.assertEqual(response.json()['total'], 4)
        self.assertEqual(len(response.json()['items']), 2)

    async def test_search_treats_sql_wildcards_literally(self):
        response = await self.client.get('/api/wishes', params={'account_id': 1, 'search': '%'})
        self.assertEqual(response.json()['total'], 1)
        self.assertEqual(response.json()['items'][0]['item_name'], '100% Sword')

    async def test_invalid_rarity_and_missing_account(self):
        self.assertEqual((await self.client.get('/api/wishes?account_id=1&rarity=9')).status_code, 422)
        self.assertEqual((await self.client.get('/api/wishes?account_id=999')).status_code, 404)
