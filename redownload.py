import requests
import os
import re


base_dir = '.'
numbers = []
pattern = re.compile(r'^(\d+)')

for folder_name in os.listdir(base_dir):
    full_path = os.path.join(base_dir, folder_name)
    if os.path.isdir(full_path):
        match = pattern.match(folder_name)
        if match:
            number = int(match.group(1))
            numbers.append(number)


for bid in numbers:
    res = requests.get(f'https://beatconnect.io/b/{bid}', stream=True, timeout=30)
    res.raise_for_status()

    filepath = res.headers['Content-Disposition'][21:-2]

    with open(filepath, 'wb') as f:
        for chunk in res.iter_content(chunk_size=8192):
            if chunk:
                f.write(chunk)

        print(f'Done! {filepath}')
