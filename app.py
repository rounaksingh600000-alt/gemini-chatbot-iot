# GEMINI KNOWLEDGE-BASED CHATBOT (Streamlit version)
import streamlit as st
from google import genai
from google.genai import types

# ---------------- Page setup ----------------
st.set_page_config(page_title="Arduino IoT Chatbot", page_icon="🤖", layout="centered")

# ---------------- Knowledge / Manual ----------------
MANUAL = """
ARDUINO IOT CLOUD & SENSOR GUIDE

HARDWARE SUPPORTED:
- Arduino MKR WiFi 1010, ESP8266, ESP32
- Sensors: DHT11/DHT22 (Temperature & Humidity), MQ-2 (Gas/Smoke), HC-SR04 (Ultrasonic)

WIFI CONNECTION SETUP:
To connect ESP32/ESP8266 to Wi-Fi using Arduino IDE:
#include <WiFi.h>
const char* ssid = "YOUR_SSID";
const char* password = "YOUR_PASSWORD";

void setup() {
  Serial.begin(115200);
  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("Connected to WiFi");
}

COMMON ISSUES & TROUBLESHOOTING:
- Failed to connect to Wi-Fi: Double-check your SSID and password. Ensure you are using a 2.4GHz network (ESP32/ESP8266 do not support 5GHz Wi-Fi).
- Sensor reading NaN (DHT11): Check your digital pin wiring and ensure proper pull-up resistors or correct library (`DHT sensor library`) is installed.
- Compilation Error (esp32.h missing): Go to File > Preferences, add the ESP32 board manager URL, and install 'esp32' by Espressif Systems from Boards Manager.
"""

SYSTEM_INSTRUCTION = (
    "You are an expert Arduino and IoT assistant. Use the provided manual as reference, "
    "but you can also answer any other general Arduino, sensor, or IoT programming questions "
    "using your full knowledge. Give clear, technical, and helpful answers.\n\n"
    "=== MANUAL ===\n" + MANUAL
)

# ---------------- Gemini client (key from .streamlit/secrets.toml) ----------------
@st.cache_resource
def get_client(api_key: str):
    return genai.Client(api_key=api_key)


try:
    api_key = st.secrets["GEMINI_API_KEY"]
except Exception:
    st.error(
        "Gemini API key not found. Add `GEMINI_API_KEY` to `.streamlit/secrets.toml` "
        "and restart the app."
    )
    st.stop()

if not api_key or api_key.startswith("YOUR_"):
    st.error("Please replace the placeholder in `.streamlit/secrets.toml` with your real Gemini API key.")
    st.stop()

MODEL = st.secrets.get("GEMINI_MODEL", "gemini-3.5-flash-lite")
client = get_client(api_key)

# ---------------- Session state ----------------
if "messages" not in st.session_state:
    st.session_state.messages = []

# ---------------- Sidebar ----------------
with st.sidebar:
    st.header("⚙️ Options")
    st.caption(f"Model: `{MODEL}`")
    if st.button("🗑️ Clear chat", use_container_width=True):
        st.session_state.messages = []
        st.rerun()
    with st.expander("📘 View knowledge manual"):
        st.code(MANUAL, language="text")

# ---------------- Main UI ----------------
st.title("🤖 Arduino IoT Chatbot")
st.caption("Ask about ESP32 / ESP8266 / Arduino, Wi-Fi setup, sensors and troubleshooting.")

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

if question := st.chat_input("Ask your question..."):
    st.session_state.messages.append({"role": "user", "content": question})
    with st.chat_message("user"):
        st.markdown(question)

    # Build conversation history for Gemini (roles: "user" / "model")
    contents = [
        types.Content(
            role="user" if m["role"] == "user" else "model",
            parts=[types.Part(text=m["content"])],
        )
        for m in st.session_state.messages
    ]

    with st.chat_message("assistant"):
        try:
            with st.spinner("Thinking..."):
                response = client.models.generate_content(
                    model=MODEL,
                    contents=contents,
                    config=types.GenerateContentConfig(system_instruction=SYSTEM_INSTRUCTION),
                )
            answer = response.text or "_No response received._"
        except Exception as e:
            answer = f"⚠️ Error while contacting Gemini: `{e}`"
        st.markdown(answer)

    st.session_state.messages.append({"role": "assistant", "content": answer})
