""" ssm.api.manager
"""

import typing

import botocore

from .. import abcs

__all__ = ["SecretManager", "DEFAULT_KMS_ID"]

DEFAULT_KMS_ID = "alias/default"  # don't change this


class SecretManager(abcs.Loggable):
    """
    Manages SSM Parameter Store secrets with a dict-like interface.

    Supports:
    - Dict-like access: secrets[name], secrets[name] = value, del secrets[name]
    - Bulk operations: keys(), items(), under(prefix), children(prefix)
    - Parameter types: SecureString (default), String, StringList
    """

    def __init__(self, env=None, **kwargs):
        assert env is not None
        self.env = env
        self.logger_name = f"<Secrets[{self.env.logger_name}]>"
        super().__init__(**kwargs)

    def __getitem__(self, name: str) -> str:
        """dictionary compatibility: secrets['name']"""
        try:
            return self.env.ssm.get_parameter(Name=name, WithDecryption=True)[
                "Parameter"
            ]["Value"]
        except self.env.ssm.exceptions.ParameterNotFound:
            raise KeyError(name)
        except botocore.exceptions.ClientError:
            self.env.logger.warning(f"Can't retrieve key `{name}`.")
            self.env.logger.warning(
                "Either it does not exist, or it is a hierarchy and not a leaf"
            )
            raise TypeError(name)

    def __delitem__(self, name: str) -> dict:
        """ex: del secrets['foo']"""
        return self.env.ssm.delete_parameter(Name=name)

    def __setitem__(self, name: str, value: str) -> dict:
        """dictionary compatibility: secrets['name'] = 'value'"""
        return self.set_secret(name=name, value=value, description=name)

    def __contains__(self, name: str) -> bool:
        """Check if parameter exists: 'name' in secrets"""
        try:
            self.env.ssm.get_parameter(Name=name)
            return True
        except (self.env.ssm.exceptions.ParameterNotFound, botocore.exceptions.ClientError):
            return False

    def set_secret(
        self,
        name: str,
        value: str,
        description: typing.Optional[str] = None,
        kms_id: str = DEFAULT_KMS_ID,
        param_type: str = "SecureString",
    ) -> dict:
        """
        Create or update a parameter.

        Args:
            name: Parameter path/name
            value: Parameter value
            description: Optional description (defaults to name)
            kms_id: KMS key ID for encryption (only for SecureString)
            param_type: One of 'SecureString', 'String', 'StringList'

        Returns:
            AWS API response dict
        """
        assert name and value, "cannot set secret without passing name and value"
        description = description or name

        # Validate param_type
        valid_types = ("SecureString", "String", "StringList")
        if param_type not in valid_types:
            raise ValueError(f"param_type must be one of {valid_types}, got {param_type}")

        try:
            params = dict(
                Name=name,
                Value=value,
                Description=description,
                Type=param_type,
                Tier="Advanced",
                Overwrite=True,
            )
            # Only include KeyId for SecureString
            if param_type == "SecureString":
                params["KeyId"] = kms_id

            return self.env.ssm.put_parameter(**params)
        except botocore.exceptions.ClientError as exc:
            err = f"could not set secret `{name}`: {exc}"
            self.logger.critical(err)
            raise

    def items(self) -> typing.Dict[str, str]:
        """dictionary compatibility: returns all parameters as {name: value}"""
        return {key: self[key] for key in self.keys()}

    @staticmethod
    def _unpack_pager_with_values(pages) -> typing.Dict[str, str]:
        """Unpack paginator results that include Values (get_parameters_by_path)"""
        out = []
        for p in pages:
            out.extend(p["Parameters"])
        return {x["Name"]: x["Value"] for x in out}

    @staticmethod
    def _unpack_pager_names_only(pages) -> typing.List[str]:
        """Unpack paginator results for names only (describe_parameters)"""
        out = []
        for p in pages:
            out.extend(param["Name"] for param in p["Parameters"])
        return out

    def children(
        self,
        path_prefix: str,
        flat_output: bool = False,
    ) -> typing.List[str]:
        """
        Get intermediate paths (directories) under the given prefix.
        Does not return leaf nodes, only intermediate path components.
        """
        leafs = self.under(path_prefix)
        acc = []
        for k in leafs:
            tmp = k[len(path_prefix) :].split("/")[:-1]
            for i, _ in enumerate(tmp):
                j = "/".join(tmp[: i + 1])
                if not flat_output:
                    j = path_prefix + j
                if j not in acc:
                    acc.append(j)
        return acc

    def under(self, path_prefix: str) -> typing.Dict[str, str]:
        """
        Returns a dictionary of {name: value} for everything under `path_prefix`.
        Recursively fetches all parameters below the given path.
        """
        self.logger.debug(f"lookup: {path_prefix}")
        paginator = self.env.ssm.get_paginator("get_parameters_by_path")
        pages = paginator.paginate(
            Path=path_prefix, Recursive=True, WithDecryption=True
        )
        return self._unpack_pager_with_values(pages)

    __mod__ = under

    def keys(self, path_prefix: str = "/") -> typing.List[str]:
        """
        Dictionary compatibility: returns list of all parameter names.
        Uses describe_parameters which returns metadata (no values).
        """
        self.logger.debug(f"looking up all SSM keys under {path_prefix}")
        paginator = self.env.ssm.get_paginator("describe_parameters")
        pager = paginator.paginate(
            ParameterFilters=[
                dict(
                    Key="Path",
                    Option="Recursive",
                    Values=[path_prefix],
                )
            ]
        )
        return self._unpack_pager_names_only(pager)
