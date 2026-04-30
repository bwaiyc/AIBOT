"""
GUI事件处理模块 - 已修复版

该模块提供了GUI事件处理的统一接口，支持配置变更的实时保存和嵌套路径解析。
"""
import os
import logging
from typing import Any, Callable, Dict, List, Optional, Tuple, Union

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class ConfigChangeHandler:
    """
    配置变更处理器
    统一处理GUI控件的值变更事件，支持动态路径解析和自动保存。
    """

    def __init__(self, config: dict, save_callback: Callable = None):
        """
        初始化配置变更处理器
        Args:
            config: 配置字典
            save_callback: 保存配置的回调函数（通常是写入 config.json 的函数）
        """
        self.config = config
        self.save_callback = save_callback
        self.handlers = {}
        self.post_processors = {}
        self.context_providers = {}

    def register_context_provider(self, name: str, provider: Callable) -> None:
        """注册上下文提供函数（如获取当前选中的组名或按键名）"""
        self.context_providers[name] = provider

    def get_context(self, context_name: str) -> Any:
        """获取当前上下文的值"""
        if context_name not in self.context_providers:
            raise ValueError(f'未注册的上下文: {context_name}')
        return self.context_providers[context_name]()

    def save(self) -> None:
        """手动触发保存回调"""
        if self.save_callback:
            try:
                self.save_callback()
                logger.debug("配置已通过回调保存")
            except Exception as e:
                logger.error(f"保存配置时出错: {e}")

    def get_value(self, path: str) -> Any:
        """获取指定路径的配置值"""
        return self._get_config_value(path)

    def set_value(self, path: str, value: Any, save: bool = True) -> None:
        """手动设置配置值并可选触发保存"""
        self._set_config_value(path, value)
        if save:
            self.save()

    def register_config_item(self, control_id: str, config_path: str, value_type: type = None,
                             post_processor: Callable = None, special_handler: Callable = None) -> None:
        """
        注册配置项
        Args:
            control_id: 控件ID
            config_path: 配置路径，支持点分隔和 {var} 占位符
            value_type: 目标转换类型 (int, float, bool, str)
            post_processor: 配置更新后的回调（如更新推理引擎参数）
            special_handler: 完全接管处理的函数
        """
        self.handlers[control_id] = {
            'path': config_path,
            'type': value_type,
            'post_processor': post_processor,
            'special_handler': special_handler
        }
        if post_processor:
            self.post_processors[config_path] = post_processor

    def _resolve_path(self, path: str) -> List[str]:
        """解析路径并替换上下文变量"""
        parts = path.split('.')
        resolved_parts = []
        for part in parts:
            if part.startswith('{') and part.endswith('}'):
                context_name = part[1:-1]
                resolved_parts.append(str(self.get_context(context_name)))
            else:
                resolved_parts.append(part)
        return resolved_parts

    def _get_config_value(self, path: str) -> Any:
        parts = self._resolve_path(path)
        value = self.config
        for part in parts:
            if isinstance(value, dict) and part in value:
                value = value[part]
            else:
                return None
        return value

    def _set_config_value(self, path: str, value: Any) -> None:
        parts = self._resolve_path(path)
        config = self.config
        for i in range(len(parts) - 1):
            part = parts[i]
            if part not in config or not isinstance(config[part], dict):
                config[part] = {}
            config = config[part]
        config[parts[-1]] = value

    def handle_change(self, sender: str, app_data: Any) -> None:
        """处理来自GUI的变更事件"""
        if sender not in self.handlers:
            logger.warning(f'未注册的控件ID: {sender}')
            return

        handler = self.handlers[sender]

        # 1. 执行特殊处理逻辑（如果有）
        if handler['special_handler']:
            handler['special_handler'](sender, app_data)
            self.save()
            return

        # 2. 类型转换与更新
        path = handler['path']
        value_type = handler['type']
        converted_data = app_data

        if value_type:
            try:
                if value_type == float:
                    converted_data = round(float(app_data), 4)
                elif value_type == int:
                    converted_data = int(app_data)
                elif value_type == bool:
                    converted_data = bool(app_data)
                elif value_type == str:
                    converted_data = str(app_data)
            except (ValueError, TypeError) as e:
                logger.error(f'控件 {sender} 类型转换失败 ({value_type}): {e}')
                return

        # 3. 写入内存并保存到文件
        self._set_config_value(path, converted_data)
        logger.info(f'配置项 {path} 已更新为: {converted_data}')
        self.save()

        # 4. 执行后处理器
        post_processor = handler.get('post_processor')
        if post_processor:
            post_processor()

    def create_handler(self, sender: str) -> Callable:
        """为特定控件创建回调闭包"""
        return lambda s, a: self.handle_change(sender, a)


class ConfigItemGroup:
    """
    配置项组，简化嵌套路径的批量注册。
    """

    def __init__(self, handler: ConfigChangeHandler, base_path: str = ''):
        self.handler = handler
        self.base_path = base_path

    def sub_group(self, relative_path: str) -> 'ConfigItemGroup':
        """创建基于当前路径的子组"""
        full_path = f'{self.base_path}.{relative_path}' if self.base_path else relative_path
        return ConfigItemGroup(self.handler, full_path)

    def register_item(self, control_id: str, path: str, value_type: type = None,
                      post_processor: Callable = None, special_handler: Callable = None) -> None:
        """注册属于该组的配置项"""
        full_path = f'{self.base_path}.{path}' if self.base_path else path
        self.handler.register_config_item(control_id, full_path, value_type, post_processor, special_handler)