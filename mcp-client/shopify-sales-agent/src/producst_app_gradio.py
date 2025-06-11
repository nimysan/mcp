import gradio as gr
from sales_agents import chat



def process_message(message, history):
    """
    处理用户消息并返回响应和指标
    """
    # 调用chat方法获取响应
    result = chat(message)
    
    # 如果发生错误
    if result.get("error"):
        error_msg = f"发生错误: {result['error']}"
        return [], error_msg, "N/A", "N/A", "N/A", "N/A"
    
    # 获取响应和指标
    response = result["response"]
    history = history or []
    history.append((message, response))
    
    # 提取指标
    if result["metrics"]:
        tokens = str(result["metrics"]["total_tokens"])
        time = f"{result['metrics']['execution_time']:.2f}"
        tools = ", ".join(result["metrics"]["tools_used"])
    else:
        tokens = "N/A"
        time = "N/A"
        tools = "N/A"
    
    # 提取并格式化messages为表格数据
    messages_list = result.get("messages", [])
    for mes in messages_list:
        print(mes)
    
    return history, None, tokens, time, tools, messages_list

# 创建Gradio界面
with gr.Blocks(
    title="商品查询助手"
) as demo:
    with gr.Column(elem_id="chat-container"):
        # gr.Markdown(
        #     "# 🛍️ 商品查询助手\n输入您想了解的商品信息，我会为您详细分析。",
        #     elem_classes="contain"
        # )
        
        with gr.Row(elem_id="metrics-container"):
            with gr.Column(scale=1, min_width=100):
                token_label = gr.Markdown("### Token使用量")
                token_value = gr.Textbox(value="N/A", interactive=False, elem_classes="metric-box")
            with gr.Column(scale=1, min_width=100):
                time_label = gr.Markdown("### 执行时间(秒)")
                time_value = gr.Textbox(value="N/A", interactive=False, elem_classes="metric-box")
            with gr.Column(scale=2, min_width=200):
                tools_label = gr.Markdown("### 使用的工具")
                tools_value = gr.Textbox(value="N/A", interactive=False, elem_classes="metric-box")
            
        with gr.Row():
            # import pandas as pd 
            # df = pd.DataFrame({
            #     "A" : [14, 4, 5, 4, 1], 
            #     "B" : [5, 2, 54, 3, 2], 
            #     "C" : [20, 20, 7, 3, 8], 
            #     "D" : [14, 3, 6, 2, 6], 
            #     "E" : [23, 45, 64, 32, 23]
            # }) 
            # gr.DataFrame(df,interactive=False,wrap=True)
            # messages_label = gr.Markdown("### Agent Messages")
            messages_value = gr.Dataframe()
        
        chatbot = gr.Chatbot(
            label="对话历史",
            height=500,
            show_copy_button=True
        )
        msg = gr.Textbox(
            placeholder="请输入您的问题...",
            label="消息输入"
        )
        clear = gr.ClearButton([msg, chatbot])
        
        examples = gr.Examples(
            examples=[
                "Solar Generate 5000这个产品怎么样？",
                "有什么太阳能发电机推荐吗？",
                "这个产品的价格是多少？",
                "现在几点？"
            ],
            inputs=msg
        )

        # 处理消息提交
        msg.submit(
            fn=process_message,
            inputs=[msg, chatbot],
            outputs=[chatbot, msg, token_value, time_value, tools_value, messages_value],
            show_progress=True
        )

# 启动应用
if __name__ == "__main__":
    demo.launch(share=False)
