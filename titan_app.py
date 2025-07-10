import streamlit as st
import subprocess  # Import subprocess for opening applications
import spotipy
import yfinance as yf
from spotipy.oauth2 import SpotifyClientCredentials
from datetime import datetime
import re
import requests
import webbrowser
import os
import cv2
import wikipedia
import google.generativeai as genai

# Configure Google Generative AI
genai.configure(api_key="AIzaSyBf-rn2UPWQyPARj6kiATm_WGilRLt5A5U")  # Replace with your actual API key

generation_config = {
    "temperature": 1,
    "top_p": 0.95,
    "top_k": 64,
    "max_output_tokens": 8192,
    "response_mime_type": "text/plain",
}

safety_settings = [
    {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
    {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
    {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
    {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
]

model = genai.GenerativeModel(
    model_name="gemini-1.5-flash",
    safety_settings=safety_settings,
    generation_config=generation_config,
)

NEWS_API_KEY = "c30181daef0544c5957307aa18f7eb3b"  # Corrected the API key format

# Initialize Spotify client
client_credentials_manager = SpotifyClientCredentials(client_id='129f28b206c94900a828989be28c35ae',
                                                      client_secret='e72e2baa0ddd42088ad017abfc3cfe50')
sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)


# Function to get the current time
def get_time():
    now = datetime.now().strftime("%H:%M")
    return f"The current time is {now}"


# Function to get the weather
def get_weather(city):
    api_key = "84190506d5bf0843188d4a9531d7117c"  # Replace with your actual API key
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric"
    try:
        response = requests.get(url).json()
        if response.get("cod") != 200:
            return {"error": response.get("message", "Error fetching weather data.")}
        weather = response["weather"][0]["description"]
        temperature = response["main"]["temp"]
        humidity = response["main"]["humidity"]
        wind_speed = response["wind"]["speed"]
        weather_info = (f"Current weather in {city}: {weather}. "
                        f"Temperature: {temperature}°C, "
                        f"Humidity: {humidity}%, "
                        f"Wind Speed: {wind_speed} m/s.")
        return weather_info
    except Exception:
        return "An error occurred while fetching the weather."


# Function to set a reminder (simulated)
def set_reminder(reminder):
    return f"Reminder set: {reminder}"


# Function to get the latest news headlines
def get_news():
    url = f"https://newsapi.org/v2/top-headlines?country=in&apiKey={NEWS_API_KEY}"
    try:
        response = requests.get(url)
        news_data = response.json()
        if news_data["status"] == "ok":
            headlines = [article["title"] for article in news_data["articles"][:5]]
            return "Here are the latest news headlines: " + ", ".join(headlines)
        else:
            return "I couldn't fetch the news at the moment."
    except Exception:
        return "An error occurred while fetching the news."


# Function to process the command using Google Generative AI
def process_with_genai(command):
    chat_session = model.start_chat(
        history=[
            {"role": "user", "parts": [command]},
        ]
    )
    response = chat_session.send_message(command)
    return response.text


# Function to evaluate a mathematical expression
def calculate(expression):
    try:
        if re.match(r'^[\d\+\-\*/\(\) ]+$', expression):
            result = eval(expression)
            return f"The result is {result}"
        else:
            return "Invalid expression."
    except Exception:
        return "Error in calculation."


# Function to open an application
def open_application(app_name):
    """Open an application using AppOpener."""
    try:
        os.system(f"start {app_name}")
        return f"Opening {app_name}."
    except Exception as e:
        return f"An error occurred while trying to open {app_name}: {e}"


# Function to close an application
def close_application(app_name):
    """Close an application using AppOpener."""
    try:
        os.system(f"taskkill /f /im {app_name}.exe")
        return f"Closing {app_name}."
    except Exception as e:
        return f"An error occurred while trying to close {app_name}: {e}"


# Function to open Google and search for a query
def open_google_search(query):
    search_url = f"https://www.google.com/search?q={query}"
    webbrowser.open(search_url)
    return f"Searching for {query} on Google."


# Function to take a picture
def take_picture():
    try:
        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            return {"error": "Could not open webcam."}

        ret, frame = cap.read()
        if not ret:
            return {"error": "Failed to capture image."}

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"picture_{timestamp}.jpg"
        cv2.imwrite(filename, frame)

        cv2.imshow('Captured Image', frame)
        cv2.waitKey(0)
        cv2.destroyAllWindows()

        cap.release()

        return {"success": True, "filename": filename, "description": f"Picture saved as {filename}"}
    except Exception:
        return {"error": "An error occurred while taking the picture."}


def make_whatsapp_call(contact_name):
    try:
        subprocess.Popen(["/path/to/whatsapp/executable", contact_name])
        return f"Opening WhatsApp and calling {contact_name}..."
    except Exception:
        return f"An error occurred while trying to make a WhatsApp call."


# Function to search for songs on Spotify
def search_spotify(query):
    results = sp.search(q=query, type='track', limit=1)
    if results['tracks']['items']:
        return results['tracks']['items'][0]['external_urls']['spotify']
    else:
        return None


def open_youtube_search(query):
    """Open YouTube in Google Chrome and search for the given query."""
    search_url = f"https://www.youtube.com/results?search_query={query}"
    chrome_path = "C:/Program Files/Google/Chrome/Application/chrome.exe %s"  # Path to Google Chrome
    try:
        webbrowser.get(chrome_path).open(search_url)
        return f"Searching for '{query}' on YouTube."
    except Exception:
        return "An error occurred while trying to open YouTube."


# Function to play a song
def play_song(song_url):
    webbrowser.open(song_url)


# Function to get the stock price
def get_stock_price(symbol):
    try:
        stock = yf.Ticker(symbol)
        stock_info = stock.history(period="1d")
        if stock_info.empty:
            return "Could not fetch the stock price. Please check the symbol or try again later."
        latest_close = stock_info['Close'].iloc[-1]
        return f"The latest price of {symbol} is ${latest_close:.2f}"
    except Exception:
        return "An error occurred while fetching the stock price."


# Function to handle user commands
def handle_command(command):
    command = command.lower()

    if "time" in command:
        return get_time()
    elif 'search for' in command and 'in google' in command:
        search_query = command.replace('search for', '').replace('in google', '').strip()
        return open_google_search(search_query)
    elif "weather" in command:
        city = command.replace("weather in", "").strip()
        return get_weather(city)
    elif "remind me to" in command:
        reminder = command.replace("remind me to", "").strip()
        return set_reminder(reminder)
    elif "news" in command:
        return get_news()
    elif 'open' in command:
        app_name = command.replace('open', '').strip()
        return open_application(app_name)
    elif 'close' in command:
        app_name = command.replace('close', '').strip()
        return close_application(app_name)
    elif "calculate" in command:
        expression = command.replace("calculate", "").strip()
        return calculate(expression)
    elif 'take' and 'picture' in command:
        response = take_picture()
        if 'error' in response:
            return 'error'
        else:
            return (response['description'])

    elif "picture" in command:
        result = take_picture()
        if result.get("error"):
            return "An error occurred while taking the picture."
        else:
            return result["description"]
    elif "in youtube open" in command:
        query = command.replace("in youtube open", "").strip()
        return open_youtube_search(query)
    elif "whatsapp" in command and "call" in command:
        contact_name = command.replace("whatsapp call", "").strip()
        return make_whatsapp_call(contact_name)
    elif "play" in command and "song" in command:
        song_query = command.replace("play song", "").strip()
        song_url = search_spotify(song_query)
        if song_url:
            play_song(song_url)
            return f"Playing {song_query} on Spotify."
        else:
            return f"Could not find {song_query} on Spotify."
    elif 'stock' in command and 'price' in command:
        match = re.search(r'price of ([\w\s]+) today', command.lower())
        if match:
            stock_name = match.group(1).strip()
            indices = {
                "dow jones": "^DJI",
                "nasdaq": "^IXIC",
                "s&p 500": "^GSPC",
                "tesla": "TSLA",
                "apple": "AAPL",
                "microsoft": "MSFT",
                "amazon": "AMZN",
                "google": "GOOGL",
                "facebook": "META",
                "nvidia": "NVDA",
                "netflix": "NFLX",
                "adobe": "ADBE",
                "intel": "INTC",
                "cisco": "CSCO",
                "oracle": "ORCL",
                "berkshire hathaway": "BRK-B",
                "nasdaq:tsla": "TSLA",
                "nasdaq:aapl": "AAPL",
                "alphabet": "GOOGL",
                "nasdaq:amzn": "AMZN",
                "nyse:jpm": "JPM",
                "meta": "META",
                "nyse:xom": "XOM",
                "nasdaq:avgo": "AVGO",
                "eli lilly": "LLY",
                "nyse:unh": "UNH",
                "sensex": "BSESN",
                "bank nifty": "NSEBANK",
                "reliance industries": "RELIANCE.NS",
                "tata consultancy services": "TCS.NS",
                "hdfc bank": "HDFCBANK.NS",
                "infosys": "INFY.NS",
                "icici bank": "ICICIBANK.NS",
                "hdfc": "HDFC.NS",
                "kotak mahindra bank": "KOTAKBANK.NS",
                "bajaj finance": "BAJFINANCE.NS",
                "axis bank": "AXISBANK.NS",
                "larsen & toubro": "LT.NS",
                "itc": "ITC.NS",
                "tata steel": "TATASTEEL.NS",
                "coal india": "COALINDIA.NS",
                "titan company": "TITAN.NS",
                "sun pharmaceuticals": "SUNPHARMA.NS",
                "mahindra & mahindra": "M&M.NS",
                "state bank of india": "SBIN.NS",
                "hcl technologies": "HCLTECH.NS",
                "wipro": "WIPRO.NS",
                "bajaj auto": "BAJAJ-AUTO.NS",
                "britannia industries": "BRITANNIA.NS",
                "nestle india": "NESTLEIND.NS",
                "hindustan unilever": "HINDUNILVR.NS",
                "asian paints": "ASIANPAINT.NS",
                "ultratech cement": "ULTRACEMCO.NS",
                "tech mahindra": "TECHM.NS",
                "power grid corporation of india": "POWERGRID.NS",
                "nifty realty": "^CNXREALTY",
                "nifty psu bank": "^CNXPSU",
                "nifty private bank": "^NIFTYPRIVATE",
                "nifty finance": "^NIFTYFINANCE",
                "nifty consumption": "^NIFTYCONSUMPTION",
                "nifty mnc": "^NIFTYMNC",
                "nifty pharma": "^NIFTYPHARMA",
                "nifty it": "^NIFTYIT",
                "nifty metal": "^NIFTYMETAL",
                "nifty reality": "^NIFTYREALTY",
                "nifty infra": "^NIFTYINFRA",
                "nifty energy": "^NIFTYENERGY",
                "nifty media": "^NIFTYMEDIA",
                "nifty auto": "^NIFTYAUTO",
                "nifty fmcg": "^NIFTYFMCG",
                "nifty bank": "^NIFTYBANK",
                "nifty smallcap": "^NIFTYSML",
                "nifty midcap": "^NIFTYMID",
                "bse sensex": "^BSESN",
                "nifty 100": "^NIFTY100",
                "nifty 200": "^NIFTY200",
                "nifty 500": "^NIFTY500",
                "nifty 50 equal weight": "^NIFTY50EW",
                "nifty 100 equal weight": "^NIFTY100EW",
                "nifty 100 low volatility 30": "^NIFTYLVMID50",
                "nifty midcap 50": "^NIFTYMID50",
                "nifty midcap 100": "^NIFTYMID100",
                "nifty midcap 150": "^NIFTYMID150",
                "nifty smallcap 50": "^NIFTYSML50",
                "nifty smallcap 100": "^NIFTYSML100",
                "nifty smallcap 250": "^NIFTYSML250"
                # Add more indices if needed
            }
            symbol = indices.get(stock_name.lower(), stock_name.upper())
            return get_stock_price(symbol)
        else:
            return "Please specify the stock symbol."
    else:
        return process_with_genai(command)


st.title("Titan AI Assistant")
st.write("Hello! How can I assist you today?")

# Input for user commands
command = st.text_input("Enter your command:")
if st.button("Submit"):
    response = handle_command(command)
    st.write(response)
st.markdown("""
    <style>
    .container {
        display: flex;
        align-items: center;
    }
    .icon {
        margin-right: 10px;
    }
    .icon img {
        width: 30px;
        height: 30px;
    }
    </style>
    <div class="container">
        <div class="icon">
            <img src="https://img.icons8.com/color/48/000000/youtube-play.png" alt="YouTube Icon"/>
        </div>
    </div>
    <script>
    function searchYouTube() {
        var searchTerm = document.getElementById("search-term").value;
        if (searchTerm) {
            window.location.href = "https://www.youtube.com/results?search_query=" + searchTerm;
        }
    }
    </script>
""", unsafe_allow_html=True)

# Fallback for non-JS support
search_term = st.text_input("For YouTube type  your query here:")
if st.button("Search YouTube"):
    youtube_response = open_youtube_search(search_term)
    st.write(youtube_response)
