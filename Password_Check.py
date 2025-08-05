import streamlit as st
 
def check_password():
    def password_entered():
        if st.session_state["password_input"] == st.secrets.get("auth", {}).get("password"):
            st.session_state["password_correct"] = True
            del st.session_state["password_input"]
        else:
            st.session_state["password_correct"] = False
 
    if "password_correct" not in st.session_state:
        st.session_state["password_correct"] = False
 
    if not st.session_state["password_correct"]:
        st.text_input("Enter password:", type="password", key="password_input", on_change=password_entered)
        if st.session_state["password_correct"] == False and "password_input" in st.session_state:
            st.error("❌ Incorrect password")
        st.stop()
 
check_password()

st.success("🎉 Access granted! Welcome to the test dashboard.")

 