from openai import OpenAI

class AIService:
    def __init__(self):
        # 初始化AI服务
        pass
    
    def get_client(self, api_key, api_url):
        # 创建OpenAI客户端
        return OpenAI(
            api_key=api_key,
            base_url=api_url
        )
    
    def infer(self, model_config, prompt, system_prompt=None):
        """
        实现AI推理逻辑
        :param model_config: 模型配置字典，包含api_key、api_url、model_name等
        :param prompt: 用户输入的提示
        :param system_prompt: 系统提示词
        :return: 推理结果和token使用情况
        """
        try:
            # 创建客户端
            client = self.get_client(model_config['api_key'], model_config['api_url'])
            
            # 构建消息
            messages = []
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            messages.append({"role": "user", "content": prompt})
            
            # 调用API
            response = client.chat.completions.create(
                model=model_config['model_name'],
                messages=messages,
                temperature=0.7,
                max_tokens=1000
            )
            
            # 提取结果
            result = response.choices[0].message.content
            usage = {
                "prompt_tokens": response.usage.prompt_tokens,
                "completion_tokens": response.usage.completion_tokens,
                "total_tokens": response.usage.total_tokens
            }
            
            return {
                "success": True,
                "response": result,
                "usage": usage
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "response": None,
                "usage": None
            }
    
    def test_connection(self, model_config):
        """
        测试模型连接
        :param model_config: 模型配置字典
        :return: 测试结果
        """
        try:
            # 创建客户端
            client = self.get_client(model_config['api_key'], model_config['api_url'])
            
            # 发送一个简单的测试请求
            response = client.chat.completions.create(
                model=model_config['model_name'],
                messages=[{"role": "user", "content": "Hello, test connection!"}],
                max_tokens=10
            )
            
            return {
                "success": True,
                "message": "连接成功"
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
