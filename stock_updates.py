import telebot
import yfinance as yf
import matplotlib.pyplot as plt
from io import BytesIO

API_KEY = 'add your telegram api key'
bot = telebot.TeleBot(API_KEY)

stock_descriptions = {
    'TCS': 'Tata Consultancy Services.',
    'AAPL': 'Apple Inc. - Technology',
    'TSLA': 'Tesla Inc. - Automotive',
    'MSFT': 'Microsoft Corporation - Technology',
    'HDFC.NS': 'HDFC Bank Limited - Banking and Financial Services',
    'BHARTIARTL.NS': 'Bharti Airtel Limited - Telecommunications',
    'SBIN.NS': 'State Bank of India - Banking and Financial Services',
    'INFY.NS': 'Infosys Limited - Information Technology',
    'HINDUNILVR.NS': 'Hindustan Unilever Limited - Consumer Goods',
    'ITC.NS': 'ITC Limited - Conglomerate',
    'BAJFINANCE.NS': 'Bajaj Finance Limited - Financial Services',
    'RELIANCE.NS': 'Reliance Industries Limited - Conglomerate',
    'TCS.NS': 'Tata Consultancy Services - Information Technology'
}

@bot.message_handler(commands=['hi'])
def hello(message):
    bot.send_message(message.chat.id, "Hello!")

@bot.message_handler(commands=['wsb'])
def get_stocks(message):
    response = ""
    stocks = ['TCS', 'AAPL', 'TSLA', 'MSFT', 'HDFC.NS', 'BHARTIARTL.NS', 'SBIN.NS', 'INFY.NS', 'HINDUNILVR.NS',
              'ITC.NS', 'BAJFINANCE.NS', 'RELIANCE.NS', 'TCS.NS']

    for stock in stocks:
        data = yf.download(tickers=stock, period='2d', interval='1d')
        if data.empty:
            response += f"No data for {stock}\n"
            continue

        data.reset_index(inplace=True)
        response += f"-----{stock} ({stock_descriptions[stock]})-----\n"
        for index, row in data.iterrows():
            price = round(row['Close'], 2)
            format_date = row['Date'].strftime('%m/%d')
            response += f"{format_date} : {price}\n"

    bot.send_message(message.chat.id, response)

def stock_request(message):
    request = message.text.split()
    if len(request) < 2 or request[0].lower() != "stock":
        return False
    return True

@bot.message_handler(func=stock_request)
def send_price(message):
    request = message.text.split()[1].upper()
    data = yf.Ticker(request)
    hist = data.history(period="1d")

    if hist.empty:
        bot.send_message(message.chat.id, f"No data found for {request}")
        return

    description = stock_descriptions.get(request, 'Unknown')

    # Prepare the textual response
    response = f"Stock: {request} ({description})\n"
    response += f"Date: {hist.index[-1].strftime('%Y-%m-%d')}\n"
    response += f"Open: {hist['Open'][-1]:.2f}\n"
    response += f"High: {hist['High'][-1]:.2f}\n"
    response += f"Low: {hist['Low'][-1]:.2f}\n"
    response += f"Close: {hist['Close'][-1]:.2f}\n"
    response += f"Volume: {hist['Volume'][-1]}\n"

    # Plot the closing price graph
    plt.figure(figsize=(10, 5))
    plt.plot(hist.index, hist['Close'], marker='o', linestyle='-')
    plt.title(f"{request} Closing Prices")
    plt.xlabel("Date")
    plt.ylabel("Closing Price")
    plt.grid(True)

    # Save the plot to a BytesIO object
    buf = BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    plt.close()

    # Send the closing price graph
    bot.send_photo(message.chat.id, photo=buf)

    # Pie chart for open, high, low, close
    labels = ['Open', 'High', 'Low', 'Close']
    sizes = [hist['Open'][-1], hist['High'][-1], hist['Low'][-1], hist['Close'][-1]]
    colors = ['gold', 'yellowgreen', 'lightcoral', 'lightskyblue']

    plt.figure(figsize=(7, 7))
    plt.pie(sizes, labels=labels, colors=colors, autopct='%1.1f%%', shadow=True, startangle=140)
    plt.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.

    # Save the pie chart to a BytesIO object
    buf_pie = BytesIO()
    plt.savefig(buf_pie, format='png')
    buf_pie.seek(0)
    plt.close()

    # Send the pie chart
    bot.send_photo(message.chat.id, photo=buf_pie)

    # Send the textual response
    bot.send_message(message.chat.id, response)

bot.polling()
