import streamlit as st

def show_welcome():
    st.markdown(
        """
        <style>
        .welcome-title {
            font-size: 48px;
            font-weight: 900;
            color: #2e86de;
            text-align: center;
            margin-top: 30px;
        }
        .welcome-subtitle {
            font-size: 22px;
            color: #34495e;
            text-align: center;
            margin-bottom: 30px;
        }
        .welcome-container {
            background: linear-gradient(135deg, #f9f9f9 0%, #d0e8f2 100%);
            padding: 40px;
            border-radius: 15px;
            box-shadow: 0 8px 16px rgba(0,0,0,0.1);
            max-width: 800px;
            margin-left: auto;
            margin-right: auto;
        }
        </style>
        """, unsafe_allow_html=True)

    st.markdown('<div class="welcome-container">', unsafe_allow_html=True)
    st.markdown('<h1 class="welcome-title">🦷 Welcome to Dentistry Stage 4! 🦷</h1>', unsafe_allow_html=True)
    st.markdown('<p class="welcome-subtitle">Your journey to becoming a dental expert starts here. Let’s learn, practice, and succeed together! 💪✨</p>', unsafe_allow_html=True)

    st.image(
        "https://images.unsplash.com/photo-1588776814546-44ff6a7e8d3b?auto=format&fit=crop&w=900&q=80",
        caption="Your Journey Starts Here",
        use_container_width=True,
    )

    st.markdown("</div>", unsafe_allow_html=True)
