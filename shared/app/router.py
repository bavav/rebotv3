from typing import Callable,Any,Dict,List
import inspect


class RabbitRouter:
    def __init__(self):
        self.handlers: list = []

    def event(self, event_type: str, *filters: Any):
        def decorator(func: Callable):
            self.handlers.append({
                "func": func,
                "event_type": event_type,
                "filters": filters
            })
            return func
        return decorator

    async def resolve(self, event_type: str, event_object: Any):
        for handler in self.handlers:
            if handler["event_type"] != event_type:
                continue

            filters_passed = True
            for filter_func in handler["filters"]:
                try:
                    # Проверяем, асинхронный ли фильтр (метод __call__ или функция)
                    if inspect.iscoroutinefunction(filter_func) or (
                        hasattr(filter_func, "__call__") and inspect.iscoroutinefunction(filter_func.__call__)
                    ):
                        res = await filter_func(event_object)
                    else:
                        res = filter_func(event_object)

                    if not res:
                        filters_passed = False
                        break
                except Exception:
                    filters_passed = False
                    break

            if filters_passed:
                
                await handler["func"](event_object)
                return True
        return False


        
from typing import Any, Callable

from typing import Any

class BaseFilter:
    async def __call__(self, event: Any) -> bool:
        """
        Этот метод ДОЛЖЕН быть переопределен в вашем фильтре.
        Мы делаем его асинхронным, чтобы внутри фильтра можно было 
        делать запросы к БД, Redis или внешним API.
        """
        raise NotImplementedError


class MagicFilter:
    def __init__(self, path: list = None):
        self._path = path or []

    def __getattr__(self, item: str) -> Any:
        string_methods = {"startswith", "endswith", "contains"}
        if item in string_methods:
            return lambda *args, **kwargs: self._call_string_method(item, *args, **kwargs)
        return MagicFilter(self._path + [item])

    # УНИВЕРСАЛЬНЫЙ МЕТОД ИЗВЛЕЧЕНИЯ
    def _get_value(self, obj: Any) -> Any:
        current = obj
        for key in self._path:
            if current is None:
                return None
                
            # 1. Если это словарь или поддерживает обращение по ключу
            if isinstance(current, dict) and key in current:
                current = current[key]
            # 2. Если это объект класса и у него есть такой атрибут
            elif hasattr(current, key):
                current = getattr(current, key)
            else:
                return None
        return current

    def _call_string_method(self, method_name: str, *args, **kwargs) -> Callable[[Any], bool]:
        def checker(obj: Any) -> bool:
            value = self._get_value(obj)
            if not isinstance(value, str):
                return False
            if method_name == "startswith":
                return value.startswith(*args, **kwargs)
            elif method_name == "endswith":
                return value.endswith(*args, **kwargs)
            elif method_name == "contains":
                return args[0] in value
            return False
        return checker

    # Операторы сравнения
    def __eq__(self, other: Any) -> Callable[[Any], bool]:
        return lambda obj: self._get_value(obj) == other

    def __gt__(self, other: Any) -> Callable[[Any], bool]:
        return lambda obj: self._get_value(obj) > other



# Создаем глобальный объект-точку входа, как в aiogram

