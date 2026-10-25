import pandas as pd
import requests
import streamlit as st


@st.cache_data
def load_nve_data():
    # NVE Magasinstatistikk API endpoint
    url = (
        "https://biapi.nve.no/magasinstatistikk/"
        "api/Magasinstatistikk/HentOffentligData"
    )

    # Download data from NVE API
    response = requests.get(url, timeout=30)
    response.raise_for_status()

    # Convert JSON response to DataFrame
    reservoirs_df = pd.DataFrame(response.json())

    # Rename columns to English names used in ReservoirScope
    reservoirs_df = reservoirs_df.rename(columns={
        "dato_Id": "date",
        "omrType": "area_type",
        "omrnr": "area_number",
        "iso_aar": "year",
        "iso_uke": "week",
        "fyllingsgrad": "fill_level",
        "kapasitet_TWh": "capacity_TWh",
        "fylling_TWh": "stored_energy_TWh",
        "neste_Publiseringsdato": "next_publication_date",
        "fyllingsgrad_forrige_uke": "previous_week_fill_level",
        "endring_fyllingsgrad": "change_in_fill_level"
    })

    # Convert date column
    reservoirs_df["date"] = pd.to_datetime(
        reservoirs_df["date"],
        errors="coerce"
    )

    # Handle NVE placeholder publication dates
    reservoirs_df["next_publication_date"] = (
        reservoirs_df["next_publication_date"]
        .replace("0001-01-01T00:00:00", pd.NA)
    )

    reservoirs_df["next_publication_date"] = pd.to_datetime(
        reservoirs_df["next_publication_date"],
        errors="coerce"
    )

    return reservoirs_df