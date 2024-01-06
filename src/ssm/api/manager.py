""" ssm.api.manager
"""

import botocore

from .. import abcs

DEFAULT_KMS_ID = "alias/default"  # don't change this


class SecretManager(abcs.Loggable):
    """ """

    def __init__(self, env=None, **kwargs):
        assert env is not None
        self.env = env
        self.logger_name = f"<Secrets[{self.env.logger_name}]>"
        super().__init__(**kwargs)

    def __getitem__(self, name):
        """dictionary compatability"""
        try:
            return self.env.ssm.get_parameter(Name=name, WithDecryption=True)[
                "Parameter"
            ]["Value"]
        except self.env.ssm.exceptions.ParameterNotFound as exc:
            raise KeyError(name)
        except botocore.exceptions.ClientError as exc:
            self.env.logger.warning(f"Can't retrieve key `{name}`.")
            self.env.logger.warning(
                "Either it does not exist, or it is a hiearchy and not a leaf"
            )
            raise TypeError(name)

    def __delitem__(self, name):
        """ex: del secrets['foo']"""
        return self.env.ssm.delete_parameter(Name=name)

    def __setitem__(self, name, value):
        """dictionary compatability"""
        return self.set_secret(name=name, value=value, description=name)

    def set_secret(
        self, name=None, value=None, description=None, kms_id=DEFAULT_KMS_ID
    ):
        """ """
        assert name and value, "cannot set secret without passing name and value"
        description = description or name
        try:
            return self.env.ssm.put_parameter(
                Name=name,
                Value=value,
                Description=description,
                Type="SecureString",
                KeyId=kms_id,
                Tier="Advanced",
                Overwrite=True,
            )
        except botocore.exceptions.ClientError as exc:
            err = "could not set secret `{}` with locals: {}"
            self.logger.critical(err.format(name, locals()))
            raise

    def items(self):
        """dictionary compatability"""
        return {key: self[key] for key in self.keys()}

    @staticmethod
    def _unpack_pager(pages) -> dict:
        """ """
        out = []
        for p in pages:
            out.extend(p["Parameters"])
        out = {x["Name"]: x["Value"] for x in out}
        return out

    def children(
        self,
        path_prefix,
        flat_output: bool = False,
    ) -> list:
        """ """
        leafs = self.under(path_prefix)
        acc = []
        for k in leafs:
            tmp = k[len(path_prefix) :].split("/")[:-1]
            for i, c in enumerate(tmp):
                j = "/".join(tmp[: i + 1])
                if not flat_output:
                    j = path_prefix + j
                if j not in acc:
                    acc.append(j)
        return acc

    def under(self, path_prefix) -> dict:
        """
        returns a dictionary of {k:v} for everything under `path_prefix`
        """
        self.logger.debug(f"lookup: {path_prefix}")
        paginator = self.env.ssm.get_paginator("get_parameters_by_path")
        pages = paginator.paginate(
            Path=path_prefix, Recursive=True, WithDecryption=True
        )
        return self._unpack_pager(pages)

    __mod__ = under

    def keys(self, under=None):
        """dictionary compatability"""
        self.logger.debug("looking up all SSM keys")
        paginator = self.env.ssm.get_paginator("describe_parameters")
        pager = paginator.paginate(
            ParameterFilters=[
                dict(
                    Key="Path",
                    Option="Recursive",
                    Values=["/"],
                )
            ]
        )
        return self._unpack_pager(pager).keys()
