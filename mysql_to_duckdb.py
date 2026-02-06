#!/usr/bin/env python3
"""
MySQL Dump to DuckDB Converter

Converts MySQL dump files to DuckDB-compatible SQL format.
Handles:
- CREATE TABLE IF NOT EXISTS (instead of DROP TABLE)
- MySQL-specific types → DuckDB types
- Hex literals → proper BOOLEAN or BLOB based on column type
- Batched INSERT statements
- Removes MySQL-specific clauses (ENGINE, CHARSET, COLLATE, etc.)

Usage:
    python mysql_to_duckdb.py input.sql output.sql
    duckdb mydb.duckdb < output.sql
"""

import re
from pathlib import Path
from typing import Optional


"""
MySQL to DuckDB Type Mapping Reference:

NUMERIC TYPES:
  MySQL                    → DuckDB
  ─────────────────────────────────────────
  TINYINT(1)               → BOOLEAN (special case for flags)
  TINYINT                  → TINYINT (-128 to 127)
  TINYINT UNSIGNED         → UTINYINT (0 to 255)
  SMALLINT                 → SMALLINT (-32768 to 32767)
  SMALLINT UNSIGNED        → USMALLINT (0 to 65535)
  MEDIUMINT                → INTEGER (-8388608 to 8388607)
  MEDIUMINT UNSIGNED       → UINTEGER
  INT / INTEGER            → INTEGER (-2147483648 to 2147483647)
  INT UNSIGNED             → UINTEGER (0 to 4294967295)
  BIGINT                   → BIGINT
  BIGINT UNSIGNED          → UBIGINT
  DECIMAL(p,s) / NUMERIC   → DECIMAL(p,s)
  FLOAT                    → FLOAT (4 bytes)
  DOUBLE / REAL            → DOUBLE (8 bytes)
  BIT(1)                   → BOOLEAN
  BIT(n)                   → BLOB (for n > 1)

DATE/TIME TYPES:
  MySQL                    → DuckDB
  ─────────────────────────────────────────
  DATE                     → DATE
  TIME                     → TIME
  DATETIME                 → TIMESTAMP
  TIMESTAMP                → TIMESTAMP
  YEAR                     → SMALLINT

STRING TYPES:
  MySQL                    → DuckDB
  ─────────────────────────────────────────
  CHAR(n)                  → VARCHAR(n)
  VARCHAR(n)               → VARCHAR(n)
  TINYTEXT                 → TEXT (max 255 bytes)
  TEXT                     → TEXT (max 65,535 bytes)
  MEDIUMTEXT               → TEXT (max 16,777,215 bytes)
  LONGTEXT                 → TEXT (max 4,294,967,295 bytes)
  BINARY(n)                → BLOB
  VARBINARY(n)             → BLOB
  TINYBLOB                 → BLOB (max 255 bytes)
  BLOB                     → BLOB (max 65,535 bytes)
  MEDIUMBLOB               → BLOB (max 16,777,215 bytes)
  LONGBLOB                 → BLOB (max 4,294,967,295 bytes)
  ENUM('a','b',...)        → VARCHAR
  SET('a','b',...)         → VARCHAR

JSON TYPE:
  MySQL                    → DuckDB
  ─────────────────────────────────────────
  JSON                     → JSON

SPATIAL TYPES (stored as text):
  MySQL                    → DuckDB
  ─────────────────────────────────────────
  GEOMETRY                 → VARCHAR
  POINT                    → VARCHAR
  LINESTRING               → VARCHAR
  POLYGON                  → VARCHAR
  MULTIPOINT               → VARCHAR
  MULTILINESTRING          → VARCHAR
  MULTIPOLYGON             → VARCHAR
  GEOMETRYCOLLECTION       → VARCHAR
"""


