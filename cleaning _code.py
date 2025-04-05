import pandas as pd
import re
import numpy as np
from scipy.stats import zscore

# function to read csv files 
def load_csv(file_path):
    try:
        df = pd.read_csv(file_path, dtype=str)
        print(f"CSV file '{file_path}' loaded successfully.")
        return df
    except Exception as e:
        print("Error occurred:", e)
        return None
    
# function to convert duration into total number of minutes 
def duration_to_minutes(duration):
    time = duration.split('h')
    hours = int(time[0])
    minutes = int(time[1].replace('m', '').strip()) 
    total_minutes = hours * 60 + minutes
    return total_minutes

# dunction to clean prices and convert them to numeric values 
def clean_price_column(series):
    def convert_value(x):
        x = str(x).strip()
        x = re.sub(r'[$,]', '', x)  
        try:
            return float(x)
        except ValueError:
            return None  
    return series.apply(convert_value)

# function to convert stops to numbers 
def convert_stops(Transit):
    if pd.isna(Transit):
        return 0
    match = re.search(r'(\d+)', Transit)
    return int(match.group(1)) if match else 0

# function to add a new column for seasons based on Departure 
def get_season(date_str):
    try:
        month = pd.to_datetime(date_str).month
        if month in [12, 1, 2]:
            return 'Winter'
        elif month in [3, 4, 5]:
            return 'Spring'
        elif month in [6, 7, 8]:
            return 'Summer'
        else:
            return 'Autumn'
    except:
        return None
    
# function to determine the type of flight based on its Duration 
def categorize_duration(df):
    min_duration = df['Duration in Minutes'].min()
    max_duration = df['Duration in Minutes'].max()
    avg_duration = df['Duration in Minutes'].mean()
    df['Flight Type'] = df['Duration in Minutes'].apply(
        lambda minutes: 'Short' if minutes < avg_duration * 0.8
        else 'Medium' if avg_duration * 0.8 <= minutes <= avg_duration * 1.2
        else 'Long'
    )
    return df

# function to determine type of Price 
def categorize_price(df):
  min_price = df['Price'].min()
  max_price = df['Price'].max()
  avg_price = df['Price'].mean()
  df['Price Type'] = df['Price'].apply(
      lambda price: 'Cheap' if price < avg_price * 0.8
        else 'Affordable' if avg_price * 0.8 <= price <= avg_price * 1.2
        else 'Expensive' 
  )
  return df

# function to clean Competitor Price outliers
def clean_competitor_price_outliers(df, z_thresh=3):
    df = df.copy()
    df['Competitor Price'] = df['Competitor Price'].apply(
        lambda x: np.nan if x in [0, 1, 2, 3, 4, 5, 6, 7, 0.0, 1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0] else x
    )
    df['Price_Diff'] = df['Price'] - df['Competitor Price']
    df['Z_Score'] = zscore(df['Price_Diff'].fillna(0))
    non_outlier_mask = df['Z_Score'].abs() <= z_thresh
    mean_diff = df.loc[non_outlier_mask, 'Price_Diff'].mean()
    fix_mask = (df['Z_Score'].abs() > z_thresh) | (df['Competitor Price'].isna())
    df.loc[fix_mask, 'Competitor Price'] = round(
        df.loc[fix_mask, 'Price'] - mean_diff, 2
    )
    df.drop(['Price_Diff', 'Z_Score'], axis=1, inplace=True)
    return df


# function to save the cleaned DataFrame to a new CSV file 
def save_to_csv(df, file_path):
    try:
        df.to_csv(file_path, index=False)
        print(f"Data has been successfully saved to '{file_path}'")
    except Exception as e:
        print("Error occurred while saving the file:", e)

def cleaning(df):
    # dropping duplicates
    df = df.drop_duplicates()

    # clean price, competitor price, duration, transit
    df['Price'] = clean_price_column(df['Price'])
    df['Competitor Price'] = clean_price_column(df['Competitor Price'])
    df['Duration in Minutes'] = df['Duration'].apply(duration_to_minutes)
    df['Transit'] = df['Transit'].apply(convert_stops)

    # convert to numeric
    df['Price'] = pd.to_numeric(df['Price'], errors='coerce')
    df['Competitor Price'] = pd.to_numeric(df['Competitor Price'], errors='coerce')
    df['Duration in Minutes'] = pd.to_numeric(df['Duration in Minutes'], errors='coerce')

    # clean competitor price outliers
    df = clean_competitor_price_outliers(df)

    # add flight type, price type, season columns
    df = categorize_duration(df)
    df = categorize_price(df)
    df['Season'] = df['Departure'].apply(get_season)
    df['Price per Hour'] = round(df['Price'] / (df['Duration in Minutes'] / 60), 2)

    return df


# file paths
input_output_files = {
    "LAX_BEI.csv": "LAX_BEI_cleaned.csv",
    "Paris_scrape.csv": "Paris_cleaned.csv",
    "Riyadh_scrape.csv": "Riyadh_cleaned.csv"
}

# processing each file
for input_file, output_file in input_output_files.items():
    df = load_csv(input_file)
    if df is not None:
        df_cleaned = cleaning(df)
        if df_cleaned is not None:
            save_to_csv(df_cleaned, output_file)