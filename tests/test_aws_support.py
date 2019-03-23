"""Tests for the AWS environment support functions in the soong package."""

import os

import boto3

import soong


def test_is_not_running_in_lambda_cloud():
    assert not soong.is_running_in_lambda()


def test_is_running_in_mock_lambda_cloud(monkeypatch):
    with monkeypatch.context() as mp:
        mp.setattr(os, 'environ', {'AWS_EXECUTION_ENV': 'AWS_Lambda_python3.7'})
        assert soong.is_running_in_lambda()


def test_is_running_in_mock_sam_local(monkeypatch):
    with monkeypatch.context() as mp:
        mp.setattr(os, 'environ', {'AWS_EXECUTION_ENV': 'AWS_Lambda_python3.7'})
        mp.setattr(os, 'environ', {'AWS_SAM_LOCAL': 'true'})
        assert not soong.is_running_in_lambda()


def test_get_iam_token(mocker):
    rds_mock = mocker.Mock()
    rds_mock.generate_db_auth_token.return_value = 'token123'
    mocker.patch.object(boto3, 'client', return_value=rds_mock)

    dsn = dict(host='test_host', port=1234, user='test_user')
    assert soong.get_iam_token(dsn) == 'token123'
    rds_mock.generate_db_auth_token.assert_called_once_with(*dsn.values())


def test_connect_in_mock_lambda(mocker, monkeypatch):
    conn_mock = mocker.Mock()
    mocker.patch('psycopg2.connect', new=conn_mock)
    mocker.patch('soong.get_iam_token', return_value='token123')
    env = {'AWS_EXECUTION_ENV': 'AWS_Lambda_python3.7',
           'PG_HOST': 'eqtr-pg1.abcde123.us-east-1.rds.amazonaws.com',
           'PG_DBNAME': 'equitir',
           'PG_USER': 'equitir'}
    with monkeypatch.context() as mp:
        mp.setattr(os, 'environ', env)
        soong.connect()

    conn_mock.assert_called_with(
        host=env['PG_HOST'], hostaddr=None, port=5432, connect_timeout=30,
        dbname=env['PG_DBNAME'], user=env['PG_USER'], password='token123',
        connection_factory=None, cursor_factory=None)
