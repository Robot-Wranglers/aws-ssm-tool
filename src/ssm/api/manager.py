""" ssm.api.manager
"""
from __future__ import absolute_import
import collections

import botocore

from .. import (abcs,)

DEFAULT_KMS_ID = 'alias/default' # don't change this

class SecretManager(abcs.Loggable):
    """ """

    def __init__(self, env=None, **kwargs):
        assert env is not None
        self.env = env
        self.logger_name = '{}[Secrets]'.format(repr(self.env))
        super(SecretManager, self).__init__(**kwargs)

    def __getitem__(self, name):
        """ dictionary compatability """
        try:
            return self.env.ssm.get_parameter(
                Name=name, WithDecryption=True)['Parameter']['Value']
        except self.env.ssm.exceptions.ParameterNotFound as exc:
            raise KeyError(name)

    def __delitem__(self,name):
        """ ex: del secrets['foo'] """
        return self.env.ssm.delete_parameter(Name=name)

    def __setitem__(self, name, value):
        """ dictionary compatability """
        return self.set_secret(name=name, value=value, description=name)

    def set_secret(self, name=None,value=None, description=None, kms_id=DEFAULT_KMS_ID):
        """ """
        assert name and value, 'cannot set secret without passing name and value'
        description = description or name
        try:
            return self.env.ssm.put_parameter(
                Name=name,
                Value=value,
                Description=description,
                Type='SecureString',
                KeyId=kms_id,
                Tier='Advanced',
                Overwrite=True)
        except botocore.exceptions.ClientError as exc:
            err="could not set secret `{}` with locals: {}"
            self.logger.critical(err.format(name, locals()))
            raise


    def items(self):
        """ dictionary compatability """
        return { key: self[key] for key in self.keys() }

    @staticmethod
    def _unpack_pager(pages):
        """
        """
        out = []
        for p in pages:
            out.extend(p['Parameters'])
        out = dict([[x['Name'], x['Value']] for x in out])
        return out

    def under(self, path_prefix):
        """
        """
        self.logger.debug("looking up all SSM keys under {}".format(path_prefix))
        paginator = self.env.ssm.get_paginator('get_parameters_by_path')
        pages = paginator.paginate(
            Path=path_prefix, Recursive=True, WithDecryption=True)
        return self._unpack_pager(pages)
    __mod__ = under

    def keys(self, under=None):
        """ dictionary compatability """
        self.logger.debug("looking up all SSM keys")
        paginator = self.env.ssm.get_paginator('describe_parameters')
        pager = paginator.paginate(
            ParameterFilters=[
                dict(Key="Path", Option="Recursive",
                     Values=['/'],)])
        return self._unpack_pager(pager).keys()
