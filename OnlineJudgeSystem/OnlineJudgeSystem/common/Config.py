#!/usr/bin/env python3
# -*- coding:utf-8 -*-
import os

connect_dict_windows_config = dict(host='127.0.0.1', port=3306, user='root', password='123456', database='onlinejudgesystem', charset='utf8')

# AI provider configuration. Prefer environment variables for secrets and endpoints.
# Example env vars: KIMI_API_KEY, KIMI_ENDPOINT, DEEPSEEK_API_KEY, DEEPSEEK_ENDPOINT
AI_PROVIDERS = {
	'kimi': {
		# default to a reachable Moonshot/Kimi host (can be overridden with KIMI_ENDPOINT env var)
		'endpoint': os.environ.get('KIMI_ENDPOINT', 'https://api.moonshot.cn'),
		'api_key': os.environ.get('KIMI_API_KEY', 'sk-X3JKAH3YnNb4KmzN0HopGaVV6FVnCokoIGgiAGoiflD1O3Vj'),
		'timeout': int(os.environ.get('KIMI_TIMEOUT', '10')),
	},
	'deepseek': {
		'endpoint': os.environ.get('DEEPSEEK_ENDPOINT', 'https://api.deepseek.example/v1/query'),
		'api_key': os.environ.get('DEEPSEEK_API_KEY', ''),
		'timeout': int(os.environ.get('DEEPSEEK_TIMEOUT', '10')),
	}
}

# Default provider if none specified
DEFAULT_AI_PROVIDER = os.environ.get('DEFAULT_AI_PROVIDER', 'kimi')