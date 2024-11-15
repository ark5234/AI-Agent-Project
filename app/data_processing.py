import pandas as pd

def process_data_from_csv(uploaded_file):
    """Reads CSV data from the uploaded file and processes it into a DataFrame."""
    try:
        df = pd.read_csv(uploaded_file)
        return df
    except Exception as e:
        raise ValueError(f"Error processing CSV file: {e}")
