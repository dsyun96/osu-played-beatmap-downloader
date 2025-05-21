import requests
import os
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

s = requests.Session()
s.cookies.set('osu_session', '...')

os.makedirs('beatmap', exist_ok=True)

def download_map(it, max_retries=3):
    bid = it['beatmap']['beatmapset_id']
    title = it['beatmapset']['title'].replace('/', '_').replace('?', '')
    artist = it['beatmapset']['artist'].replace('/', '_').replace('?', '')
    filename = f'{bid} {artist} - {title}.osz'
    filepath = f'beatmap/{filename}'

    for attempt in range(1, max_retries + 1):
        try:
            if os.path.isfile(filepath):
                return True, f'Passed... {filename}', it

            res = requests.get(f'https://beatconnect.io/b/{bid}', stream=True, timeout=10)
            res.raise_for_status()

            with open(filepath, 'wb') as f:
                for chunk in res.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)

            return True, f'Done! {filename}', it
        except Exception as e:
            if attempt < max_retries:
                time.sleep(2 * attempt)
            else:
                return False, f'Failed after {max_retries} attempts: {filename} ({e})', it

offset = 0
executor = ThreadPoolExecutor(max_workers=10)
failed_maps = []

while True:
    res = s.get(f'https://osu.ppy.sh/users/1262919/beatmapsets/most_played?limit=100&offset={offset}')
    if not res or not res.content:
        break

    data = res.json()
    if not data:
        break

    futures = [executor.submit(download_map, it) for it in data]
    for future in as_completed(futures):
        success, msg, it = future.result()
        if not msg.startswith('Passed'):
            print(offset, msg)
        offset += 1
        if not success:
            failed_maps.append(it)

