import pandas as pd
import numpy as np
from sqlalchemy import text
from database import engine


def make_key(row):
    if pd.notnull(row['SsId']) and row['SsId'] != 0:
        return f"SS_{int(row['SsId'])}"
    elif pd.notnull(row['TsId']) and row['TsId'] != 0:
        return f"TS_{int(row['TsId'])}"
    return None


def run_database_cleanup():
    df = pd.read_sql("SELECT * FROM dbo.Feeders11", engine)
    
    df['NameplateRating'] = df['NameplateRating'].replace(0, np.nan)
 
    temp_key = df['SsId'].replace(0, np.nan).fillna(df['TsId'])
    df['PrivremeniKljuc'] = temp_key.fillna(-1).astype(int).astype(str)
 
    df['NameplateRating'] = df['NameplateRating'].fillna(
        df.groupby('PrivremeniKljuc')['NameplateRating'].transform('mean')
    )
 
    global_median = df['NameplateRating'].median()
    df['NameplateRating'] = df['NameplateRating'].fillna(global_median)
 
    print(f"--- 2. Logika primenjena. Preostalo NaN: {df['NameplateRating'].isna().sum()} ---")
 
    with engine.begin() as conn:
        for _, row in df[['Id', 'NameplateRating']].iterrows():
            conn.execute(text("""
                UPDATE dbo.Feeders11
                SET NameplateRating = :rating
                WHERE Id = :id
            """), {"rating": float(row['NameplateRating']), "id": int(row['Id'])})
 
    print("--- 3. Baza uspešno ažurirana! ---")


if __name__ == "__main__":
    run_database_cleanup()