import streamlit as st
import tensorflow as tf
import numpy as np
from PIL import Image
import io
import importlib
from streamlit_webrtc import webrtc_streamer, VideoTransformerBase
import av
import cv2

st.set_page_config(
    page_title="Detection System",
    page_icon="🔍",
    initial_sidebar_state="auto"
)

class VideoTransformer(VideoTransformerBase):
    def __init__(self, model):
        self.model = model

    def transform(self, frame):
        img = frame.to_ndarray(format="bgr24")
        img = Image.fromarray(img)
        img = img.resize((128, 128))
        input_arr = tf.keras.preprocessing.image.img_to_array(img)
        input_arr = np.array([input_arr])
        predictions = self.model.predict(input_arr)
        result_index = np.argmax(predictions)
        confidence = predictions[0][result_index] * 100

        class_name = ['Acne', 'Eczema', 'Melanoma', 'Normal']
        result_text = f'{class_name[result_index]}: {confidence:.2f}%'
        img = np.array(img)
        img = cv2.putText(img, result_text, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2, cv2.LINE_AA)
        return av.VideoFrame.from_ndarray(img, format='bgr24')

def model_prediction(input_image, model):
    try:
        image = Image.open(io.BytesIO(input_image.read()))
        image = image.resize((128, 128))
        input_arr = tf.keras.preprocessing.image.img_to_array(image)
        input_arr = np.array([input_arr])

        predictions = model.predict(input_arr)
        result_index = np.argmax(predictions)
        confidence = predictions[0][result_index] * 100

        return result_index, confidence
    except Exception as e:
        st.error(f"Error in model prediction: {e}")
        return None, None

model_path = "cnn_skin_disease_model.h5"
try:
    trained_model = tf.keras.models.load_model(model_path)
except Exception as e:
    st.error(f"Error loading the model: {e}")
    trained_model = None

st.markdown("""
<style>
    [data-testid=stSidebar] {
        background-color: #bff2ca;
    }
</style>
""", unsafe_allow_html=True)

if 'prediction_result' not in st.session_state:
    st.session_state.prediction_result = None
    st.session_state.prediction_confidence = None

if 'video_transformer' not in st.session_state:
    st.session_state.video_transformer = VideoTransformer(trained_model)

st.sidebar.title("Dashboard")
app_mode = st.sidebar.selectbox("Select Page", ["Home", "Info", "Disease Recognition","About Us"])

if app_mode == "Home":
    st.header("SKIN DISEASE DETECTION SYSTEM")
    st.markdown("""
    Welcome to the Skin Disease Detection System! 🔍
    
    We are the students of **KS Rangasamy College of Arts and Science.** 

    Our mission is to help in identifying skin diseases efficiently. Scan the surface of skin, and our system will analyze it to detect any signs of diseases. Together, let's protect our skin and ensure a healthier body!

    ### How It Works
    1. **Scan:** Go to the **Disease Recognition** page and scan the surface of skin with suspected diseases.
    2. **Analysis:** Our system will process the image using advanced algorithms to identify potential diseases.
    3. **Results:** View the results and recommendations for further action.

    ### Why Choose Us?
    - **Accuracy:** Our system utilizes state-of-the-art machine learning techniques for accurate disease detection.
    - **User-Friendly:** Simple and intuitive interface for seamless user experience.
    - **Fast and Efficient:** Receive results in seconds, allowing for quick decision-making.

    ### Get Started
    Click on the **Disease Recognition** page in the sidebar to upload an image and experience the power of our Skin Disease Recognition System!
    """)

elif app_mode == "Info":
    st.header("Information on Skin Diseases")
    class_name = st.selectbox("Select a class name to get more information:", ['Acne', 'Eczema', 'Melanoma'])
    
    if class_name:
        try:
            module = importlib.import_module(class_name)
            info_content = module.get_info()
            st.subheader(f"Information about {class_name}")
            st.write(info_content)
        except ModuleNotFoundError:
            st.error(f"Information module for {class_name} not found.")
        except AttributeError:
            st.error(f"Information function not found in the {class_name} module.")
        except Exception as e:
            st.error(f"An error occurred: {e}")

elif app_mode == "Disease Recognition":
    st.header("Disease Recognition")
    input_image = st.file_uploader("Choose an Image:", type=['jpg', 'png', 'jpeg'])
    
    if input_image:
        st.image(input_image, use_column_width=True)
        
        if st.button("Predict"):
            st.write("Our Prediction")
            if trained_model:
                result_index, confidence = model_prediction(input_image, trained_model)
                if result_index is not None:
                    class_name = ['Acne', 'Eczema', 'Melanoma', 'Normal']
                    model_predicted = class_name[result_index]
                    st.session_state.prediction_result = model_predicted
                    st.session_state.prediction_confidence = confidence
                    st.success(f"Model is predicting it's {model_predicted} with {confidence:.2f}% confidence")
                else:
                    st.error("Prediction failed. Please try again.")
            else:
                st.error("Model not loaded. Please check the model file.")

        if st.session_state.prediction_result:
            if st.button("Show Information"):
                try:
                    module = importlib.import_module(st.session_state.prediction_result)
                    info_content = module.get_info()
                    st.subheader(f"Information about {st.session_state.prediction_result}")
                    st.write(info_content)
                except ModuleNotFoundError:
                    st.error(f"Information module for {st.session_state.prediction_result} not found.")
                except AttributeError:
                    st.error(f"Information function not found in the {st.session_state.prediction_result} module.")
                except Exception as e:
                    st.error(f"An error occurred: {e}")

elif app_mode =="About Us":
    st.header("Created By ")
    st.subheader("Shurthika, Vikraman, Prasanth, Surdeep")
    # st.subheader("Under the guidance of ")
