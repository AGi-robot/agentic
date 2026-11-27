"""Offline checks that incomplete or ambiguous calls cannot execute tools."""
from unittest.mock import Mock, patch

import pytest

from agi_agentic import Tool, run


@pytest.mark.parametrize('finish', ['length', 'content_filter', None])
def test_truncated_calls_do_not_execute(finish):
    execute = Mock()
    tool = Tool('example', 'Example', {'type': 'object'}, execute)
    response = Mock()
    response.json.return_value = {'choices': [{'finish_reason': finish, 'message': {
        'tool_calls': [{'id': 'one', 'function': {'name': 'example', 'arguments': '{}'}}],
    }}]}
    with patch('agi_agentic.httpx.Client') as factory:
        factory.return_value.__enter__.return_value.post.return_value = response
        with pytest.raises(ValueError, match='incomplete'):
            run('hello', base_url='http://model.invalid/v1', model='test', tools=[tool])
    execute.assert_not_called()


def test_duplicate_call_ids_do_not_execute_any_tools():
    execute = Mock()
    tool = Tool('example', 'Example', {'type': 'object'}, execute)
    response = Mock()
    call = {'id': 'duplicate', 'function': {'name': 'example', 'arguments': '{}'}}
    response.json.return_value = {'choices': [{'finish_reason': 'tool_calls', 'message': {'tool_calls': [call, call]}}]}
    with patch('agi_agentic.httpx.Client') as factory:
        factory.return_value.__enter__.return_value.post.return_value = response
        with pytest.raises(ValueError, match='unique'):
            run('hello', base_url='http://model.invalid/v1', model='test', tools=[tool])
    execute.assert_not_called()


def test_complete_calls_execute_and_return_final_answer():
    execute = Mock(return_value={'ok': True})
    tool = Tool('example', 'Example', {'type': 'object'}, execute)
    first, final = Mock(), Mock()
    first.json.return_value = {'choices': [{'finish_reason': 'tool_calls', 'message': {'role': 'assistant', 'tool_calls': [
        {'id': 'one', 'function': {'name': 'example', 'arguments': '{}'}}]}}]}
    final.json.return_value = {'choices': [{'finish_reason': 'stop', 'message': {'content': 'Done'}}]}
    with patch('agi_agentic.httpx.Client') as factory:
        factory.return_value.__enter__.return_value.post.side_effect = [first, final]
        assert run('hello', base_url='http://model.invalid/v1', model='test', tools=[tool]) == 'Done'
    execute.assert_called_once_with()
