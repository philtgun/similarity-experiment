import json
import random
from datetime import datetime
from typing import Optional

import pandas as pd
import streamlit as st

SIMILARITY = {
    'Not similar': 0,
    'Somewhat similar': 1,
    'Quite similar': 2,
    'Very similar': 3
}

DESCRIPTION = """
⚠ Please use Firefox or Chrome browser for this experiment, as Safari have been reported to have some issues.

👋 Welcome! This experiment should take around 20 minutes of your time. Please use the device with a big screen if you
can, it would be easier to do the experiment. This survey contains a completion code for SurveySwap.io

📢 Please read the following instructions carefully
and **don't reload the page** until you are finished, or you will lose your progress.

📃 You will be presented with a reference track and 5 playlists of 4 tracks that are suggested based on the reference
track. **You don't need to listen to each track for the full duration**, by default you would be presented with
15-second segment from each track. You can continue listening or skip around by using the controls of the audio player
to get a better understanding if you feel that 15 seconds is not enough. However,
please listen to the reference track and each track from the playlist **just enough** to understand the nature of
each track.

⚠ If the audio widgets are too short for the controls to be comfortably used, please zoom out the webpage with the
help of your browser.

🎯 There are 4 reference tracks in total, your overall progress is indicated by the progress bar under these
instructions.

⏳ Please **don't think too much** about the answers or spend too much time on each track, answer intuitively by
adjusting the rating to that which feels right after familiarizing yourself with every track from a playlist.
Don't forget that there are no wrong answers.

⭐ For each playlist,
please rate its similarity **to the reference track** on the 4-point scale from _"not similar"_ to _"very similar"_
as if the playlist is presented to you in the following context:

### If you liked how this track sounds, you might like these other tracks
"""

END_MESSAGE = """
### Thanks for participating!

Please answer a few background questions that should only take 3 minutes of your time:
[https://forms.gle/JM5meAHhiafsBwvx5](https://forms.gle/JM5meAHhiafsBwvx5)
"""

LETTERS = ['A', 'B', 'C', 'D']


def jamendo_url(track_id: int) -> str:
    return f'https://mp3d.jamendo.com/?trackid={track_id}&format=mp32#t=30,45'


def save_respose(df: pd.DataFrame) -> None:
    print(df)
    aws_path = st.secrets['AWS_PATH']
    aws_path += f'{datetime.now()}.csv'
    df.to_csv(aws_path, storage_options={'anon': False})


def save_answer(keys: list[str], track_id: int, total: int) -> None:
    st.session_state['progress'] += 1
    results: dict[str, Optional[int]]
    if st.session_state['skip']:
        results = {k: None for k in keys}
    else:
        results = {k: SIMILARITY[st.session_state[k]] for k in keys}
    st.session_state['results'][track_id] = results

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
            st.markdown(f'### Reference track {LETTERS[progress]}')
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

            st.checkbox('I am not very familiar with this genre (skip)', key='skip',
                        help='Only tick this checkbox if you have ***zero*** idea on how to rate the playlists, '
                             'and you will skip this track')
            st.form_submit_button(on_click=save_answer, args=[keys, reference_track_id, total])
    else:
        st.balloons()
        st.markdown(END_MESSAGE)


if __name__ == '__main__':
    main()
