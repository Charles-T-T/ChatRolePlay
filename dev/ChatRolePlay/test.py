from ChatHaruhi import ChatHaruhi
import sys

def main():
    sys.path.append(".")
    chatbot = ChatHaruhi(role_name='haruhi',
                         llm='openai',
                         # max_len_story=1e5,
                         # max_len_history=1e5
                         )
    response = chatbot.chat(role='阿虚', text='我看新一年的棒球比赛要开始了！我们要去参加吗？')
    print(response)


if __name__ == "__main__":
    main()
