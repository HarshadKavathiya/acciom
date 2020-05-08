from flask import current_app
from flask import render_template
from flask_mail import Message, Mail
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from passlib.hash import pbkdf2_sha256 as sha256

from application.common.constants import APIMessages
from application.model.models import DbConnection
from application.model.models import User, TestSuite, TestCase
from index import app


def validate_empty_fields(data_json, list_of_args):
    """
    Validate the fields provided by user is empty or not on request payload.

    Args:
        data_json(dict): Dictionary of payload sent by user
        list_of_args(list): list of arguments that are expected by system

    Returns(str): Message in case of empty string
    """
    for each_arg in list_of_args:
        if not (data_json[each_arg]):
            # Checking if fields are empty
            return APIMessages.EMPTY_FIELD.format(each_arg)


def get_table_name(table_names):
    """
      To generate dictinory containing source and target table names.

    Args:
        table_names(dic):Dictinory with source table name as key and target
        table name as value.

    Returns:
          Returns a dictionary contains source table and target table names
          as values for the keys src_table and target_table.
    """
    table_names_dic = {}
    for key in table_names:
        table_names_dic['src_table'] = key
        table_names_dic['target_table'] = table_names[key]
    return table_names_dic


def db_details_without_password(db_connection_id):
    """
    To generate a dictionary for data base details.

    Args:
        db_connection_id(int):data base connection id.

    Returns:
         Returns a dictionary containing data base details for a particular
         data base connection id.
    """
    db_details_list = {}
    db_obj = DbConnection.query.filter_by(
        db_connection_id=db_connection_id).first()
    db_details_list['db_connection_id'] = db_obj.db_connection_id
    db_details_list['db_type'] = db_obj.db_type
    db_details_list['db_name'] = db_obj.db_name
    db_details_list['db_hostname'] = db_obj.db_hostname
    db_details_list['db_username'] = db_obj.db_username
    db_details_list['db_connection_name'] = db_obj.db_connection_name
    return db_details_list


def send_reset_email(user):
    """
    To send Email to the user to reset password.

    Args:
        user(object):By using this object we can get the user information.

    Returns:
        Mail send to the user.
    """
    mail = Mail(app)
    token = user.get_reset_token()
    msg = Message('Password Reset Request',
                  sender=("Acciom", app.config.get('MAIL_USERNAME')),
                  recipients=[user.email])
    msg_link = str(app.config.get('API_END_POINT') + app.config.get(
        'UI_RESET_PASSWORD_PATH') + token)
    msg.html = render_template("email_reset_password.html", links=msg_link,
                               name=user.first_name, email=user.email,
                               emailnoreplay='<noreplay@accionlabs.com>')
    # api.url_for(ResetPassword, token=token, _external=True)
    mail.send(msg)


def verify_reset_token(token):
    """
    To verify the token provided by the user.

    Args:
        token(str):token to verify.

    Returns:
        It returns user_id of the user provided token.
    """
    s = Serializer(current_app.config.get('SECRET_KEY'))
    try:
        user_id = s.loads(token)['user_id']
    except Exception as e:
        app.logger.error(e)
        return None
    return User.query.get(user_id)


def verify_hash(userpassword, password_in_db):
    """
       To verify whether the password entered by the user and password in db
       are matching or not.

    Args:
        userpassword(str): Old Password entered by the user.
        password_in_db(str): Password in db.

    Returns:
        It returns true if both the passwords matches.
    """
    return sha256.verify(userpassword, password_in_db)


def generate_hash(userpassword):
    """
     To generate hash password.

    Args:
        userpassword(str):New Password entered by the user.

    Returns:
        It returns hashed password for the new password enter by the user.
    """
    return sha256.hash(userpassword)


def return_excel_name_and_project_id(test_case_id):
    """
    It takes test case id and gives the excelname and project id for the
    particular test case id.

    Args:
        test_case_id(int):test case id.

    Returns:
    The excel name and project id.
    """

    def test_suite_to_json(test_suite):
        return {
            'excel_name': test_suite.excel_name,
            'project_id': test_suite.project_id
        }

    def test_case_to_json(test_case):
        return {
            'test_suite_id': list(
                map(lambda test_suite: test_suite_to_json(test_suite),
                    TestSuite.query.
                    filter(
                        TestSuite.test_suite_id == test_case.test_suite_id,
                        TestSuite.is_deleted == False)))}

    return {'user': list(map(lambda test_case: test_case_to_json(test_case),
                             TestCase.query.filter(
                                 TestCase.test_case_id == test_case_id,
                                 TestCase.is_deleted == False)))}
