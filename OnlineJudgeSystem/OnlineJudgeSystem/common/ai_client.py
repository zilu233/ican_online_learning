#!/usr/bin/env python3
# -*- coding:utf-8 -*-
"""
Lightweight AI provider client supporting Kimi and DeepSeek via simple HTTP POST requests.
This module intentionally keeps dependencies minimal (only requests).
"""
import requests
import urllib.parse
import json
import time
import os
import logging
from typing import Tuple, Optional
from OnlineJudgeSystem.common.Config import AI_PROVIDERS, DEFAULT_AI_PROVIDER

logger = logging.getLogger(__name__)
if not logger.handlers:
    # minimal console logging by default
    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)s %(message)s'))
    logger.addHandler(handler)
    logger.setLevel(os.environ.get('AI_CLIENT_LOG_LEVEL', 'INFO'))


class AIClientError(Exception):
    pass


class AIClient:
    def __init__(self, provider: str = None):
        self.provider_name = provider or DEFAULT_AI_PROVIDER
        if self.provider_name not in AI_PROVIDERS:
            raise AIClientError(f"Unknown AI provider: {self.provider_name}")
        self.cfg = AI_PROVIDERS[self.provider_name]
        self.endpoint = self.cfg.get('endpoint')
        self.api_key = self.cfg.get('api_key')
        self.timeout = self.cfg.get('timeout', 10)

    def ask(self, question: str, metadata: dict = None) -> Tuple[bool, dict]:
        """
        Send a question to the configured AI provider.
        Returns (success, response_dict).
        """
        if not self.endpoint:
            raise AIClientError("No endpoint configured for provider")

        # Mock mode: when AI_MOCK is true, return a canned response for local dev/offline
        if os.environ.get('AI_MOCK', '').lower() in ('1', 'true', 'yes'):
            mock_answer = os.environ.get('AI_MOCK_ANSWER', '这是一个模拟回答（AI_MOCK 模式）。请在生产环境配置真实的 KIMI_ENDPOINT 与 API_KEY。')
            logger.info('AI_MOCK enabled - returning mock answer')
            return True, {'raw': {'mock': True}, 'answer': mock_answer}

        # Provider-specific routing: for known providers implement small adapters
        if self.provider_name == 'kimi':
            return self._ask_kimi(question, metadata)

        # default generic behavior
        headers = {
            'Content-Type': 'application/json',
        }
        if self.api_key:
            headers['Authorization'] = f"Bearer {self.api_key}"

        payload = {
            'question': question,
        }
        if metadata:
            payload['metadata'] = metadata

        try:
            resp = requests.post(self.endpoint, headers=headers, data=json.dumps(payload), timeout=self.timeout)
        except Exception as e:
            # Catch broad exceptions (including requests.RequestException and mocks
            logger.exception("HTTP request failed")
            msg = str(e)
            err_type = 'network_error'
            # simple heuristics for DNS/name resolution problems
            if 'Failed to resolve' in msg or 'NameResolutionError' in msg or 'getaddrinfo' in msg:
                err_type = 'dns_error'
            return False, {'error': msg, 'error_type': err_type}

        try:
            data = resp.json()
        except Exception:
                return False, {'error': 'invalid_json_response', 'status_code': resp.status_code, 'text': resp.text, 'error_type': 'invalid_response'}

        if resp.status_code >= 400:
            return False, {'error': 'provider_error', 'status_code': resp.status_code, 'body': data}

        # Normalization: expect provider to return {'answer': '...'} or similar
        answer = data.get('answer') or data.get('result') or data.get('text') or ''
        return True, {'raw': data, 'answer': answer}

    def _ask_kimi(self, question: str, metadata: Optional[dict] = None) -> Tuple[bool, dict]:
        """Small adapter for Kimi API (best-effort). Uses Bearer auth by default.

        Assumptions (from common Kimi-style APIs):
        - POST JSON body with keys like `question` or `prompt`.
        - Authorization: Bearer <API_KEY>
        - Successful response contains a JSON with `answer` or `data.answer`.
        If Kimi's real API differs, provide the exact example and I'll adapt.
        """
        # Prefer using an OpenAI-compatible SDK (Moonshot Kimi exposes an OpenAI-like API)
        model = os.environ.get('KIMI_MODEL') or self.cfg.get('model') or 'kimi-k2-0905-preview'

        # Try OpenAI-compatible client first (example: `from openai import OpenAI` / pip package `openai` >= newer SDKs)
        try:
            # Prefer the OpenAI-compatible SDK and mirror the working debug script usage
            from openai import OpenAI  # type: ignore
            logger.info('Using OpenAI SDK for Kimi/Moonshot call (SDK import succeeded)')

            # Use the endpoint/env value as the base_url exactly as provided (don't strip /v1)
            base_url = self.endpoint or os.environ.get('KIMI_ENDPOINT')
            client_kwargs = {}
            if self.api_key:
                client_kwargs['api_key'] = self.api_key
            if base_url:
                # OpenAI SDK expects base_url that already includes '/v1'
                # If user configured host without path, append '/v1'
                normalized = base_url.rstrip('/')
                if not normalized.endswith('/v1'):
                    normalized = normalized + '/v1'
                client_kwargs['base_url'] = normalized

            client = OpenAI(**client_kwargs)

            messages = [
                {"role": "system", "content": os.environ.get('KIMI_SYSTEM_PROMPT', '你是 Kimi，由 Moonshot AI 提供的人工智能助手。')},
                {"role": "user", "content": question}
            ]

            resp = client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=float(os.environ.get('KIMI_TEMPERATURE', '0.6')),
            )

            # Extract text from SDK response (support multiple shapes)
            answer = ''
            try:
                answer = resp.choices[0].message.content
            except Exception:
                try:
                    answer = resp.choices[0].text
                except Exception:
                    try:
                        j = getattr(resp, 'to_dict', lambda: dict(resp))()
                        answer = j.get('choices', [{}])[0].get('message', {}).get('content') or j.get('choices', [{}])[0].get('text')
                    except Exception:
                        answer = str(resp)

            # Convert SDK response to a serializable form for callers/logging
            raw_serializable = None
            try:
                if hasattr(resp, 'to_dict'):
                    raw_serializable = resp.to_dict()
                else:
                    # try to convert to dict-like structure
                    raw_serializable = dict(resp)
            except Exception:
                try:
                    raw_serializable = json.loads(json.dumps(resp, default=lambda o: getattr(o, '__dict__', str(o)), ensure_ascii=False))
                except Exception:
                    raw_serializable = repr(resp)

            return True, {'raw': raw_serializable, 'answer': answer}
        except Exception as e:
            # SDK not available or failed; fallback to HTTP requests
            logger.info('OpenAI SDK unavailable or failed, fallback to requests: %s', e)

        # Fallback to requests-based POST (original behavior)
        headers = {
            'Content-Type': 'application/json'
        }
        if self.api_key:
            headers['Authorization'] = f"Bearer {self.api_key}"

        # Determine if endpoint expects chat-style payload (messages) based on path
        is_chat_endpoint = False
        try:
            parsed = urllib.parse.urlparse(self.endpoint)
            path = parsed.path or ''
            if 'chat' in path or path.endswith('completions'):
                is_chat_endpoint = True
        except Exception:
            path = ''

        # If endpoint contains only host (no path), assume OpenAI-like chat completions path
        try:
            parsed = urllib.parse.urlparse(self.endpoint)
            if not parsed.path or parsed.path == '/':
                # target the canonical chat completions path
                self._requests_target = self.endpoint.rstrip('/') + '/v1/chat/completions'
                # Since we are explicitly targeting chat completions, force chat-style payload
                is_chat_endpoint = True
            else:
                self._requests_target = self.endpoint
        except Exception:
            self._requests_target = self.endpoint

        if is_chat_endpoint:
            payload = {
                'model': model,
                'messages': [
                    {'role': 'system', 'content': os.environ.get('KIMI_SYSTEM_PROMPT', 'You are Kimi, an assistant.')},
                    {'role': 'user', 'content': question}
                ]
            }
            if metadata:
                payload['metadata'] = metadata
        else:
            payload = {
                'question': question,
            }
            if metadata:
                payload['metadata'] = metadata
            if model:
                # include model hint for providers that accept it
                payload['model'] = model

        max_retries = int(os.environ.get('AI_CLIENT_MAX_RETRIES', '2'))
        backoff = float(os.environ.get('AI_CLIENT_BACKOFF', '0.5'))
        last_err = None
        # Auto-probe mode: when enabled, try common alternative endpoints/payloads/headers
        auto_probe = os.environ.get('AI_CLIENT_AUTO_PROBE', '').lower() in ('1', 'true', 'yes')
        if auto_probe:
            logger.info('AI client auto-probe enabled: will try alternative paths/headers on 400/403')
        for attempt in range(max_retries + 1):
            try:
                # In probe/debug mode, log the outgoing headers and payload (redact sensitive values)
                if auto_probe:
                    try:
                        logged_headers = {k: ('REDACTED' if k.lower() in ('authorization', 'x-api-key') else v) for k, v in headers.items()}
                    except Exception:
                        logged_headers = headers
                    try:
                        logged_payload = json.dumps(payload, ensure_ascii=False)
                    except Exception:
                        logged_payload = str(payload)
                    logger.debug('Sending request to %s (attempt %s). Headers: %s; Payload: %s', self.endpoint, attempt + 1, logged_headers, logged_payload)

                resp = requests.post(self._requests_target, headers=headers, json=payload, timeout=self.timeout)
            except Exception as e:
                last_err = str(e)
                logger.warning('Kimi request failed on attempt %s: %s', attempt + 1, e)
                time.sleep(backoff * (2 ** attempt))
                continue

            try:
                data = resp.json()
            except Exception:
                logger.error('Kimi returned non-json response: %s', resp.text)
                return False, {'error': 'invalid_json_response', 'status_code': resp.status_code, 'text': resp.text, 'error_type': 'invalid_response'}

            if resp.status_code >= 400:
                logger.warning('Kimi responded with error status %s: %s', resp.status_code, data)
                last_err = {'status_code': resp.status_code, 'body': data}
                # If allowed, try auto-probe alternatives for 400/401/403 to discover correct path/payload/header
                if auto_probe and resp.status_code in (400, 401, 403):
                    try:
                        # Build a small set of alternative endpoints and payloads to try
                        base = self.endpoint.rstrip('/')
                        alt_paths = [
                            base,
                            base + '/chat/completions',
                            base + '/completions',
                            base + '/v1',
                        ]

                        alt_headers = [headers.copy()]
                        # alternative header style (some providers use x-api-key)
                        if self.api_key:
                            h2 = headers.copy()
                            h2.pop('Authorization', None)
                            h2['x-api-key'] = self.api_key
                            alt_headers.append(h2)

                        alt_payloads = []
                        # chat-style
                        alt_payloads.append({
                            'model': model,
                            'messages': [
                                {'role': 'system', 'content': os.environ.get('KIMI_SYSTEM_PROMPT', 'You are Kimi, an assistant.')},
                                {'role': 'user', 'content': question}
                            ]
                        })
                        # prompt-style
                        alt_payloads.append({'prompt': question, 'model': model})
                        # simple question field
                        alt_payloads.append({'question': question})

                        probe_timeout = float(os.environ.get('AI_CLIENT_PROBE_TIMEOUT', '8'))
                        for p in alt_paths:
                            for ah in alt_headers:
                                for ap in alt_payloads:
                                    # Log probe attempt details (redact sensitive headers)
                                    try:
                                        probe_logged_headers = {k: ('REDACTED' if k.lower() in ('authorization', 'x-api-key') else v) for k, v in ah.items()}
                                    except Exception:
                                        probe_logged_headers = ah
                                    try:
                                        probe_logged_payload = json.dumps(ap, ensure_ascii=False)
                                    except Exception:
                                        probe_logged_payload = str(ap)
                                    logger.info('Auto-probe trying %s with headers %s and payload keys %s', p, list(ah.keys()), list(ap.keys()))
                                    logger.debug('Auto-probe sending to %s. Headers: %s; Payload: %s', p, probe_logged_headers, probe_logged_payload)
                                    try:
                                        r = requests.post(p, headers=ah, json=ap, timeout=probe_timeout)
                                    except Exception as e:
                                        logger.debug('Auto-probe request to %s failed: %s', p, e)
                                        continue
                                    try:
                                        rd = r.json()
                                    except Exception:
                                        logger.debug('Auto-probe non-json response from %s: %s', p, r.text)
                                        continue
                                    if r.status_code < 400:
                                        ans = rd.get('answer') or (rd.get('data') and rd.get('data').get('answer')) or rd.get('result') or rd.get('text')
                                        if ans is None:
                                            ans = json.dumps(rd, ensure_ascii=False)
                                        logger.info('Auto-probe succeeded on %s', p)
                                        return True, {'raw': rd, 'answer': ans, 'probe': {'path': p, 'headers': list(ah.keys())}}
                        logger.info('Auto-probe exhausted alternatives, continuing original retry/backoff')
                    except Exception:
                        logger.exception('Auto-probe failed unexpectedly')

                if 500 <= resp.status_code < 600 and attempt < max_retries:
                    time.sleep(backoff * (2 ** attempt))
                    continue
                return False, {'error': 'provider_error', 'status_code': resp.status_code, 'body': data, 'error_type': 'provider_error'}

            answer = data.get('answer') or (data.get('data') and data.get('data').get('answer')) or data.get('result') or data.get('text')
            if answer is None:
                answer = json.dumps(data, ensure_ascii=False)

            return True, {'raw': data, 'answer': answer}

        return False, {'error': 'request_failed', 'detail': last_err, 'error_type': 'request_failed'}


# Convenience factory
def get_client(provider: str = None) -> AIClient:
    return AIClient(provider)
