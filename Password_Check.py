import streamlit as st
 
def check_password():

    if "password_correct" not in st.session_state:

        st.session_state["password_correct"] = False
 
    if not st.session_state["password_correct"]:

        pwd = st.text_input("Enter password:", type="password")

        if st.button("Submit"):

            stored_password = st.secrets.get("auth", {}).get("password", None)

            if stored_password is None:

                st.error("🚨 Password is not set in secrets!")

                st.stop()

            if pwd == stored_password:

                st.session_state["password_correct"] = True

                st.experimental_rerun()

            else:

                st.error("❌ Incorrect password")

        st.stop()
 
check_password()

st.success("🎉 Access granted! Welcome to the test dashboard.")

 