## API for 'aws-ssm-tool' package

---------------------------------------------------------------------------------------------------------------------------------------------------------------
### ssm
* **Overview:**  [source code](/src/ssm/__init__.py), [unit tests](/tests/units/), [integration tests](/tests/integrations/)
* **Names:** (5 total)::
  *  *abcs*, *util*, *bin*, *cli*, *api*
-------------------------------------------------------------------------------
### ssm.abcs
* **Overview:**  [source code](/src/ssm/abcs/__init__.py), [unit tests](/tests/units/), [integration tests](/tests/integrations/)
* **Names:** (2 total)::
  *  *Loggable*, *loggable*
-------------------------------------------------------------------------------
### ssm.abcs.loggable
* **Overview:**  [source code](/src/ssm/abcs/loggable.py), [unit tests](/tests/units/), [integration tests](/tests/integrations/)
* **Classes:** (1 total)
  * [`ssm.abcs.loggable.Loggable`](/src/ssm/abcs/loggable.py#L8-L19)
    * with bases ([`__builtin__.object`](https://docs.python.org/3/library/functions.html#object),)
-------------------------------------------------------------------------------
### ssm.util
* **Overview:**  [source code](/src/ssm/util/__init__.py), [unit tests](/tests/units/), [integration tests](/tests/integrations/)
* **Functions:** (5 total)
  * [`ssm.util.fatal_error`](/src/ssm/util/__init__.py#L49-L52) with signature `(msg)`
  * [`ssm.util.flatten_output`](/src/ssm/util/__init__.py#L40-L46) with signature `(result: dict) -> dict`
  * [`ssm.util.get_logger`](/src/ssm/util/__init__.py#L55-L94) with signature `(name)`
  * [`ssm.util.is_string`](/src/ssm/util/__init__.py#L35-L37) with signature `(obj) -> bool`
  * [`ssm.util.rich_walk_dict`](/src/ssm/util/__init__.py#L20-L32)
    * with signature `(dct, tree: rich.tree.Tree, branch_color='[bold magenta]') -> None`
-------------------------------------------------------------------------------
### ssm.bin
* **Overview:**  [source code](/src/ssm/bin/__init__.py), [unit tests](/tests/units/), [integration tests](/tests/integrations/)
* **Names:** (1 total)::
  *  *ssm*
-------------------------------------------------------------------------------
### ssm.bin.ssm
* **Overview:**  [source code](/src/ssm/bin/ssm.py), [unit tests](/tests/units/), [integration tests](/tests/integrations/)
* **Functions:** (1 total)
  * [`ssm.bin.ssm.entry`](/src/ssm/bin/ssm.py#L18-L23) with signature `(*args: Any, **kwargs: Any) -> Any`
-------------------------------------------------------------------------------
### ssm.cli
* **Overview:**  [source code](/src/ssm/cli/__init__.py), [unit tests](/tests/units/), [integration tests](/tests/integrations/)
* **Classes:** (1 total)
  * [`ssm.cli.Group`](/src/ssm/cli/__init__.py#L13-L55)
    * with bases ([Group](#clickcore),)
-------------------------------------------------------------------------------
### ssm.cli.options
* **Overview:**  [source code](/src/ssm/cli/options.py), [unit tests](/tests/units/), [integration tests](/tests/integrations/)
* **Names:** (45 total)::
  *  *partial*, *click*, *key*, *top*, *existing_file*, *filter_service_partial*, *filter_service*, *output_format_partial*, *output_format*, *format*, *output_format_yaml_default*, *output_format_json_default*, *output_format_stdout_default*, *output_format_tree_default*, *optional_user*, *user*, *optional_users*, *users*, *raw*, *force_or_dry*, *force*, *dry_run*, *pause_or_nowait*, *no_wait*, *pause*, *optional_prefix*, *cascade_partial*, *cascade*, *no_cascade*, *flat_output*, *dirs_only*, *caller_context*, *profile_partial*, *src_profile_partial*, *dst_profile_partial*, *required_profile*, *profile*, *default_profile*, *src_profile*, *src_profile_default*, *dst_profile*, *dst_profile_default*, *src_profile_no_default*, *dst_profile_no_default*, *src_prefix*
-------------------------------------------------------------------------------
### ssm.cli.wrapper
* **Overview:**  [source code](/src/ssm/cli/wrapper.py), [unit tests](/tests/units/), [integration tests](/tests/integrations/)
* **Classes:** (1 total)
  * [`ssm.cli.wrapper.ApiWrapper`](/src/ssm/cli/wrapper.py#L16-L138)
    * with bases ([Loggable](#ssmabcsloggable),)
    * with admonitions:  [🐉 Complex](/src/ssm/cli/wrapper.py#L54 "score 16 / 7") 
-------------------------------------------------------------------------------
### ssm.cli.args
* **Overview:**  [source code](/src/ssm/cli/args.py), [unit tests](/tests/units/), [integration tests](/tests/integrations/)
* **Names:** (5 total)::
  *  *click*, *secret_name*, *path_prefix*, *namespace*, *path_prefix_default*
-------------------------------------------------------------------------------
### ssm.api
* **Overview:**  [source code](/src/ssm/api/__init__.py), [unit tests](/tests/units/), [integration tests](/tests/integrations/)
* **Functions:** (14 total)
  * [`ssm.api._get_client`](/src/ssm/api/__init__.py#L25-L30) with signature ``
  * [`ssm.api._get_env`](/src/ssm/api/__init__.py#L17-L22) with signature ``
  * [`ssm.api.copy`](/src/ssm/api/__init__.py#L191-L213)
    * with signature `(src_name, dst_name, src_profile: str = 'default', dst_profile: str = 'default', **kwargs)`
  * [`ssm.api.delete`](/src/ssm/api/__init__.py#L118-L139) with signature `(secret_name, no_backup=False, **kwargs)`
  * [`ssm.api.delete_path`](/src/ssm/api/__init__.py#L233-L235) with signature `(path_prefix, **kwargs)`
  * [`ssm.api.get_many`](/src/ssm/api/__init__.py#L107-L115) with signature `(namespace, flat_output: bool = False, **kwargs)`
  * [`ssm.api.list`](/src/ssm/api/__init__.py#L91-L104) with signature `(path_prefix, dirs_only: bool = False, **kwargs) -> List`
  * [`ssm.api.list_dirs`](/src/ssm/api/__init__.py#L82-L88) with signature `(path_prefix, **kwargs) -> List`
  * [`ssm.api.move`](/src/ssm/api/__init__.py#L142-L158)
    * with signature `(src_name, dst_name, src_profile: str = 'default', dst_profile: str = 'default', **kwargs)`
  * [`ssm.api.move_many`](/src/ssm/api/__init__.py#L161-L188)
    * with signature `(src_name, dst_name, src_profile: str = 'default', dst_profile: str = 'default', **kwargs)`
  * [`ssm.api.put_many`](/src/ssm/api/__init__.py#L238-L242) with signature `(secret_name, input_file=None, **kwargs)`
  * [`ssm.api.read`](/src/ssm/api/__init__.py#L33-L43) with signature `(secret_name, **kwargs)`
  * [`ssm.api.stat`](/src/ssm/api/__init__.py#L46-L76) with signature `(path_prefix='/', caller_context: bool = True, **kwargs)`
  * [`ssm.api.update`](/src/ssm/api/__init__.py#L216-L230) with signature `(secret_name, value, file=None, **kwargs)`
-------------------------------------------------------------------------------
### ssm.api.environment
* **Overview:**  [source code](/src/ssm/api/environment.py), [unit tests](/tests/units/), [integration tests](/tests/integrations/)
* **Classes:** (1 total)
  * [`ssm.api.environment.Environment`](/src/ssm/api/environment.py#L21-L179)
    * with bases ([Loggable](#ssmabcsloggable),)
    * with properties: (11 total)
      *  [`account_alias`](/src/ssm/api/environment.py#L62) -> inspect._empty
      *  [`account_aliases`](/src/ssm/api/environment.py#L56) -> inspect._empty
      *  [`account_id`](/src/ssm/api/environment.py#L71) -> inspect._empty
      *  [`caller_id`](/src/ssm/api/environment.py#L67) -> inspect._empty
      *  [`profile`](/src/ssm/api/environment.py#L47) -> inspect._empty
      *  [`profile_name`](/src/ssm/api/environment.py#L47) -> inspect._empty
      *  [`region`](/src/ssm/api/environment.py#L75) -> inspect._empty
      *  [`region_name`](/src/ssm/api/environment.py#L75) -> inspect._empty
      *  [`role_names`](/src/ssm/api/environment.py#L139) -> inspect._empty
      *  [`secrets`](/src/ssm/api/environment.py#L173) -> inspect._empty
      *  [`user_names`](/src/ssm/api/environment.py#L133) -> inspect._empty
-------------------------------------------------------------------------------
### ssm.api.manager
* **Overview:**  [source code](/src/ssm/api/manager.py), [unit tests](/tests/units/), [integration tests](/tests/integrations/)
* **Classes:** (1 total)
  * [`ssm.api.manager.SecretManager`](/src/ssm/api/manager.py#L11-L121)
    * with bases ([Loggable](#ssmabcsloggable),)
