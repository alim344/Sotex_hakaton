import pandas as pd
import numpy as np
from sqlalchemy import text
from database import engine

def make_key(row):
    """
    Creates a unique string key to prevent collisions between 
    different types of IDs (Substation vs Transmission).
    """
    if pd.notnull(row['SsId']) and row['SsId'] != 0:
        return f"SS_{int(row['SsId'])}"
    elif pd.notnull(row['TsId']) and row['TsId'] != 0:
        return f"TS_{int(row['TsId'])}"
    return "NONE"

def run_database_cleanup():
    print("Loading db")
    df = pd.read_sql("SELECT * FROM dbo.Feeders11", engine)

    #0 with Nan    
    df['NameplateRating'] = df['NameplateRating'].replace(0, np.nan)
 
    
    df['PrivremeniKljuc'] = df.apply(make_key, axis=1)
 
   
    mask_has_group = df['PrivremeniKljuc'] != "NONE"
    
    df.loc[mask_has_group, 'NameplateRating'] = df.loc[mask_has_group, 'NameplateRating'].fillna(
        df[mask_has_group].groupby('PrivremeniKljuc')['NameplateRating'].transform('mean')
    )
 
    global_median = df['NameplateRating'].median()
    df['NameplateRating'] = df['NameplateRating'].fillna(global_median)
 
    print(f" Left NaN: {df['NameplateRating'].isna().sum()} ---")
 
    print("Update")
    with engine.begin() as conn:
        for _, row in df[['Id', 'NameplateRating']].iterrows():
            conn.execute(text("""
                UPDATE dbo.Feeders11
                SET NameplateRating = :rating
                WHERE Id = :id
            """), {
                "rating": float(row['NameplateRating']), 
                "id": int(row['Id'])
            })
 
    print("Upgrade done")

if __name__ == "__main__":
    run_database_cleanup()