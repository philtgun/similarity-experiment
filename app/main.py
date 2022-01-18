import json
import random
from datetime import datetime

import pandas as pd
import streamlit as st

SIMILARITY = {
    'Not similar': 0,
    'Somewhat similar': 1,
    'Quite similar': 2,
    'Very similar': 3
}

DESCRIPTION = """
Welcome! This experiment should take around 15 minutes of your time. Please don't reload the page until you are
finished, or you will lose your progress.

You will be presented with a reference track and 5 playlists of 4 tracks that are suggested based on the reference
track. Please listen to the reference track and each playlist enough to understand the nature of each track.
For each playlist,
please rate its similarity to the reference track on the scale from "not similar" to "very similar" as if
the playlist is being recommended to you in the "if you liked this track, you might like these other tracks" context.
"""


def jamendo_url(track_id: int) -> str:
    return f'https://mp3d.jamendo.com/?trackid={track_id}&format=mp32'


def save_respose(df: pd.DataFrame) -> None:
    print(df)
    aws_path = st.secrets['AWS_PATH']
    aws_path += f'{datetime.now()}.csv'
    df.to_csv(aws_path, storage_options={'anon': False})


def save_answer(keys: list[str], track_id: int, total: int) -> None:
    st.session_state['progress'] += 1
    st.session_state['results'][track_id] = {k: SIMILARITY[st.session_state[k]] for k in keys}

    if st.session_state['progress'] == total:
        df = pd.DataFrame(st.session_state['results'])
        df.sort_index(inplace=True)
        save_respose(df)


def main():
    st.set_page_config(layout='wide')
    st.markdown('# Music similarity experiment')
    st.markdown(DESCRIPTION)

    with open('data.json') as fp:
        data_all = json.load(fp)

    if 'progress' not in st.session_state:
        st.session_state['progress'] = 0
        st.session_state['results'] = {}
    progress = st.session_state['progress']

    total = len(data_all)
    st.progress(progress / total)
    if progress < total:
        data = data_all[progress]
        reference_track_id = data['reference']

        with st.form(key='form', clear_on_submit=True):
            st.markdown('### Reference track')
            st.audio(jamendo_url(reference_track_id))

            keys = data['options'].keys()
            columns = st.columns(len(data['options']))
            items = list(data['options'].items())
            random.shuffle(items)
            for i, (column, (key, track_ids)) in enumerate(zip(columns, items)):
                with column:
                    st.markdown(f'### Playlist #{i+1}')
                    for track_id in track_ids:
                        st.audio(jamendo_url(track_id))
                    st.select_slider('How similar?', options=SIMILARITY.keys(), key=key)

            st.form_submit_button(on_click=save_answer, args=[keys, reference_track_id, total])
    else:
        st.balloons()
        st.markdown('### Thanks for participating!')


if __name__ == '__main__':
    main()
