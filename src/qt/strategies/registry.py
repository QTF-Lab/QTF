# src/qt/strategies/registry.py
"""
A registry for discovering and loading strategy classes.

This allows strategies to be referred to by a simple string name in configs
and scripts, decoupling the rest of the framework from specific strategy
class implementations.

Strategies are registered using the `@register_strategy` decorator.
"""
from __future__ import annotations
from typing import Dict, Type

from .base import Strategy

# Global dictionary to hold the mapping from strategy name to class
_STRATEGY_REGISTRY: Dict[str, Type[Strategy]] = {}


def register_strategy(name: str):
    """
    A decorator to register a strategy class in the registry.

    Args:
        name: The name to register the strategy under.

    Example:
        @register_strategy("my_awesome_strategy")
        class MyAwesomeStrategy(Strategy):
            ...
    """

    def decorator(cls: Type[Strategy]) -> Type[Strategy]:
        if name in _STRATEGY_REGISTRY:
            raise ValueError(f"Strategy with name '{name}' is already registered.")
        _STRATEGY_REGISTRY[name] = cls
        return cls

    return decorator


def get_strategy(name: str) -> Type[Strategy]:
    """
    Retrieves a strategy class from the registry by its name.

    Args:
        name: The name of the strategy to retrieve.

    Returns:
        The strategy class.

    Raises:
        KeyError: If no strategy with the given name is registered.
    """
    if name not in _STRATEGY_REGISTRY:
        raise KeyError(
            f"No strategy registered with the name '{name}'. "
            f"Available strategies are: {list(_STRATEGY_REGISTRY.keys())}"
        )
    return _STRATEGY_REGISTRY[name]