import streamlit as st 
import requests

# --- CONFIGURATION: API KEYS ---
# We will load these from Streamlit's secrets manager
RAPIDAPI_KEY = st.secrets["992bee11d3mshd96dd0aa6d3d9b7p14ca66jsn068122157885"]
RAPIDAPI_HOST = st.secrets["ai-medical-diagnosis-api-symptoms-to-results.p.rapidapi.com"]
EDAMAM_APP_ID = st.secrets["28cadc7b"]
EDAMAM_APP_KEY = st.secrets["30b5c2d3f65bd277724c9c6f8220cb43"]

# --- AGENT FUNCTIONS (No changes needed here) ---

def get_diagnosis(symptoms_text):
    url = f"https://{RAPIDAPI_HOST}/analyzeSymptomsAndDiagnose"
    symptom_list = [s.strip() for s in symptoms_text.split(',')]
    payload = {"symptoms": symptom_list, "patientInfo": {"age": 35, "gender": "female"}, "lang": "en"}
    headers = {"x-rapidapi-key": RAPIDAPI_KEY, "x-rapidapi-host": RAPIDAPI_HOST, "Content-Type": "application/json"}
    
    try:
        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()
        data = response.json()
        possible_conditions = data.get('result', {}).get('analysis', {}).get('possibleConditions', [])
        if possible_conditions:
            return possible_conditions[0].get('condition', 'Unknown Condition')
        return None
    except requests.exceptions.RequestException as e:
        st.error(f"Error calling diagnosis API: {e}")
        return None

def get_dietary_advice(disease_name):
    query = "healthy comforting food"
    if "fever" in disease_name.lower():
        query = "hydrating soup"
    elif "hypertension" in disease_name.lower():
        query = "low sodium meal"

    url = f"https://api.edamam.com/search?q={query}&app_id={EDAMAM_APP_ID}&app_key={EDAMAM_APP_KEY}&to=3"
    
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        if 'hits' in data and data['hits']:
            return [hit['recipe']['label'] for hit in data['hits']]
        return None
    except requests.exceptions.RequestException as e:
        st.error(f"Error calling Edamam API: {e}")
        return None

# --- STREAMLIT WEB INTERFACE ---

# Set up the title and a simple description
st.title("🩺 Agentic AI Health Assistant")
st.markdown("Enter your symptoms below and the AI agents will provide a possible diagnosis, precautions, and dietary advice.")
st.markdown("**Disclaimer:** This is not real medical advice. Always consult a professional.")

# 1. User Input
user_symptoms = st.text_input("Please enter your symptoms, separated by commas (e.g., fever, headache):")

# 2. Button to start the analysis
if st.button("Analyze Symptoms"):
    if user_symptoms:
        # Create a spinner to show that the app is working
        with st.spinner("Analyzing... The AI agents are at work! 🧠"):
            
            # --- Agent 1: Diagnosis ---
            st.subheader("🩺 Diagnosis Agent")
            disease = get_diagnosis(user_symptoms)
            
            if disease:
                st.success(f"**Possible Condition:** {disease}")

                # --- Agent 2: Explanation ---
                st.subheader("🧠 Explanation Agent")
                st.info(f"Based on the symptoms, a possible condition is '{disease}'. This is an AI-generated suggestion for educational purposes only.")

                # --- Agent 3: Precautions ---
                st.subheader("🛡️ Precaution Agent")
                st.markdown("""
                - Rest as much as possible.
                - Stay hydrated by drinking plenty of water.
                - Monitor your symptoms closely.
                - Consult a healthcare professional for personalized advice.
                """)

                # --- Agent 4: Nutrition ---
                st.subheader("🥦 Nutrition Agent")
                recipes = get_dietary_advice(disease)
                if recipes:
                    st.markdown("Here are some dietary suggestions:")
                    for r in recipes:
                        st.markdown(f"- Try a recipe like: **{r}**")
                else:
                    st.warning("Could not retrieve dietary suggestions.")
            else:
                st.error("Could not determine a diagnosis. Please try different symptoms.")
    else:
        st.warning("Please enter your symptoms.")