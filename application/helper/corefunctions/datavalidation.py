import datetime
import subprocess

from flask import current_app
from flask import current_app as app

from application.common.constants import SupportedDBType
from index import basedir


def datavalidation(source_db, source_table, src_db_type, des_db,
                   des_table, des_db_type,
                   source_name, source_password, source_hostname,
                   destination_name, destination_password,
                   destination_hostname, srcqry, targetqry, case_log):
    """
    DataValidation function will submit the job to spark and execute the job

    Args:
        source_db: source_db of case
        source_table: source_table of case
        src_db_type: src_db_type of case
        des_db: des_db of case
        des_table: des_db of case
        des_db_type: des_db of case
        source_name: source_name of case
        source_password: source_password of case
        source_hostname: source_hostname of case
        destination_name: destination_name of case
        destination_password: destination_password of case
        destination_hostname: destination_hostname of case
        srcqry: srcqry of case
        targetqry: targetqry of case
        case_log: case_log of case

    Returns: Submit the Job to spark

    """
    api_end_point = "datavalidation=" + current_app.config.get(
        'API_END_POINT') + "/api/spark-job-status/{0}".format(
        case_log.test_case_log_id)
    driver_mem = current_app.config.get('DRIVER_MEMORY')
    executor_mem = current_app.config.get('EXECUTOR_MEMORY')
    sqljdbc = basedir + "/spark/sqljdbc42.jar"
    mysql_connector = basedir + "/spark/mysql-connector-java.jar"
    postgres_connector = basedir + "/spark/postgresql-42.2.5.jar"
    oracle_db_connector = basedir + "/spark/ojdbc6.jar"
    py_spark_file = basedir + current_app.config.get('SPARK_FILE')
    src_record_count = current_app.config.get('SPARK_SOURCE_RECORDS_COUNT')
    target_record_count = current_app.config.get('SPARK_TARGET_RECORDS_COUNT')
    thread_count = current_app.config.get('SPARK_THREAD_COUNT')
    app.logger.info(
        "Data validation Job start at = {}".format(datetime.datetime.now()))

    subprocess.check_output(
        'spark-submit --driver-memory {0} '
        '--executor-memory {1} --jars {2},{3},{4},{5}'
        ' {6} {7} {8} {9} {10} {11} {12} '
        '{13} {14} {15} {16} {17} {18} {19} {20} {21} {22} {23} {24}'.format(
            driver_mem, executor_mem,
            sqljdbc, mysql_connector,
            postgres_connector,
            oracle_db_connector,
            py_spark_file,
            source_hostname,
            source_name,
            source_password,
            source_db, source_table,
            SupportedDBType().get_db_name_by_id(src_db_type),
            destination_hostname,
            destination_name,
            destination_password,
            des_db, des_table,
            SupportedDBType().get_db_name_by_id(des_db_type),
            '"{0}"'.format(srcqry if srcqry else str(None)),
            '"{0}"'.format(targetqry if targetqry else str(None)),
            str(src_record_count),
            str(target_record_count),
            str(thread_count),
            api_end_point),
        shell=True, universal_newlines=False)
    app.logger.debug(str(datetime.datetime.now()))


def manage_none_value(diff_result, column_list):
    """
    To handle None values,it appends Null to the missing column name in the
    result.

    Args:
        diff_result(list):Result of the datavalidation.
        column_list(list):List of column names of the table.

    Returns:
        Return the list of dictionaries with processed data.
    """
    processed_data = list()
    for each_dict in diff_result:
        temp_dict = dict()
        for each_key in column_list:
            temp_dict[each_key] = each_dict.get(each_key, None)
        processed_data.append(temp_dict)
    return processed_data
