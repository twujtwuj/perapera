import pandas as pd
from datetime import datetime

# For testing purposes
NUMBER_OF_CARDS = 100

# Read JSON file with Pandas
def data_loader():
    kanji_df = pd.read_json("../data/kanji-kyouiku.json", orient="index")[:NUMBER_OF_CARDS]
    kanji_df.reset_index(inplace=True)
    kanji_df.rename(columns={"index": "kanji"}, inplace=True)
    cols = [
        "kanji",
        "strokes",
        "grade",
        "freq",
        "jlpt_new",
        "meanings",
        "readings_on",
        "readings_kun"
    ]
    kanji_df = kanji_df[cols]

    # Select the first element of the lists for meanings, readings_on, and readings_kun
    kanji_df["meanings"] = kanji_df["meanings"].apply(lambda x: x[0] if x else None)
    kanji_df["readings_on"] = kanji_df["readings_on"].apply(
        lambda x: x[0] if x else None
    )
    kanji_df["readings_kun"] = kanji_df["readings_kun"].apply(
        lambda x: x[0] if x else None
    )
    kanji_df["seen"] = False

    # 'Reset' the review
    kanji_df["prev_review"] = datetime.now().date()
    kanji_df["next_review"] = datetime.now().date()

    # Convert 'freq' column to integer
    kanji_df["freq"] = (
        pd.to_numeric(kanji_df["freq"], errors="coerce").fillna(0).astype(int)
    )
    return kanji_df