import json
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_core.chat_history import BaseChatMessageHistory
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_community.llms import Ollama

class QA_Agent:
    def __init__(self):
        llm = Ollama(model="llama3.2")
        print("Model Loaded")

        qa_prompt = ChatPromptTemplate.from_messages([
            ("system", self.get_system_prompt()),
            MessagesPlaceholder("chat_history"),
            ("human", "{input}")
        ])
        q_chain = qa_prompt | llm

        self.chat_history = {}
        self.chat_model = RunnableWithMessageHistory(
            q_chain,
            self.get_session_history,
            input_messages_key="input",
            history_messages_key="chat_history"
        )
        print("Ynjoy!!")

    def get_session_history(self, session_id: str):
        if session_id not in self.chat_history:
            self.chat_history[session_id] = ChatMessageHistory()
        return self.chat_history[session_id]

    def reformat_json(self, json_string, path):
        data = json.loads(json_string)
        formatted_messages = []
        for message in data['messages']:
            if message['type'] == 'human':
                user_content = message['content']
                ai_response = next((msg['content'] for msg in data['messages'] if msg['type'] == 'ai'), None)
                if ai_response:
                    formatted_messages.append({
                        "user_query": user_content,
                        "ai_response": ai_response
                    })

        # Creating the desired JSON structure
        formatted_data = {
            "messages": formatted_messages
        }
        # Convert Python dictionary back to JSON string
        with open(path, 'w') as f:
            json.dump(formatted_data, f, indent=2)
        return formatted_data

    def save_history(self, path="./agent_stup.json"):
        history = self.chat_history["acc_setup"].json()
        self.reformat_json(history, path)
        print(f"History saved to {path}")

    def get_system_prompt(self):
        system_prompt = (
            """
            You are a document-based chatbot. Your task is to help users extract information and insights from uploaded documents. Only answer questions based on the uploaded content. If a question is unrelated or beyond your scope, respond with: "I'm sorry, I can't answer that." Your responses should be concise and accurate. Be polite and helpful at all times
            """
        )
        return system_prompt    
    
    def agent_chat(self, usr_prompt):
        response = self.chat_model.invoke(
            {"input": usr_prompt},
                config={
                    "configurable": {"session_id": "acc_setup"}
                }
        )
        return response

def main():
    chat_agent = QA_Agent()
    print("You are now conversing with your assistant. Good Luck!")
    print("What do you want to know about this: ")
    while True:
        prompt = input("Enter you query|('/exit' to quit session): ")
        if prompt == "/exit":
            print("You will have a fortuitous encounter soon, God Speed mate!")
            break
        response = chat_agent.agent_chat(prompt)
        print(f"Assistant: {response}")
        print("-"*30)
    chat_agent.save_history()

if __name__ == "__main__":
    main()