def convert_mysql_type(type_str: str) -> str:
    """Convert MySQL data type to DuckDB equivalent."""
    type_str = type_str.strip()

    # Remove CHARACTER SET and COLLATE with various formats
    type_str = re.sub(r'\s*CHARACTER\s+SET\s*=?\s*[\w\-]+', '', type_str, flags=re.IGNORECASE)
    type_str = re.sub(r'\s*CHARSET\s*=?\s*[\w\-]+', '', type_str, flags=re.IGNORECASE)
    type_str = re.sub(r'\s*COLLATE\s*=?\s*[\w\-]+', '', type_str, flags=re.IGNORECASE)

    type_lower = type_str.lower()

    # Check for UNSIGNED modifier
    is_unsigned = 'unsigned' in type_lower
    type_lower = re.sub(r'\s*unsigned', '', type_lower, flags=re.IGNORECASE).strip()

    # ─────────────────────────────────────────
    # BOOLEAN special cases
    # ─────────────────────────────────────────
    if re.match(r'bit\s*\(\s*1\s*\)', type_lower):
        return 'BOOLEAN'
    if re.match(r'tinyint\s*\(\s*1\s*\)', type_lower):
        return 'BOOLEAN'
    if re.match(r'bool\b', type_lower) or re.match(r'boolean\b', type_lower):
        return 'BOOLEAN'

    # ─────────────────────────────────────────
    # BIT (n > 1) → BLOB
    # ─────────────────────────────────────────
    if re.match(r'bit\s*\(\s*(\d+)\s*\)', type_lower):
        return 'BLOB'

    # ─────────────────────────────────────────
    # INTEGER TYPES
    # ─────────────────────────────────────────
    if re.match(r'tinyint', type_lower):
        return 'UTINYINT' if is_unsigned else 'TINYINT'
    if re.match(r'smallint', type_lower):
        return 'USMALLINT' if is_unsigned else 'SMALLINT'
    if re.match(r'mediumint', type_lower):
        return 'UINTEGER' if is_unsigned else 'INTEGER'
    if re.match(r'bigint', type_lower):
        return 'UBIGINT' if is_unsigned else 'BIGINT'
    if re.match(r'int\b', type_lower) or re.match(r'integer\b', type_lower):
        return 'UINTEGER' if is_unsigned else 'INTEGER'

    # ─────────────────────────────────────────
    # DECIMAL / NUMERIC (DuckDB max precision is 38)
    # ─────────────────────────────────────────
    decimal_match = re.match(r'(?:decimal|numeric)\s*\(\s*(\d+)\s*,\s*(\d+)\s*\)', type_lower)
    if decimal_match:
        precision = min(int(decimal_match.group(1)), 38)  # Cap at 38
        scale = min(int(decimal_match.group(2)), precision)  # Scale can't exceed precision
        return f'DECIMAL({precision},{scale})'
    decimal_match = re.match(r'(?:decimal|numeric)\s*\(\s*(\d+)\s*\)', type_lower)
    if decimal_match:
        precision = min(int(decimal_match.group(1)), 38)  # Cap at 38
        return f'DECIMAL({precision},0)'
    if re.match(r'(?:decimal|numeric)\b', type_lower):
        return 'DECIMAL(10,0)'  # MySQL default

    # ─────────────────────────────────────────
    # FLOATING POINT
    # ─────────────────────────────────────────
    if re.match(r'double', type_lower) or re.match(r'real\b', type_lower):
        return 'DOUBLE'
    if re.match(r'float', type_lower):
        return 'FLOAT'

    # ─────────────────────────────────────────
    # DATE / TIME TYPES
    # ─────────────────────────────────────────
    if re.match(r'datetime', type_lower):
        return 'TIMESTAMP'
    if re.match(r'timestamp', type_lower):
        return 'TIMESTAMP'
    if re.match(r'date\b', type_lower):
        return 'DATE'
    if re.match(r'time\b', type_lower):
        return 'TIME'
    if re.match(r'year', type_lower):
        return 'SMALLINT'

    # ─────────────────────────────────────────
    # STRING TYPES
    # ─────────────────────────────────────────
    varchar_match = re.match(r'varchar\s*\(\s*(\d+)\s*\)', type_lower)
    if varchar_match:
        return f'VARCHAR({varchar_match.group(1)})'
    char_match = re.match(r'char\s*\(\s*(\d+)\s*\)', type_lower)
    if char_match:
        return f'VARCHAR({char_match.group(1)})'
    if re.match(r'varchar\b', type_lower):
        return 'VARCHAR'
    if re.match(r'char\b', type_lower):
        return 'VARCHAR(1)'

    # TEXT types (order matters - check longer names first)
    if 'longtext' in type_lower:
        return 'TEXT'
    if 'mediumtext' in type_lower:
        return 'TEXT'
    if 'tinytext' in type_lower:
        return 'TEXT'
    if 'text' in type_lower:
        return 'TEXT'

    # ─────────────────────────────────────────
    # BINARY TYPES
    # ─────────────────────────────────────────
    if re.match(r'varbinary', type_lower):
        return 'BLOB'
    if re.match(r'binary', type_lower):
        return 'BLOB'

    # BLOB types (order matters - check longer names first)
    if 'longblob' in type_lower:
        return 'BLOB'
    if 'mediumblob' in type_lower:
        return 'BLOB'
    if 'tinyblob' in type_lower:
        return 'BLOB'
    if 'blob' in type_lower:
        return 'BLOB'

    # ─────────────────────────────────────────
    # ENUM / SET
    # ─────────────────────────────────────────
    if re.match(r'enum\s*\(', type_lower):
        return 'VARCHAR'
    if re.match(r'set\s*\(', type_lower):
        return 'VARCHAR'

    # ─────────────────────────────────────────
    # JSON
    # ─────────────────────────────────────────
    if re.match(r'json\b', type_lower):
        return 'JSON'

    # ─────────────────────────────────────────
    # SPATIAL TYPES (stored as VARCHAR)
    # ─────────────────────────────────────────
    spatial_types = [
        'geometry', 'point', 'linestring', 'polygon',
        'multipoint', 'multilinestring', 'multipolygon',
        'geometrycollection', 'geomcollection'
    ]
    for spatial in spatial_types:
        if re.match(rf'{spatial}\b', type_lower):
            return 'VARCHAR'

    # ─────────────────────────────────────────
    # SERIAL (auto-increment alias)
    # ─────────────────────────────────────────
    if re.match(r'serial\b', type_lower):
        return 'BIGINT'

    # Fallback: return as-is
    return type_str


