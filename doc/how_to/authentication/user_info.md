# Accessing User information

## User State

Once a user is authorized with the chosen OAuth provider certain user information and an `access_token` will be available to be used in the application to customize the user experience. Like all other global state this may be accessed on the `pn.state` object, specifically it makes three attributes available:

* **`pn.state.user`**: A unique name, email or ID that identifies the user.
* **`pn.state.access_token`**: The access token issued by the OAuth provider to authorize requests to its APIs.
* **`pn.state.refresh_token`**: The refresh token issued by the OAuth provider to authorize requests to its APIs (if available these are usually longer lived than the `access_token`).
* **`pn.state.user_info`**: Additional user information provided by the OAuth provider. This may include names, email, APIs to request further user information, IDs and more.

## Authorization callbacks

The OAuth providers integrated with Panel provide an easy way to enable authentication on your applications. This verifies the identity of a user and also provides some level of access control (i.e. authorization). However often times the OAuth configuration is controlled by a corporate IT department or is otherwise difficult to manage so its often easier to grant permissions to use the OAuth provider freely but then restrict access controls in the application itself. To manage access you can provide an `authorization_callback` as part of your applications.

The `authorization_callback` can be configured on `pn.config` or via the `pn.extension`:

```python
import panel as pn

def authorize(user_info):
    with open('users.txt') as f:
        valid_users = f.readlines()
    return user_info['username'] in valid_users

pn.config.authorize_callback = authorize # or pn.extension(..., authorize_callback=authorize)
```

The `authorize_callback` is given a dictionary containing the data in the OAuth provider's `id_token`. The example above checks whether the current user is in the list of users specified in a `user.txt` file. However you can implement whatever logic you want to either grant a user access or reject it.

If a user is not authorized they will be presented with a authorization error template which can be configured using the `--auth-template` commandline option or by setting `config.auth_template`.

<img src="../../_static/authorization.png" width="600" style="margin-left: auto; margin-right: auto; display: block;"></img>

The auth template must be a valid Jinja2 template and accepts a number of arguments:

- `{{ title }}`: The page title.
- `{{ error_type }}`: The type of error.
- `{{ error }}`: A short description of the error.
- `{{ error_msg }}`: A full description of the error.
