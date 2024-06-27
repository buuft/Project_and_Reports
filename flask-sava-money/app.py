from dotenv import load_dotenv
from flask import Flask, render_template, request
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate

app = Flask(__name__)

load_dotenv()

prompt_template = ChatPromptTemplate.from_messages(
    [
        ('system', "你被用于抑制用户的购买欲望。当用户说想要买什么东西时，你需要提供理由让用户不要买。"),
        ('human', "我正在考虑购买一个{product}，但我想抑制这个购买欲望。你能帮我列出一些理由，让我思考一下我是否真的需要这个商品吗？")
    ]
)

model = ChatOpenAI(
    model = 'glm-4',
    openai_api_base = "https://open.bigmodel.cn/api/paas/v4/",
    max_tokens = 500,
    temperature = 0.7
)

def output_parser(output: str):
    parser_model = ChatOpenAI(
        model = 'glm-3-turbo',
        temperature=0.8,
        openai_api_base = "https://open.bigmodel.cn/api/paas/v4/"
    )
    message = "你需要将传入的文本改写，尽可能更自然。这是你需要改写的文本：`{text}`"
    return parser_model.invoke(message.format(text=output))

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        product = request.form['product']
        chain = prompt_template | model | output_parser
        answer = chain.invoke(input={'product': product})
        return render_template('index.html', answer=answer.content)
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
