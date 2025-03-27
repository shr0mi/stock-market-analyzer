from google import genai
import requests
import gradio as gr
import json
import os
news_api_key = os.getenv('NEWS_API_KEY')
gemini_api_key = os.getenv('GEMINI_API_KEY')
alphavantage_api_key = os.getenv('ALPHAVANTAGE_API_KEY')


def stock_app(stock_symbol):
    #Create a new gemini chat
    client = genai.Client(api_key=gemini_api_key)
    chat = client.chats.create(model="gemini-1.5-flash")

    #'''
    #Getting past 10 week stock prices from alpha vantage api

    stock_data = requests.get(f'https://www.alphavantage.co/query?function=TIME_SERIES_WEEKLY&symbol={stock_symbol}&apikey={alphavantage_api_key}')
    #print(stock_data.json())
    weekly_data = stock_data.json()["Weekly Time Series"]
    dates = list(weekly_data.keys()) #dates is a list of weekly dates that is also being used in news api


    analysis = ""
    for i in range(0,10):
        close_price = float(weekly_data[dates[i]]["4. close"])
        s = stock_symbol + " price on " + dates[i] + " is " +str(close_price)
        analysis += s + "\n"

    price_report_prompt = f"The user is asking about the current stock price of {stock_symbol}. Here is a list of data that indicates the stock prices of {stock_symbol} with dates: \n{analysis}Now generate a short within 70 words summary of the price of {stock_symbol} based on the given list so that user gets an idea about the current market situation of {stock_symbol}."
    #print(price_report_prompt)


    cur_price_report_response = chat.send_message(price_report_prompt)
    print(cur_price_report_response.text)

    #'''


    response = chat.send_message(f"Find 10 important keywords to search for in news to better understand the market of {stock_symbol}. Notice if the company has a influencial CEO or powerful competitor and contrast topic(such as oil prices can influence EV sales), you must try to include them. Write only the 10 keywords separated with a comma followed by a single space and nothing else.")
    #print(response.text)

    keywords="%28"
    comma = False
    for char in response.text:
        if char == ' ' and comma == False:
            keywords += "%20"
        elif char == ',':
            keywords += "%29%20OR%20%28"
            comma = True
        elif char != ' ':
            keywords += str(char).lower()
            comma = False

    keywords = keywords[:-1]
    keywords += "%29"
    #print(keywords)
    
    news_data = requests.get(f"https://newsapi.org/v2/everything?q={keywords}&from={dates[4]}&to={dates[1]}&sortBy=relevancy&apiKey={news_api_key}")
    news_data_new = requests.get(f"https://newsapi.org/v2/everything?q={keywords}&from={dates[1]}&to={dates[0]}&sortBy=relevancy&apiKey={news_api_key}")

    news_info = ""
    news_info_new = ""
    #print(news_data.json())
    k = 0
    for data in news_data.json()["articles"]:
        k+=1
        news_info+=data["source"]["name"] + " : "
        news_info+=data["title"] + "\n"
        news_info+=data["description"] + "\n"
        if k==10:
            break

    k = 0
    for data in news_data_new.json()["articles"]:
        k+=1
        news_info_new+=data["source"]["name"] + " : "
        news_info_new+=data["title"] + "\n"
        news_info_new+=data["description"] + "\n"
        if k==10:
            break

    #print(news_info)

    cur_market_analysis_response = chat.send_message(f"Based on the keywords you have shared here are the top 10 news from {str(dates[4])} to {str(dates[1])}:\n{news_info}\nNow write a summary of {stock_symbol}'s current market and explain it's current position within 200 words. You must not make any predictions.")
    print(cur_market_analysis_response.text)

    #print(news_info_new)
    fut_market_analysis_response = chat.send_message(f"Based on the keywords you have shared here are the top 10 news from {str(dates[1])} to {str(dates[0])}:\n{news_info}\nUsing the newly and previously provided information, write a summary of {stock_symbol}'s future market and explain it's future position within 200 words.")
    print(fut_market_analysis_response.text)

    return cur_price_report_response.text, news_info, cur_market_analysis_response.text, news_info_new, fut_market_analysis_response.text
'''
gr_interface = gr.Interface(
    fn = stock_app,
    inputs=["text"],
    outputs=[gr.Textbox(label="Current Price Report"),
             gr.Textbox(label="Current Price Analysis"),
             gr.Textbox(label="Future Price Analysis"),
             ],
)
gr_interface.launch()
'''

with gr.Blocks() as demo:
    with gr.Row():
        with gr.Column():
            text_input = gr.Textbox(label="Enter Stock Symbol")
            submit_button = gr.Button("Submit", variant='primary')
        with gr.Column():
            price_analysis = gr.Textbox(label="Current Price Report")
            with gr.Accordion("Analyzed News", open=False):
                news = gr.Textbox(label="Top 10 news related to the company till last week", lines=10)
            cur_price_analysis = gr.Textbox(label="Current Market Analysis")
            with gr.Accordion("Analyzed News", open=False):
                news_new = gr.Textbox(label="Top 10 news related to the company till now", lines=10)
            fut_price_analysis = gr.Textbox(label="Future Market Analysis")

    submit_button.click(stock_app, inputs=text_input, outputs=[price_analysis, news, cur_price_analysis, news_new, fut_price_analysis])

demo.launch()
