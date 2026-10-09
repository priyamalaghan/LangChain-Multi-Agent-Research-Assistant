# LangChain-Multi-Agent-Research-Assistant
Research assistant of fully autonomous AI system that thinks, searches, reads and writes on its own.Instead of a single AI answering your question from tools, we are deploying a team of specialized intelligent agents that collaborate together to produce a professional research report on any topic you give them. The research agent goes out on the live internet and finds the most relevant and recent sources. The Reader Agent then dives deep into those sources, scrapping and extracting meaningful content. The Writer Agent takes all that gathered intelligence and crafts well structured detailed report. And finally the Critic Agent reviews the entire report, sources it and gives feedback just like A senior researcher reviewing a junior's work. Every single agent is powered by a large language model connected through langChain's modern LCEL pipeline and orchestrated through a shared memory system that makes them work as one unified brain. 

from langchain_google_genai import ChatGoogleGenerativeAI
import os

llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    google_api_key=os.getenv("GEMINI_API_KEY")
)

response = llm.invoke("What is LangGraph?")
print(response.content)

