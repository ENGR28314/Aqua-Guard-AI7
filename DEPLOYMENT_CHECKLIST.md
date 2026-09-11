# AquaGuard AI v6 — Streamlit deployment checklist

## Fix for NameError: calculate_sector_profile

Upload these files together to the SAME GitHub repository and folder:

- `app.py`
- `environment.py`
- `requirements.txt`

Do not upload only `app.py`.

The new `app.py` also contains a compatibility sector engine, so the Sector Screening tab remains executable if an older `environment.py` is temporarily present. For a clean deployment, replace the old `environment.py` with the one included in this ZIP.

## Streamlit Cloud

1. Commit/push the included files.
2. Confirm the main file is `app.py`.
3. Reboot/redeploy the Streamlit app.
4. If an old error remains, use Streamlit Cloud **Reboot app** after the GitHub commit is complete.

## Local test

```bash
pip install -r requirements.txt
streamlit run app.py
```
