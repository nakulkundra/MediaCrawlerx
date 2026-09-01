# -*- coding: utf-8 -*-
# Copyright (c) 2025 relakkes@gmail.com
#
# This file is part of MediaCrawler project.
# Repository: https://github.com/NanmiCoder/MediaCrawler/blob/main/test/test_db_sync.py
# GitHub: https://github.com/NanmiCoder
# Licensed under NON-COMMERCIAL LEARNING LICENSE 1.1

"""
Compares ORM mapping models (database/models.py) with actual database schema
and performs difference reporting / synchronization.
"""

import os
import sys
from sqlalchemy import create_engine, inspect as sqlalchemy_inspect
from sqlalchemy.schema import MetaData

# Add project root directory to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.db_config import mysql_db_config, sqlite_db_config
from database.models import Base


def get_mysql_engine():
    """Create and return a MySQL database engine"""
    conn_str = f"mysql+pymysql://{mysql_db_config['user']}:{mysql_db_config['password']}@{mysql_db_config['host']}:{mysql_db_config['port']}/{mysql_db_config['db_name']}"
    return create_engine(conn_str)


def get_sqlite_engine():
    """Create and return a SQLite database engine"""
    conn_str = f"sqlite:///{sqlite_db_config['db_path']}"
    return create_engine(conn_str)


def get_db_schema(engine):
    """Get current table structure of the database"""
    inspector = sqlalchemy_inspect(engine)
    schema = {}
    for table_name in inspector.get_table_names():
        columns = {}
        for column in inspector.get_columns(table_name):
            columns[column['name']] = str(column['type'])
        schema[table_name] = columns
    return schema


def get_orm_schema():
    """Get table structure of ORM model"""
    schema = {}
    for table_name, table in Base.metadata.tables.items():
        columns = {}
        for column in table.columns:
            columns[column.name] = str(column.type)
        schema[table_name] = columns
    return schema


def compare_schemas(db_schema, orm_schema):
    """Compare database structure with ORM model structure and return differences"""
    db_tables = set(db_schema.keys())
    orm_tables = set(orm_schema.keys())

    added_tables = orm_tables - db_tables
    deleted_tables = db_tables - orm_tables
    common_tables = db_tables.intersection(orm_tables)

    changed_tables = {}
    for table in common_tables:
        db_cols = db_schema[table]
        orm_cols = orm_schema[table]

        added_cols = set(orm_cols.keys()) - set(db_cols.keys())
        deleted_cols = set(db_cols.keys()) - set(orm_cols.keys())
        common_cols = set(db_cols.keys()).intersection(set(orm_cols.keys()))

        type_diffs = {}
        for col in common_cols:
            if db_cols[col].lower() != orm_cols[col].lower():
                type_diffs[col] = {"db": db_cols[col], "orm": orm_cols[col]}

        if added_cols or deleted_cols or type_diffs:
            changed_tables[table] = {
                "added_columns": added_cols,
                "deleted_columns": deleted_cols,
                "type_differences": type_diffs,
            }

    return {
        "added_tables": added_tables,
        "deleted_tables": deleted_tables,
        "changed_tables": changed_tables,
    }
