# -*- coding: utf-8 -*-
""" ssm.api.environment

Core abstraction for environment-aware boto, which
reduces a lot of boilerplate with boto sessions/profiles
"""

from __future__ import absolute_import
from __future__ import division
import collections

import six
import boto3
import botocore

from ssm import (abcs, util,)

from .manager import SecretManager

# default logger only used for class-methods,
# because for this there is no instance is available
LOGGER = util.get_logger(__name__)


class Environment(abcs.Loggable,):
    """ """
    @staticmethod
    def normalize_env_name(name):
        """ """
        return name
    @classmethod
    def from_profile(cls, name):
        """
        instantiates an Environment from AWS profile name,
        preferably something like 'dev', or 'datacenter1',
        or 'prod'.
        """
        assert isinstance(name, six.string_types), type(name)
        normal_name = Environment.normalize_env_name(name)
        try:
            config = cls.ENV_CONFIGS[normal_name]
        except KeyError:
            err = "no such environment name `{}` found inside config:\n  {}"
            raise KeyError(err.format(normal_name, cls.ENV_CONFIGS))
        return cls(config=config)

    @property
    def profile_name(self):
        """
        returns the default profile name from config
        """
        return self.config.get('profile_name')
    profile = profile_name

    @property
    def account_id(self):
        return self.config.get('account_id')
    account = account_id

    @property
    def region_name(self):
        """
        returns the default region name from config
        """
        return self.config.get('region_name') or \
            getattr(
                getattr(self,'session', None),
                'region_name', None)
    region = region_name

    def __init__(self, config={}, **kwargs):
        if not isinstance(config, dict):
            err = 'expected dict for `config`, got {}'
            raise ValueError(err.format(config))
        self.config = config
        self.name = self.config['name']
        self.logger_name = "A[{}]".format(self.name)
        self.init_session()
        super(Environment, self).__init__(**kwargs)

    def get_boto(self, client_type):
        """
        get a classic boto client.  this is still
        necessary for example with some route53 operations
        """
        import boto
        fxn = getattr(boto, 'connect_{}'.format(client_type))
        creds = self.session.get_credentials()
        return fxn(
            aws_access_key_id=creds.access_key,
            aws_secret_access_key=creds.secret_key,
            security_token=creds.token,)

    def init_session(self):
        """
        initializes boto session and various service handles
        """
        self.session = boto3.session.Session(
            profile_name=self.profile_name,
            region_name=self.region_name)
        self.s3 = self.session.client('s3')
        self.ec2 = self.session.client('ec2')
        self.emr = self.session.client('emr')
        self.ssm = self.session.client('ssm')
        self.iam = self.session.client('iam')
        self.sts = self.session.client('sts')
        self.cloudwatch = self.session.client('cloudwatch')
        self.route53 = self.session.client('route53')
        # always us-east-1
        self.support = boto3.session.Session(
            profile_name=self.profile_name,
            region_name='us-east-1').client('support')
        self.redshift = self.session.client('redshift')
        self.cloudformation = self.session.client('cloudformation')

    @property
    def user_names(self):
        """  """
        self.logger.debug("computing IAM usernames for this environment")
        return [ u['UserName'] for u in self.iam.list_users()['Users']  ]

    @property
    def role_names(self):
        """  """
        self.logger.debug("computing IAM roles for this environment")
        return [ u['RoleName'] for u in self.iam.list_roles()['Roles']  ]

    def has_role(self,  name):
        """ """
        return name in self.role_names

    def has_user(self,name):
        """ """
        return name in self.user_names

    def __eq__(self, other):
        """ environments are equal if their names are equal """
        return all([
            isinstance(other, (self.__class__,)),
            self.name == other.name])

    def __hash__(self):
        return hash(self.name)

    def __ne__(self, other):
        """ opposite of self==other, otherwise this would use obj id's """
        return not self == other

    def __str__(self):
        """
        human friendly strings for things like console
        output, i.e. with `secrets shell`, or logging
        """
        return "<Environment: {} @ {}>".format(self.name, self.profile_name)
    __repr__ = __str__

    @property
    def secrets(self):
        """
        returns a secrets manager for this session
        (see ssm for more info)
        """
        return SecretManager(env=self)


from botocore import session;
Environment.ENV_CONFIGS = collections.OrderedDict()
Environment.ALL_PROFS = session.Session().available_profiles
tmp="loading environments from {} available profiles.."
LOGGER.debug(tmp.format(len(Environment.ALL_PROFS)))
for profile_name in Environment.ALL_PROFS:
    # LOGGER.debug("\t{}".format(profile_name))
    Environment.ENV_CONFIGS[profile_name] = dict(
        profile_name=profile_name,
    )
LOGGER.debug("normalizing and pre-computing env metadata")
for env_name, env_config in Environment.ENV_CONFIGS.copy().items():
    LOGGER.debug("\t- {}".format(env_name))
    env_config['name'] = Environment.normalize_env_name(env_name)
LOGGER.debug("done loading environment configs")
