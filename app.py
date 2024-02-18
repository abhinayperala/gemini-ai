import streamlit as st
import sqlite3
from passlib.hash import pbkdf2_sha256
import google.generativeai as genai
from pathlib import Path

genai.configure(api_key="AIzaSyAeqGjYU_pUWyvlBw9XPkGihnTSIndrNIY")
generation_config = {"temperature": 0.9, "top_p": 1, "top_k": 1, "max_output_tokens": 2048}

model = genai.GenerativeModel("gemini-pro", generation_config=generation_config)
model1 = genai.GenerativeModel("gemini-pro-vision", generation_config=generation_config)

# Function to create a connection to the database
def create_connection():
    return sqlite3.connect('users.db')

# Function to create the users table if it doesn't exist
def create_table():
    conn = create_connection()
    with conn:
        conn.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL,
                password TEXT NOT NULL
            )
        ''')

# Function to register a new user
def register_user(username, password):
    conn = create_connection()
    with conn:
        hashed_password = pbkdf2_sha256.hash(password)
        conn.execute('INSERT INTO users (username, password) VALUES (?, ?)', (username, hashed_password))

# Function to authenticate a user
def authenticate_user(username, password):
    conn = create_connection()
    with conn:
        cursor = conn.execute('SELECT password FROM users WHERE username = ?', (username,))
        result = cursor.fetchone()
        if result:
            return pbkdf2_sha256.verify(password, result[0])
        return False

# Main part of the Streamlit app
def main():
    st.title('WELCOME TO GEMINI')

    # Create the users table if it doesn't exist
    create_table()

    # Navigation
    menu = ['Home', 'Login', 'Register', 'Chat', 'Image']
    choice = st.sidebar.selectbox('Menu', menu)

    if choice == 'Home':
        st.subheader('Home')
        # Add content for the home page

    elif choice == 'Login':
        st.subheader('Login')
        username = st.text_input('Username')
        password = st.text_input('Password', type='password')

        if st.button('Login'):
            if authenticate_user(username, password):
                st.success(f'Welcome, {username}!')
            else:
                st.error('Authentication failed. Please check your username and password.')

    elif choice == 'Register':
        st.subheader('Register')
        new_username = st.text_input('New Username')
        new_password = st.text_input('New Password', type='password')

        if st.button('Register'):
            register_user(new_username, new_password)
            st.success(f'Account created for {new_username}. You can now log in.')

    elif choice == 'Chat':
        st.title("Gemini Pro Chat Room")
        user_input = st.text_input("You: ")

        if st.button("Send"):
            response = model.generate_content([user_input])
            for chunk in response:
                st.text("Gemini Pro: " + chunk.text)

    elif choice == 'Image':
        st.title("Gemini Pro Image Chat Room")
        user_input = st.text_input("You: ")

        # File uploader widget to allow users to upload an image
        uploaded_file = st.file_uploader("Upload an image", type=["jpg", "jpeg", "png"])

        # Check if an image is uploaded
        if uploaded_file is not None:
            # Read the uploaded image bytes
            image_data = uploaded_file.read()

            # Display the uploaded image
            st.image(uploaded_file, caption="Uploaded Image", use_column_width=True)

            # Prepare image part for prompt
            image_part = {
                "mime_type": f"image/{uploaded_file.type.split('/')[-1]}",
                "data": image_data
            }

            # Prompt parts including the image
            prompt_parts = [
                "Describe the image:\n", image_part
            ]

            # Generate content based on the prompt
            response = model.generate_content(prompt_parts)

            # Display the generated content
            st.text(response)

if __name__ == '__main__':
    main()
