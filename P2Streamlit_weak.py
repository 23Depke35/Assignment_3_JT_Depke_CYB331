import streamlit as st

st.title("Comment Submission Page")

# Form setup
with st.form(key="comment_form"):
    user_comment = st.text_area("Leave a comment:")
    submit_button = st.form_submit_button(label="Submit")

# Display submitted comment
if submit_button and user_comment:
    st.subheader("Your Submitted Comment:")
    st.write(user_comment)