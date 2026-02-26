import streamlit as st
import tempfile
import os
import json

import rule_generation
import rule_check


st.set_page_config(page_title="Contract Compliance System", layout="centered")

st.title("Contract Compliance Monitor")


uploaded_file = st.file_uploader(
    "Upload a .pdf or .py file",
    type=["pdf", "py"],
)

if uploaded_file is not None:

    # Save uploaded file temporarily
    with tempfile.NamedTemporaryFile(delete=False, suffix=f".{uploaded_file.name.split('.')[-1]}") as tmp_file:
        tmp_file.write(uploaded_file.read())
        tmp_path = tmp_file.name

    extension = os.path.splitext(tmp_path)[1].lower()

    try:
        if extension == ".pdf":
            st.info("PDF detected. Generating rules...")

            rules = rule_generation.generate_rules_from_pdf(tmp_path)

            st.success("Rules generated successfully!")

            st.subheader("Generated Rules:")
            st.json(rules)

        elif extension == ".py":
            st.info("Checking compliance...")

            result = rule_check.check_python_file(tmp_path)

            if result.get("violation"):
                st.error("VIOLATION:")
                st.markdown(f"{result.get('formatted_output')}")
            else:
                st.success("Safe to execute the file")

        else:
            st.error("Only .pdf and .py files are allowed.")

    except Exception as e:
        st.error(f"Error: {str(e)}")

    finally:
        os.remove(tmp_path)