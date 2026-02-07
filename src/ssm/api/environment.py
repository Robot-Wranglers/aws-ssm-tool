""" ssm.api.environment

Core abstraction for environment-aware boto, which
reduces a lot of boilerplate with boto sessions/profiles
"""

import collections
import functools
import typing

import boto3
from botocore import session
from botocore.config import Config

from ssm import abcs, util

from .manager import SecretManager

__all__ = ["Environment"]

# default logger only used for class-methods,
# because for this there is no instance is available
LOGGER = util.get_logger(__name__, fake=True)  # Quiet during import

# Retry configuration for resilience
BOTO_CONFIG = Config(
    retries={
        "max_attempts": 3,
        "mode": "adaptive",
    },
    connect_timeout=5,
    read_timeout=30,
)


class Environment(abcs.Loggable):
    """
    AWS environment abstraction for managing SSM parameters across profiles.

    Supports:
    - Multiple AWS profiles/environments
    - Lazy initialization of AWS clients
    - Retry configuration for resilience
    - Cached SecretManager instances
    """

    # Class-level storage for profile configs (populated lazily)
    ENV_CONFIGS: typing.ClassVar[typing.Dict[str, dict]] = None
    ALL_PROFS: typing.ClassVar[typing.List[str]] = None
    _profiles_loaded: typing.ClassVar[bool] = False

    @classmethod
    def _ensure_profiles_loaded(cls) -> None:
        """Lazily load AWS profiles on first access."""
        if cls._profiles_loaded:
            return

        cls.ENV_CONFIGS = collections.OrderedDict()
        cls.ALL_PROFS = session.Session().available_profiles

        for profile_name in cls.ALL_PROFS:
            cls.ENV_CONFIGS[profile_name] = dict(
                profile_name=profile_name,
                name=cls.normalize_env_name(profile_name),
            )

        cls._profiles_loaded = True

    @staticmethod
    def normalize_env_name(name: str) -> str:
        """Normalize environment name (override for custom normalization)."""
        return name

    @classmethod
    def from_profile(cls, name: str) -> "Environment":
        """
        Instantiate an Environment from AWS profile name.

        Args:
            name: AWS profile name (e.g., 'default', 'dev', 'prod')

        Returns:
            Environment instance configured for the profile

        Raises:
            KeyError: If profile name not found
        """
        cls._ensure_profiles_loaded()
        assert isinstance(name, str), type(name)
        normal_name = cls.normalize_env_name(name)
        try:
            config = cls.ENV_CONFIGS[normal_name]
        except KeyError:
            available = list(cls.ENV_CONFIGS.keys())
            err = f"Profile `{normal_name}` not found. Available: {available}"
            raise KeyError(err)
        return cls(config=config)

    @classmethod
    def list_profiles(cls) -> typing.List[str]:
        """Return list of available AWS profile names."""
        cls._ensure_profiles_loaded()
        return list(cls.ALL_PROFS)

    @property
    def profile_name(self) -> typing.Optional[str]:
        """Returns the AWS profile name from config."""
        return self.config.get("profile_name")

    profile = profile_name

    @property
    def account_aliases(self) -> typing.Optional[typing.List[str]]:
        """Get AWS account aliases."""
        aliases = self.iam.list_account_aliases()
        return aliases and aliases.get("AccountAliases")

    @property
    def account_alias(self) -> typing.Optional[str]:
        """Get primary AWS account alias."""
        aliases = self.account_aliases
        return aliases[0] if aliases else None

    @property
    def caller_id(self) -> dict:
        """Get caller identity from STS."""
        return self.sts.get_caller_identity()

    @property
    def account_id(self) -> typing.Optional[str]:
        """Get AWS account ID."""
        return self.caller_id.get("Account")

    @property
    def region_name(self) -> typing.Optional[str]:
        """Returns the AWS region name."""
        # Check config first, then existing session (use _session to avoid recursion)
        return self.config.get("region_name") or getattr(
            self._session, "region_name", None
        )

    region = region_name

    def __init__(self, config: typing.Optional[dict] = None, **kwargs):
        config = config or {}
        if not isinstance(config, dict):
            raise ValueError(f"expected dict for `config`, got {type(config)}")
        self.config = config
        self.name = self.config.get("name", "default")
        self.logger_name = f"<Env@{self.name}>"
        self._session = None
        self._ssm = None
        self._iam = None
        self._sts = None
        super().__init__(**kwargs)

    @property
    def session(self) -> boto3.session.Session:
        """Lazily create boto3 session."""
        if self._session is None:
            self._session = boto3.session.Session(
                profile_name=self.profile_name,
                region_name=self.region_name,
            )
        return self._session

    @property
    def ssm(self):
        """Lazily create SSM client with retry configuration."""
        if self._ssm is None:
            self._ssm = self.session.client("ssm", config=BOTO_CONFIG)
        return self._ssm

    @property
    def iam(self):
        """Lazily create IAM client with retry configuration."""
        if self._iam is None:
            self._iam = self.session.client("iam", config=BOTO_CONFIG)
        return self._iam

    @property
    def sts(self):
        """Lazily create STS client with retry configuration."""
        if self._sts is None:
            self._sts = self.session.client("sts", config=BOTO_CONFIG)
        return self._sts

    @property
    def user_names(self) -> typing.List[str]:
        """Get IAM usernames for this environment."""
        self.logger.debug("computing IAM usernames for this environment")
        return [u["UserName"] for u in self.iam.list_users()["Users"]]

    @property
    def role_names(self) -> typing.List[str]:
        """Get IAM role names for this environment."""
        self.logger.debug("computing IAM roles for this environment")
        return [u["RoleName"] for u in self.iam.list_roles()["Roles"]]

    def has_role(self, name: str) -> bool:
        """Check if IAM role exists."""
        return name in self.role_names

    def has_user(self, name: str) -> bool:
        """Check if IAM user exists."""
        return name in self.user_names

    def __eq__(self, other) -> bool:
        """Environments are equal if their names are equal."""
        return isinstance(other, self.__class__) and self.name == other.name

    def __hash__(self) -> int:
        return hash(self.name)

    def __ne__(self, other) -> bool:
        """Opposite of self==other."""
        return not self == other

    def __str__(self) -> str:
        """Human-friendly string representation."""
        return f"<Environment `{self.profile_name}`>"

    __repr__ = __str__

    @functools.cached_property
    def secrets(self) -> SecretManager:
        """
        Returns a SecretManager for this environment.
        Cached to avoid creating multiple instances.
        """
        return SecretManager(env=self)
