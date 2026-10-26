// Refresh the local catalog and icons. Node 20+, tar; no npm dependencies.
// Usage: node scripts/update_item_icons.mjs [genshin-db version]
import {
  mkdir,
  readFile,
  writeFile,
  mkdtemp,
  rm,
  access,
  rename
} from 'node:fs/promises'
import { tmpdir } from 'node:os'
import { join, resolve } from 'node:path'
import { fileURLToPath } from 'node:url'
import { execFileSync } from 'node:child_process'

const version = process.argv[2] || '5.2.14'
if (!/^\d+\.\d+\.\d+$/.test(version))
  throw new Error('Expected a numeric package version')
const root = fileURLToPath(new URL('../', import.meta.url))
const output = resolve(root, 'frontend/public/icons/items')
const temp = await mkdtemp(join(tmpdir(), 'selfwishes-icons-'))
const catalog = {
  source: `https://github.com/theBowja/genshin-db (npm ${version})`,
  items: {},
  names: {}
}
async function download(url) {
  const response = await fetch(url, { signal: AbortSignal.timeout(30000) })
  if (!response.ok) throw new Error(`${response.status}: ${url}`)
  return Buffer.from(await response.arrayBuffer())
}
try {
  await mkdir(output, { recursive: true })
  await writeFile(
    join(temp, 'db.tgz'),
    await download(
      `https://registry.npmjs.org/genshin-db/-/genshin-db-${version}.tgz`
    )
  )
  execFileSync('tar', [
    '-xzf',
    join(temp, 'db.tgz'),
    '-C',
    temp,
    'package/src/min/data.min.json'
  ])
  const db = JSON.parse(
    await readFile(join(temp, 'package/src/min/data.min.json'), 'utf8')
  )
  const jobs = []
  for (const kind of ['characters', 'weapons']) {
    for (const [key, item] of Object.entries(db.data.English[kind])) {
      if (item.rarity < 3 || ['aether', 'lumine'].includes(key)) continue
      const image = db.image[kind][key]
      if (!/^UI_[A-Za-z0-9_]+$/.test(image?.filename_icon || '')) continue
      const url = `https://enka.network/ui/${image.filename_icon}.png`
      jobs.push({ kind, key, item, url })
    }
  }
  let failed = 0
  await Promise.all(
    Array.from({ length: 6 }, async () => {
      while (jobs.length) {
        const { kind, key, item, url } = jobs.shift()
        const id = String(item.id)
        const path = join(output, `${id}.png`)
        try {
          try {
            await access(path)
          } catch {
            const bytes = await download(url)
            if (
              !bytes
                .subarray(0, 8)
                .equals(Buffer.from([137, 80, 78, 71, 13, 10, 26, 10]))
            )
              throw new Error('Not a PNG')
            await writeFile(`${path}.tmp`, bytes)
            await rename(`${path}.tmp`, path)
          }
          catalog.items[id] = id
          catalog.names[item.name.toLowerCase()] = id
          // Older imports may lack an item ID; support all catalog translations.
          for (const language of Object.values(db.data)) {
            const name = language[kind]?.[key]?.name
            if (name) catalog.names[name.toLowerCase()] = id
          }
        } catch (error) {
          failed++
          console.warn(`Icon ${id} (${item.name}): ${error.message}`)
        }
      }
    })
  )
  const previousPath = resolve(root, 'frontend/src/catalog/item-icons.json')
  // Keep known images when a refresh temporarily cannot reach an upstream asset.
  let previous = { items: {}, names: {} }
  try {
    previous = JSON.parse(await readFile(previousPath, 'utf8'))
  } catch {}
  catalog.items = Object.fromEntries(
    Object.entries({ ...previous.items, ...catalog.items }).sort(
      ([a], [b]) => Number(a) - Number(b)
    )
  )
  catalog.names = Object.fromEntries(
    Object.entries({ ...previous.names, ...catalog.names }).sort(([a], [b]) =>
      a.localeCompare(b)
    )
  )
  await mkdir(resolve(root, 'frontend/src/catalog'), { recursive: true })
  await writeFile(previousPath, JSON.stringify(catalog) + '\n')
  console.log(
    `Saved ${Object.keys(catalog.items).length} local icons; ${failed} unavailable (UI uses fallback).`
  )
} finally {
  await rm(temp, { recursive: true, force: true })
}