def parse_column_definition(col_def: str) -> Optional[tuple]:
    """Parse a single column definition, return (name, type, constraints) or None if not a column."""
    col_def = col_def.strip()

    # Skip non-column definitions
    skip_patterns = [
        r'^PRIMARY\s+KEY',
        r'^UNIQUE\s+KEY',
        r'^KEY\s+',
        r'^INDEX\s+',
        r'^CONSTRAINT\s+',
        r'^FOREIGN\s+KEY',
        r'^FULLTEXT',
        r'^SPATIAL',
    ]
    for pattern in skip_patterns:
        if re.match(pattern, col_def, re.IGNORECASE):
            return None

    # Match column: `name` type [constraints]
    match = re.match(r'`(\w+)`\s+(\S+(?:\s*\([^)]+\))?)(.*)', col_def)
    if not match:
        return None

    col_name = match.group(1)
    col_type = match.group(2)
    constraints = match.group(3).strip()

    # Convert type
    duckdb_type = convert_mysql_type(col_type)

    # Convert constraints - remove MySQL-specific clauses
    # Handle CHARACTER SET with various formats: CHARACTER SET utf8, CHARACTER SET = utf8, CHARSET utf8
    constraints = re.sub(r'\s*CHARACTER\s+SET\s*=?\s*[\w\-]+', '', constraints, flags=re.IGNORECASE)
    constraints = re.sub(r'\s*CHARSET\s*=?\s*[\w\-]+', '', constraints, flags=re.IGNORECASE)
    # Handle COLLATE with various formats
    constraints = re.sub(r'\s*COLLATE\s*=?\s*[\w\-]+', '', constraints, flags=re.IGNORECASE)
    # Handle DEFAULT with bit literal
    constraints = re.sub(r"DEFAULT\s+b'([01])'", lambda m: f"DEFAULT {'TRUE' if m.group(1) == '1' else 'FALSE'}", constraints, flags=re.IGNORECASE)
    # Remove AUTO_INCREMENT
    constraints = re.sub(r'\s*AUTO_INCREMENT', '', constraints, flags=re.IGNORECASE)
    # Remove ON UPDATE CURRENT_TIMESTAMP
    constraints = re.sub(r'\s*ON\s+UPDATE\s+CURRENT_TIMESTAMP(?:\(\))?', '', constraints, flags=re.IGNORECASE)
    # Remove COMMENT 'text'
    constraints = re.sub(r"\s*COMMENT\s+'[^']*'", '', constraints, flags=re.IGNORECASE)

    return (col_name, duckdb_type, constraints.strip())


