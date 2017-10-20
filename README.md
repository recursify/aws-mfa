# Installation

You will need Python 2 or 3 and the `boto3` package.

```
$ pip install boto3
```

# Typical Usage

Your `~/.aws/credentials` file will look something like:

```
[alice]
aws_access_key_id = FOOACCESSKEY
aws_secret_access_key = FOOSECRETKEY
```

Notice that there is no `default` profile.

Now, we invoke the `aws_mfa.py` command to fetch temporary access
tokens and fill in the `default` profile:

```
$ python aws_mfa.py -m arn:aws:iam::123456789:mfa/alice -p alice \
        write --output-profile=default
```

It will ask for your MFA code at this point.  Open up Google
Authenticator and put in your 6 digit access code.  Your
`~/.aws/credential` file should now look like:

```
[default]
aws_access_key_id = TEMPACCESSKEY
aws_secret_access_key = SECRETKEY
aws_session_token = BIGLONGSESSIONTOKEN

[alice]
aws_access_key_id = FOOACCESSKEY
aws_secret_access_key = FOOSECRETKEY
```

You can now use the AWS CLI, which should assume the default role.
