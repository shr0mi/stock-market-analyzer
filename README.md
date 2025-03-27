# stock-market-analyzer
Analyzes Market with the data from Alpha Venture API and News API through Gemini API.
Check it out at: https://huggingface.co/spaces/Shromi/Stock-Market-Analyzer

#How it works
- First it collects the past 10 week stock prices from Alpha Venture API
- Creates a new GEMINI chat sending the data of stock prices and tell it to create a current price report
- Collects 10 related keywords from Gemini and searches news using those keywords by News API
- Enters top 10 news till last week to Gemini and asks for a current price analysis
- Enters top 10 news till now to Gemini and asks for a future price analysis