def extract_primary_key(create_body: str) -> Optional[str]:
    """Extract PRIMARY KEY column(s) from CREATE TABLE body."""
    match = re.search(r'PRIMARY\s+KEY\s*\(\s*`?(\w+)`?\s*\)', create_body, re.IGNORECASE)
    if match:
        return match.group(1)
    return None


def convert_create_table(sql: str) -> Optional[tuple]:
    """
    Convert MySQL CREATE TABLE to DuckDB format.
    Returns (create_sql, column_types_list) where column_types_list is list of DuckDB types in order.
    """
    # Extract table name and body
    # Handle optional MySQL comments/attributes between ) and ENGINE (e.g., /*!50100 TABLESPACE ... */)
    match = re.search(r'CREATE\s+TABLE\s+`(\w+)`\s*\((.*)\)\s*(?:/\*.*?\*/\s*)*ENGINE\s*=', sql, re.DOTALL | re.IGNORECASE)
    if not match:
        # Try without ENGINE
        match = re.search(r'CREATE\s+TABLE\s+`(\w+)`\s*\((.*)\)\s*;', sql, re.DOTALL | re.IGNORECASE)
        if not match:
            return None

    table_name = match.group(1)
    body = match.group(2)

    # Get primary key
    pk_column = extract_primary_key(body)

    # Parse columns - split by comma, but respect parentheses
    columns = []
    depth = 0
    current = []
    for char in body:
        if char == '(':
            depth += 1
        elif char == ')':
            depth -= 1
        elif char == ',' and depth == 0:
            columns.append(''.join(current).strip())
            current = []
            continue
        current.append(char)
    if current:
        columns.append(''.join(current).strip())

    # Convert each column
    duckdb_columns = []
    column_types = []  # Track types in order for INSERT conversion

    for col in columns:
        parsed = parse_column_definition(col)
        if parsed:
            col_name, col_type, constraints = parsed
            column_types.append(col_type)
            # Add PRIMARY KEY inline if this is the PK column
            if pk_column and col_name.upper() == pk_column.upper() and 'PRIMARY KEY' not in constraints.upper():
                constraints = f"PRIMARY KEY {constraints}".strip()
            duckdb_columns.append(f'    "{col_name}" {col_type} {constraints}'.rstrip())

    # Build CREATE TABLE IF NOT EXISTS
    columns_sql = ',\n'.join(duckdb_columns)
    create_sql = f'CREATE TABLE IF NOT EXISTS "{table_name}" (\n{columns_sql}\n);'

    return (create_sql, column_types)


def is_escaped(s: str, pos: int) -> bool:
    """Check if character at position is escaped by counting preceding backslashes."""
    if pos == 0:
        return False
    # Count consecutive backslashes before this position
    count = 0
    i = pos - 1
    while i >= 0 and s[i] == '\\':
        count += 1
        i -= 1
    # If odd number of backslashes, the character is escaped
    return count % 2 == 1


