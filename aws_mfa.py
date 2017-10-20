import sys
import argparse
import boto3
import os
import ConfigParser
import datetime


# Python 2/3 compatible input
if hasattr(__builtins__, 'raw_input'):
    input = raw_input

def write_credential_file(args, creds):
    # Read in the existing config file
    # Kind of a hack, ConfigParser doesn't play nice with default sections
    ConfigParser.DEFAULTSECT = 'default'
    config = ConfigParser.SafeConfigParser()
    config.read([os.path.expanduser(args.credential_file)])

    # Write the new config file
    if (not config.has_section(args.output_profile) and
            args.output_profile.lower() != 'default'):
        config.add_section(args.output_profile)
    config.set(args.output_profile, 'aws_access_key_id', creds['AccessKeyId'])
    config.set(args.output_profile, 'aws_secret_access_key', creds['SecretAccessKey'])
    config.set(args.output_profile, 'aws_session_token', creds['SessionToken'])

    cred_path = os.path.expanduser(args.credential_file)
    print("Writing credentials to the profile [%s] in file: %s" % (args.output_profile, cred_path))

    yn = input('Proceed? [y/n]: ')
    if yn != 'y':
        print("exiting...")
        sys.exit(0)

    with open(cred_path, 'wb') as f:
        config.write(f)

    print("done..")

def print_credentials(creds):
    print("Run the following command in your terminal to set your temporary credentials:\n")
    print('  export AWS_ACCESS_KEY_ID="%s"' % creds['AccessKeyId'])
    print('  export AWS_SECRET_ACCESS_KEY="%s"' % creds['SecretAccessKey'])
    print('  export AWS_SESSION_TOKEN="%s"' % creds['SessionToken'])
    print("\n")
    print

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-p', '--profile',dest='profile', required=True,
                        help='Profile used to fetch temporary credentials')
    parser.add_argument('-m', '--mfa-arn',dest='mfa_arn', required=True,
                        help='ARN of the MFA device to use')
    parser.add_argument('-d', '--duration', dest='duration', type=int,
                        help='The duration, in seconds, that the credentials'
                        ' should remain valid.', default=129600)
    subparsers = parser.add_subparsers(dest='cmd')
    write_cred_cmd = subparsers.add_parser(
        'write', help='Write temporary credentials to INI file'
    )
    print_cred_cmd = subparsers.add_parser(
        'print', help='Print temporary credentials.'
    )

    write_cred_cmd.add_argument('-f', '--credential-file', dest='credential_file',
                        help='Credential file to write to', default='~/.aws/credentials')
    write_cred_cmd.add_argument('--output-profile', dest='output_profile', default='sts')

    args = parser.parse_args()

    print("Using MFA: %s" % args.mfa_arn)
    code = input('Please enter MFA code: ')

    # TODO: allow other ways of authenticating (ie: ENV var)
    session = boto3.session.Session(profile_name=args.profile)
    client = session.client('sts')
    resp = client.get_session_token(
        SerialNumber=args.mfa_arn,
        TokenCode=str(code),
        DurationSeconds=args.duration,
    )
    creds = resp['Credentials']

    if args.cmd == 'print':
        print_credentials(creds)
    elif args.cmd == 'write':
        write_credential_file(args, creds)
