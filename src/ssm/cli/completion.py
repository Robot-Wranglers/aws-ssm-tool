""" ssm.cli.completion

    Click shell_complete callbacks for dynamic tab completion.
    Provides completions for SSM parameter names, paths, and AWS profiles.
"""

import os
import time

from click.shell_completion import CompletionItem

__all__ = ["complete_profiles", "complete_parameters", "complete_paths"]

# Simple time-based cache: {key: (value, timestamp)}
_cache = {}
_cache_ttl = 300  # 5 minutes


def _get_profile(ctx):
    """Resolve the active AWS profile from context or environment."""
    return (
        (ctx.params.get("profile") if ctx else None)
        or os.environ.get("AWS_PROFILE")
        or "default"
    )


def _cached_fetch(cache_key, fetch_fn):
    """Fetch with time-based caching."""
    now = time.time()
    if cache_key in _cache:
        value, timestamp = _cache[cache_key]
        if now - timestamp < _cache_ttl:
            return value
    value = fetch_fn()
    _cache[cache_key] = (value, now)
    return value


def _fetch_keys(profile):
    """Fetch all parameter names for a profile using describe_parameters (no decryption)."""
    from ssm.api.environment import Environment

    env = Environment.from_profile(profile)
    return env.secrets.keys("/")


def _extract_paths(keys):
    """Extract directory paths from a list of parameter names."""
    paths = set()
    for key in keys:
        parts = key.strip("/").split("/")
        for i in range(1, len(parts)):
            paths.add("/" + "/".join(parts[:i]))
    return sorted(paths)


def complete_profiles(ctx, param, incomplete):
    """Complete AWS profile names."""
    try:
        from ssm.api.environment import Environment

        profiles = _cached_fetch("profiles", Environment.list_profiles)
        return [
            CompletionItem(p)
            for p in profiles
            if p.startswith(incomplete)
        ]
    except Exception:
        return []


def complete_parameters(ctx, param, incomplete):
    """Complete SSM parameter names."""
    try:
        profile = _get_profile(ctx)
        keys = _cached_fetch(
            f"params:{profile}", lambda: _fetch_keys(profile)
        )
        return [
            CompletionItem(k)
            for k in keys
            if k.startswith(incomplete)
        ]
    except Exception:
        return []


def complete_paths(ctx, param, incomplete):
    """Complete SSM directory paths."""
    try:
        profile = _get_profile(ctx)
        keys = _cached_fetch(
            f"params:{profile}", lambda: _fetch_keys(profile)
        )
        paths = _cached_fetch(
            f"paths:{profile}", lambda: _extract_paths(keys)
        )
        return [
            CompletionItem(p)
            for p in paths
            if p.startswith(incomplete)
        ]
    except Exception:
        return []