def parse_insert_values(values_str: str) -> list:
    """Parse INSERT VALUES into list of row tuples (as strings)."""
    rows = []
    depth = 0
    current_row = []
    in_string = False
    string_char = None

    i = 0
    while i < len(values_str):
        char = values_str[i]

        # Handle string literals
        if char in ("'", '"'):
            if not in_string:
                in_string = True
                string_char = char
            elif char == string_char:
                # Check if this quote is escaped
                if not is_escaped(values_str, i):
                    # Also check for doubled quotes ('' or "")
                    if i + 1 < len(values_str) and values_str[i + 1] == char:
                        # Doubled quote - skip both, stay in string
                        if depth > 0:
                            current_row.append(char)
                            current_row.append(char)
                        i += 2
                        continue
                    else:
                        # End of string
                        in_string = False
                        string_char = None

        if not in_string:
            if char == '(':
                if depth == 0:
                    current_row = []
                depth += 1
                if depth == 1:
                    i += 1
                    continue
            elif char == ')':
                depth -= 1
                if depth == 0:
                    rows.append(''.join(current_row))
                    i += 1
                    continue

        if depth > 0:
            current_row.append(char)

        i += 1

    return rows


def convert_mysql_string_escapes(val: str) -> str:
    """
    Convert MySQL string escapes to DuckDB-compatible format.
    MySQL uses backslash escapes: \' \" \\ \n \r \t \0
    DuckDB uses doubled quotes for escaping: '' for single quote
    """
    if not (val.startswith("'") and val.endswith("'")):
        return val  # Not a string literal

    # Extract content between quotes
    content = val[1:-1]

    # Convert MySQL escapes to DuckDB format
    result = []
    i = 0
    while i < len(content):
        if content[i] == '\\' and i + 1 < len(content):
            next_char = content[i + 1]
            if next_char == "'":
                # \' → '' (doubled single quote)
                result.append("''")
                i += 2
                continue
            elif next_char == '"':
                # \" → " (just the quote, no escape needed in single-quoted string)
                result.append('"')
                i += 2
                continue
            elif next_char == '\\':
                # \\ → \\ (keep as-is, DuckDB understands this)
                result.append('\\\\')
                i += 2
                continue
            elif next_char == 'n':
                # \n → newline (keep as-is)
                result.append('\\n')
                i += 2
                continue
            elif next_char == 'r':
                # \r → carriage return (keep as-is)
                result.append('\\r')
                i += 2
                continue
            elif next_char == 't':
                # \t → tab (keep as-is)
                result.append('\\t')
                i += 2
                continue
            elif next_char == '0':
                # \0 → null byte (keep as-is)
                result.append('\\0')
                i += 2
                continue
            elif next_char == 'Z':
                # \Z → Ctrl+Z (Windows EOF)
                result.append('\\Z')
                i += 2
                continue
            elif next_char == '%':
                # \% → % (LIKE escape)
                result.append('%')
                i += 2
                continue
            elif next_char == '_':
                # \_ → _ (LIKE escape)
                result.append('_')
                i += 2
                continue
            else:
                # Unknown escape, keep backslash
                result.append(content[i])
                i += 1
        elif content[i] == "'" and i + 1 < len(content) and content[i + 1] == "'":
            # Already doubled quote, keep as-is
            result.append("''")
            i += 2
        else:
            result.append(content[i])
            i += 1

    return "'" + ''.join(result) + "'"


def convert_row_values(row_str: str, column_types: list) -> str:
    """Convert a single row's values based on column types."""
    # Parse individual values from the row
    values = []
    current = []
    depth = 0
    in_string = False
    string_char = None

    i = 0
    while i < len(row_str):
        char = row_str[i]

        # Handle string literals
        if char in ("'", '"'):
            if not in_string:
                in_string = True
                string_char = char
            elif char == string_char:
                # Check if escaped
                if not is_escaped(row_str, i):
                    # Check for doubled quotes
                    if i + 1 < len(row_str) and row_str[i + 1] == char:
                        current.append(char)
                        current.append(char)
                        i += 2
                        continue
                    else:
                        in_string = False
                        string_char = None

        if char == ',' and not in_string and depth == 0:
            values.append(''.join(current).strip())
            current = []
        else:
            if char == '(' and not in_string:
                depth += 1
            elif char == ')' and not in_string:
                depth -= 1
            current.append(char)

        i += 1

    if current:
        values.append(''.join(current).strip())

    # Convert each value based on column type
    converted = []
    for i, val in enumerate(values):
        col_type = column_types[i] if i < len(column_types) else 'VARCHAR'

        # Check if it's a hex literal
        hex_match = re.match(r'^0x([0-9A-Fa-f]+)$', val)
        if hex_match:
            hex_val = hex_match.group(1)
            if col_type == 'BOOLEAN':
                # Convert to TRUE/FALSE
                if hex_val in ('00', '0'):
                    converted.append('FALSE')
                elif hex_val in ('01', '1'):
                    converted.append('TRUE')
                else:
                    # Non-standard value, treat as true if non-zero
                    converted.append('TRUE' if int(hex_val, 16) != 0 else 'FALSE')
            elif col_type == 'BLOB':
                # Convert to blob literal
                converted.append(f"'\\x{hex_val}'::BLOB")
            else:
                # For other types, just use the hex value as-is or convert
                converted.append(val)
        elif val.startswith("'") and val.endswith("'"):
            # String literal - convert MySQL escapes to DuckDB format
            converted.append(convert_mysql_string_escapes(val))
        else:
            converted.append(val)

    return ', '.join(converted)


