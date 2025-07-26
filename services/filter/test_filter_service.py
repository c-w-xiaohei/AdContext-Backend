import os
import pytest
from unittest.mock import patch, Mock, MagicMock
from services.filter.filter_service import FilterService

class TestFilterService:
    """FilterService测试类"""
    
    def setup_method(self):
        """测试前的设置"""
        # 使用测试用的API密钥
        self.filter_service = FilterService(
            api_key="test_api_key",
            model_name="test_model",
            api_url="https://test.api.com/v1/chat/completions"
        )
    
    @patch('services.filter.filter_service.OpenAI')
    def test_call_ai_success(self, mock_openai_class):
        """测试OpenAI调用成功的情况"""
        # 模拟OpenAI客户端和响应
        mock_client = MagicMock()
        mock_openai_class.return_value = mock_client
        
        # 模拟响应对象
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = '这是AI的回复内容'
        mock_client.chat.completions.create.return_value = mock_response
        
        # 重新初始化服务以使用mock的OpenAI客户端
        service = FilterService(
            api_key="test_api_key",
            model_name="test_model"
        )
        
        # 调用方法
        result = service._call_ai("测试提示词")
        
        # 验证结果
        assert result == "这是AI的回复内容"
        
        # 验证OpenAI客户端调用
        mock_client.chat.completions.create.assert_called_once_with(
            model="test_model",
            messages=[
                {
                    "role": "user",
                    "content": "测试提示词"
                }
            ],
            temperature=0.1,
            max_tokens=2000
        )
    
    @patch('services.filter.filter_service.OpenAI')
    def test_call_ai_json_response(self, mock_openai_class):
        """测试AI返回JSON格式响应的情况"""
        # 模拟OpenAI客户端和响应
        mock_client = MagicMock()
        mock_openai_class.return_value = mock_client
        
        # 模拟返回JSON格式的响应
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = '{"result": "JSON格式的回复", "score": 0.8}'
        mock_client.chat.completions.create.return_value = mock_response
        
        # 重新初始化服务
        service = FilterService(
            api_key="test_api_key",
            model_name="test_model"
        )
        
        # 调用方法
        result = service._call_ai("测试提示词")
        
        # 验证结果
        assert isinstance(result, dict)
        assert result['result'] == 'JSON格式的回复'
        assert result['score'] == 0.8
    
    @patch('services.filter.filter_service.OpenAI')
    def test_call_ai_integration_task(self, mock_openai_class):
        """测试归纳总结任务的参数调整"""
        # 模拟OpenAI客户端和响应
        mock_client = MagicMock()
        mock_openai_class.return_value = mock_client
        
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = '归纳总结的结果'
        mock_client.chat.completions.create.return_value = mock_response
        
        # 重新初始化服务
        service = FilterService(
            api_key="test_api_key",
            model_name="test_model"
        )
        
        # 调用包含"归纳总结"的提示词
        result = service._call_ai("请对以下内容进行归纳总结")
        
        # 验证结果
        assert result == "归纳总结的结果"
        
        # 验证参数调整
        mock_client.chat.completions.create.assert_called_once_with(
            model="test_model",
            messages=[
                {
                    "role": "user",
                    "content": "请对以下内容进行归纳总结"
                }
            ],
            temperature=0.2,  # 归纳总结时的温度
            max_tokens=1500   # 归纳总结时的token限制
        )
    
    @patch('services.filter.filter_service.OpenAI')
    def test_call_ai_request_exception(self, mock_openai_class):
        """测试请求异常的情况"""
        # 模拟OpenAI客户端异常
        mock_client = MagicMock()
        mock_openai_class.return_value = mock_client
        mock_client.chat.completions.create.side_effect = Exception("网络连接失败")
        
        # 重新初始化服务
        service = FilterService(
            api_key="test_api_key",
            model_name="test_model"
        )
        
        # 验证抛出异常
        with pytest.raises(Exception) as exc_info:
            service._call_ai("测试提示词")
        
        assert "OpenAI API调用失败" in str(exc_info.value)
        assert "网络连接失败" in str(exc_info.value)

    @patch('services.filter.filter_service.OpenAI')
    def test_filter_contexts_success(self, mock_openai_class):
        """测试上下文筛选成功的情况"""
        # 模拟OpenAI客户端和响应
        mock_client = MagicMock()
        mock_openai_class.return_value = mock_client
        
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = '筛选后的相关内容'
        mock_client.chat.completions.create.return_value = mock_response
        
        # 重新初始化服务
        service = FilterService(
            api_key="test_api_key",
            model_name="test_model"
        )
        
        # 测试数据
        user_talk = "用户的问题"
        candidate_contexts = ["上下文1", "上下文2", "上下文3"]
        
        # 调用方法
        result = service.filter_contexts(user_talk, candidate_contexts)
        
        # 验证结果
        assert result == "筛选后的相关内容"
        
        # 验证AI被调用
        mock_client.chat.completions.create.assert_called_once()
    
    def test_filter_contexts_empty_candidates(self):
        """测试空候选上下文的情况"""
        result = self.filter_service.filter_contexts("用户问题", [])
        assert result == ""
    
    @patch('services.filter.filter_service.OpenAI')
    def test_filter_contexts_no_relevant_content(self, mock_openai_class):
        """测试没有相关内容的情况"""
        # 模拟OpenAI客户端和响应
        mock_client = MagicMock()
        mock_openai_class.return_value = mock_client
        
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = '无相关内容'
        mock_client.chat.completions.create.return_value = mock_response
        
        # 重新初始化服务
        service = FilterService(
            api_key="test_api_key",
            model_name="test_model"
        )
        
        # 调用方法
        result = service.filter_contexts("用户问题", ["无关上下文"])
        
        # 验证结果
        assert result == ""
    
    @patch('services.filter.filter_service.OpenAI')
    def test_filter_contexts_exception_handling(self, mock_openai_class):
        """测试异常处理"""
        # 模拟OpenAI客户端异常
        mock_client = MagicMock()
        mock_openai_class.return_value = mock_client
        mock_client.chat.completions.create.side_effect = Exception("API错误")
        
        # 重新初始化服务
        service = FilterService(
            api_key="test_api_key",
            model_name="test_model"
        )
        
        # 调用方法，应该返回空字符串而不是抛出异常
        result = service.filter_contexts("用户问题", ["上下文"])
        
        # 验证结果
        assert result == ""
    
    def test_init_with_environment_variables(self):
        """测试使用环境变量初始化"""
        with patch.dict(os.environ, {
            'OPENAI_API_KEY': 'env_api_key',
            'OPENAI_MODEL_NAME': 'env_model',
            'OPENAI_BASE_URL': 'https://env.api.com'
        }):
            with patch('services.filter.filter_service.OpenAI') as mock_openai:
                service = FilterService()
                
                # 验证使用了环境变量
                mock_openai.assert_called_once_with(
                    api_key='env_api_key',
                    base_url='https://env.api.com'
                )
                assert service.model_name == 'env_model'
    
    def test_init_without_api_key(self):
        """测试没有API密钥时的异常"""
        with patch.dict(os.environ, {}, clear=True):
            with pytest.raises(ValueError) as exc_info:
                FilterService()
            
            assert "OpenAI API Key not provided" in str(exc_info.value)


if __name__ == "__main__":
    print("开始测试 FilterService...")
    print("请使用 'pytest test_filter_service.py -v' 运行完整测试套件。")
    
    # 简单的功能测试
    try:
        service = FilterService(
            api_key="test_key",
            model_name="gpt-3.5-turbo"
        )
        print("✅ FilterService 初始化成功")
        
        # 测试空上下文
        result = service.filter_contexts("测试问题", [])
        assert result == ""
        print("✅ 空上下文测试通过")
        
        print("🎉 基本功能测试完成！")
    except Exception as e:
        print(f"❌ 测试过程中出现错误: {e}")