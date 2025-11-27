# test_deploy.py

import streamlit as st

st.title("✅ Basic Test")
st.write("If you see this, Streamlit works!")
st.success("Deployment successful!")

# Test imports one by one
st.write("---")
st.write("Testing imports...")

try:
    import pandas
    st.success("✅ pandas")
except Exception as e:
    st.error(f"❌ pandas: {e}")

try:
    import numpy
    st.success("✅ numpy")
except Exception as e:
    st.error(f"❌ numpy: {e}")

try:
    import plotly
    st.success("✅ plotly")
except Exception as e:
    st.error(f"❌ plotly: {e}")

try:
    import yfinance
    st.success("✅ yfinance")
except Exception as e:
    st.error(f"❌ yfinance: {e}")

try:
    from pathlib import Path
    import sys
    project_root = Path(__file__).parent
    sys.path.insert(0, str(project_root))
    from app.config import APP_NAME
    st.success(f"✅ config imported: {APP_NAME}")
except Exception as e:
    st.error(f"❌ config: {e}")