def convert_insert_statement(sql: str, column_types: list) -> Optional[str]:
    """Convert MySQL INSERT to DuckDB format using column types for proper conversion."""
    # Match INSERT INTO `table` VALUES ...
    match = re.search(r"INSERT\s+INTO\s+`(\w+)`\s*(?:\([^)]*\))?\s*VALUES\s*(.*)", sql, re.DOTALL | re.IGNORECASE)
    if not match:
        return None

    table_name = match.group(1)
    values_part = match.group(2).strip()

    # Remove trailing semicolon if present
    if values_part.endswith(';'):
        values_part = values_part[:-1]

    # Parse and convert each row
    rows = parse_insert_values(values_part)
    converted_rows = []

    for row in rows:
        converted_row = convert_row_values(row, column_types)
        converted_rows.append(f'({converted_row})')

    return f'INSERT INTO "{table_name}" VALUES\n  ' + ',\n  '.join(converted_rows) + ';'


def normalize_sql_whitespace(sql: str) -> str:
    """
    Normalize whitespace in SQL while preserving string literals.
    Converts multiple whitespace (including newlines) to single spaces,
    but preserves content inside quoted strings.
    """
    result = []
    in_string = False
    string_char = None
    i = 0

    while i < len(sql):
        char = sql[i]

        # Handle string literals
        if char in ("'", '"') and not is_escaped(sql, i):
            if not in_string:
                in_string = True
                string_char = char
            elif char == string_char:
                # Check for doubled quotes
                if i + 1 < len(sql) and sql[i + 1] == char:
                    result.append(char)
                    result.append(char)
                    i += 2
                    continue
                else:
                    in_string = False
                    string_char = None
            result.append(char)
        elif in_string:
            # Inside string - preserve as-is
            result.append(char)
        elif char in ' \t\n\r':
            # Outside string - normalize whitespace
            if result and result[-1] != ' ':
                result.append(' ')
        else:
            result.append(char)

        i += 1

    return ''.join(result)


