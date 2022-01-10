import json
import random
from uuid import uuid4

import pandas as pd
import streamlit as st

SIMILARITY = {
    'Not similar': 0,
    'Somewhat similar': 1,
    'Quite similar': 2,
    'Very similar': 3
}


def jamendo_url(track_id: int) -> str:
    return f'https://mp3d.jamendo.com/?trackid={track_id}&format=mp32'


def increment_progress(track_id: str, result: dict[str, str]) -> None:
    st.session_state['results'][track_id] = {k: SIMILARITY[v] for k, v in result.items()}
    st.session_state['progress'] += 1


def save_respose(df: pd.DataFrame) -> None:
    aws_path = st.secrets['AWS_PATH']
    aws_path += f'{uuid4()}.csv'
    df.to_csv(aws_path, storage_options={'anon': False})


def main():
    st.set_page_config(layout='wide')
    st.markdown('# Music similarity experiment')
    st.markdown('Welcome! Here the experiment is described')

    with open('data.json') as fp:
        data_all = json.load(fp)

    if 'progress' not in st.session_state:
        st.session_state['progress'] = 0
        st.session_state['results'] = {}
    progress = st.session_state['progress']

    st.progress(progress / len(data_all))
    if progress < len(data_all):
        data = data_all[progress]

        with st.form(key='form', clear_on_submit=True):
            st.markdown('### Reference track')
            st.audio(jamendo_url(data['reference']))

            results = {}
            columns = st.columns(len(data['options']))
            items = list(data['options'].items())
            random.shuffle(items)
            for i, (column, (key, track_ids)) in enumerate(zip(columns, items)):
                with column:
                    st.markdown(f'### Playlist #{i+1}')
                    for track_id in track_ids:
                        st.audio(jamendo_url(track_id))
                    results[key] = st.select_slider('Similar', options=SIMILARITY.keys(), key=key)

            st.form_submit_button(on_click=increment_progress, args=[data['reference'], results])

    else:
        df = pd.DataFrame(st.session_state['results'])
        df.sort_index(inplace=True)
        save_respose(df)
        st.markdown('Thanks for participating!')


if __name__ == '__main__':
    main()
