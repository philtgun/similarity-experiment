import argparse
import logging
import os
from pathlib import Path
from typing import Optional

import pandas as pd
import s3fs
import toml
from tqdm import tqdm

SECRETS_FILE = Path('.streamlit/secrets.toml')


def process_results(output_file: Path) -> None:
    secrets = toml.load(SECRETS_FILE)
    for key, value in secrets.items():
        os.environ[key] = value
    fs = s3fs.S3FileSystem(anon=False)
    df_all: Optional[pd.DataFrame] = None
    total = 0
    for csv_file in tqdm(fs.listdir(secrets['AWS_PATH'])):
        if csv_file['size'] > 0:
            df = pd.read_csv('s3://' + csv_file['name'], index_col=0)
            if df_all is None:
                df_all = df
            else:
                df_all += df
            total += 1

    if df_all is None:
        logging.warning('No data on AWS!')
        return

    df_all /= total
    output_file.parent.mkdir(exist_ok=True)
    df_all.to_csv(output_file, float_format='%.4f')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('output_file', type=Path, help='output csv file')
    args = parser.parse_args()
    process_results(**vars(args))