def parse_mysql_dump(sql_content: str) -> dict:
    """Parse MySQL dump and extract tables and data."""
    result = {
        'tables': {},        # table_name -> create_sql
        'column_types': {},  # table_name -> [type1, type2, ...]
        'inserts': {},       # table_name -> [insert_sql, ...]
    }

    # Remove MySQL conditional comments
    content = re.sub(r'/\*!\d+\s+.*?\*/\s*;?', '', sql_content, flags=re.DOTALL)

    # Remove LOCK/UNLOCK TABLES
    content = re.sub(r'LOCK\s+TABLES\s+.*?;\s*', '', content, flags=re.IGNORECASE)
    content = re.sub(r'UNLOCK\s+TABLES\s*;\s*', '', content, flags=re.IGNORECASE)

    # Remove DROP TABLE statements
    content = re.sub(r'DROP\s+TABLE\s+IF\s+EXISTS\s+.*?;\s*', '', content, flags=re.IGNORECASE)

    # Normalize whitespace to handle multi-line column definitions
    content = normalize_sql_whitespace(content)

    # Extract CREATE TABLE statements
    create_pattern = r'CREATE\s+TABLE\s+`(\w+)`\s*\(.*?\)\s*(?:ENGINE\s*=\s*\w+[^;]*)?;'
    for match in re.finditer(create_pattern, content, re.DOTALL | re.IGNORECASE):
        full_sql = match.group(0)
        converted = convert_create_table(full_sql)
        if converted:
            create_sql, column_types = converted
            table_name = re.search(r'CREATE\s+TABLE\s+`(\w+)`', full_sql, re.IGNORECASE).group(1)
            result['tables'][table_name] = create_sql
            result['column_types'][table_name] = column_types

    # Extract INSERT statements - using custom parser to handle semicolons inside strings
    def find_insert_statements(sql: str):
        """Find INSERT statements, properly handling semicolons inside string values."""
        inserts = []
        i = 0
        while i < len(sql):
            # Look for INSERT INTO
            match = re.search(r"INSERT\s+INTO\s+`(\w+)`", sql[i:], re.IGNORECASE)
            if not match:
                break

            start = i + match.start()
            table_name = match.group(1)

            # Now find the actual end of the statement (semicolon outside string)
            j = i + match.end()
            in_string = False
            string_char = None

            while j < len(sql):
                char = sql[j]

                if char in ("'", '"'):
                    if not in_string:
                        in_string = True
                        string_char = char
                    elif char == string_char:
                        # Check if escaped
                        if not is_escaped(sql, j):
                            # Check for doubled quote
                            if j + 1 < len(sql) and sql[j + 1] == char:
                                j += 1  # Skip the doubled quote
                            else:
                                in_string = False
                                string_char = None

                elif char == ';' and not in_string:
                    # Found the real end of the statement
                    full_sql = sql[start:j + 1]
                    inserts.append((table_name, full_sql))
                    i = j + 1
                    break

                j += 1
            else:
                # Reached end of string without finding semicolon
                break

            if j >= len(sql):
                break

        return inserts

    for table_name, full_sql in find_insert_statements(content):
        # Get column types for this table
        column_types = result['column_types'].get(table_name, [])

        converted = convert_insert_statement(full_sql, column_types)
        if converted:
            if table_name not in result['inserts']:
                result['inserts'][table_name] = []
            result['inserts'][table_name].append(converted)

    return result


def convert_dump_to_file(sql_file: str, output_file: str, verbose: bool = True):
    """
    Convert MySQL dump to DuckDB-compatible SQL file.

    Args:
        sql_file: Path to input MySQL dump
        output_file: Path to output DuckDB SQL file
        verbose: Print progress messages
    """
    if verbose:
        print(f"Reading {sql_file}...")

    with open(sql_file, 'r', encoding='utf-8', errors='replace') as f:
        content = f.read()

    if verbose:
        print("Converting...")

    parsed = parse_mysql_dump(content)

    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("-- Converted from MySQL dump to DuckDB format\n\n")

        # Write CREATE TABLE statements
        for table_name, create_sql in parsed['tables'].items():
            f.write(f"-- Table: {table_name}\n")
            f.write(create_sql)
            f.write("\n\n")

        # Write INSERT statements
        for table_name, insert_sqls in parsed['inserts'].items():
            f.write(f"-- Data for: {table_name}\n")
            for insert_sql in insert_sqls:
                f.write(insert_sql)
                f.write("\n")
            f.write("\n")

    if verbose:
        print(f"Written to {output_file}")
        print(f"  Tables: {len(parsed['tables'])}")
        print(f"  Insert statements: {sum(len(v) for v in parsed['inserts'].values())}")


# CLI usage
if __name__ == "__main__":
    import sys

    if len(sys.argv) < 3:
        print("MySQL Dump to DuckDB Converter")
        print()
        print("Usage:")
        print("  python mysql_to_duckdb.py <mysql_dump.sql> <output.sql>")
        print()
        print("Then load into DuckDB CLI:")
        print("  duckdb mydb.duckdb < output.sql")
        print()
        print("Or directly:")
        print("  duckdb mydb.duckdb -c \".read output.sql\"")
        sys.exit(1)

    sql_file = sys.argv[1]
    output_file = sys.argv[2]

    convert_dump_to_file(sql_file, output_file)
