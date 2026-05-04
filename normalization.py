#!/usr/bin/env python3
import json, argparse, sys, os

try:
    import win32com.client
    HAS_COM = True
except ImportError:
    HAS_COM = False
    import pyodbc

def map_access_to_dbdiagram_type(access_type):
    """Map Access data types to dbdiagram.io types"""
    type_map = {
        'LONGBINARY': 'binary',
        'MEMO': 'text',
        'CURRENCY': 'decimal',
        'DATETIME': 'datetime',
        'SMALLINT': 'int',
        'INTEGER': 'int',
        'BYTE': 'int',
        'LONG': 'int',
        'AUTOINCREMENT': 'int',
        'REAL': 'float',
        'DOUBLE': 'float',
        'SINGLE': 'float',
        'FLOAT': 'float',
        'NUMERIC': 'decimal',
        'DECIMAL': 'decimal',
        'CURRENCY': 'decimal',
        'BOOLEAN': 'boolean',
        'TEXT': 'string',
        'OLE': 'binary',
        'GUID': 'string',
    }
    
    access_type_upper = access_type.upper() if access_type else 'TEXT'
    return type_map.get(access_type_upper, 'string')

def main_with_dao(path):
    """Extract schema using DAO (Data Access Objects) - Full metadata support"""
    abs_path = os.path.abspath(path)
    
    if not os.path.exists(abs_path):
        print(f"Error: El archivo '{abs_path}' no existe.", file=sys.stderr)
        sys.exit(1)
    
    try:
        # Create DAO DBEngine
        dao = win32com.client.Dispatch("DAO.DBEngine.120")
        db = dao.OpenDatabase(abs_path)
    except Exception as e:
        print(f"Error al abrir base de datos con DAO: {e}", file=sys.stderr)
        sys.exit(1)
    
    tables = []
    
    try:
        # Get all tables
        for tbl_def in db.TableDefs:
            tbl_name = tbl_def.Name
            
            # Skip system tables
            if tbl_name.startswith('MSys'):
                continue
            
            cols = []
            pks = []
            fks = []
            
            # Get columns
            for fld in tbl_def.Fields:
                col_type = get_dao_type_name(fld.Type, fld)
                cols.append({
                    "name": fld.Name,
                    "type": col_type,
                    "nullable": (fld.AllowZeroLength or not fld.Required) if hasattr(fld, 'Required') else True,
                })
            
            # Get primary key
            try:
                if tbl_def.PrimaryKey:
                    for fld in tbl_def.PrimaryKey.Fields:
                        pks.append(fld.Name)
            except:
                pass
            
            # Get foreign keys
            try:
                for rel in db.Relations:
                    # Check if this table is the foreign key table
                    if rel.ForeignTable == tbl_name:
                        for fld in rel.Fields:
                            fks.append({
                                "fk_table": rel.ForeignTable,
                                "fk_column": fld.ForeignName,
                                "pk_table": rel.Table,
                                "pk_column": fld.Name,
                            })
            except:
                pass
            
            tables.append({
                "table": tbl_name,
                "columns": cols,
                "primary_key": pks,
                "foreign_keys": fks
            })
        
        db.Close()
    except Exception as e:
        print(f"Error al procesar tablas: {e}", file=sys.stderr)
        sys.exit(1)
    
    return tables

def get_dao_type_name(dao_type, field_obj=None):
    """Convert DAO type number to string"""
    type_map = {
        1: 'BOOLEAN',
        2: 'BYTE',
        3: 'INTEGER',
        4: 'LONG',
        5: 'CURRENCY',
        6: 'SINGLE',
        7: 'DOUBLE',
        8: 'DATETIME',
        9: 'TEXT',
        10: 'TEXT',
        11: 'LONGBINARY',
        12: 'MEMO',
        15: 'GUID',
        16: 'NUMERIC',
        17: 'DECIMAL',
        18: 'FLOAT',
    }
    
    base_type = type_map.get(dao_type, 'TEXT')
    
    # Check if it's an AutoIncrement field
    if field_obj and hasattr(field_obj, 'Attributes'):
        # dbAutoIncrField = 4
        if field_obj.Attributes & 4:
            base_type = 'AUTOINCREMENT'
    
    return base_type

def main_with_pyodbc(path):
    """Fallback: Extract schema using pyodbc"""
    abs_path = os.path.abspath(path)
    
    if not os.path.exists(abs_path):
        print(f"Error: El archivo '{abs_path}' no existe.", file=sys.stderr)
        sys.exit(1)
    
    try:
        conn_str = r'Driver={Microsoft Access Driver (*.mdb, *.accdb)};DBQ=' + abs_path + ';'
        conn = pyodbc.connect(conn_str)
    except Exception as e:
        print(f"Error al conectar con la base de datos: {e}", file=sys.stderr)
        sys.exit(1)

    tables = []
    
    # Get all tables using a separate cursor
    try:
        cursor_tables = conn.cursor()
        table_list = list(cursor_tables.tables(tableType='TABLE'))
        cursor_tables.close()
    except Exception as e:
        print(f"Error al obtener tablas: {e}", file=sys.stderr)
        sys.exit(1)
    
    # Process each table with separate cursors
    for t in table_list:
        tbl = t.table_name
        if tbl.startswith('MSys'): 
            continue
            
        cols = []
        try:
            cursor_cols = conn.cursor()
            for c in cursor_cols.columns(table=tbl):
                cols.append({
                    "name": c.column_name,
                    "type": getattr(c, 'type_name', str(getattr(c, 'data_type', 'unknown'))),
                    "nullable": bool(getattr(c, 'nullable', 0)),
                })
            cursor_cols.close()
        except Exception as e:
            print(f"Warning: No se pudieron obtener columnas de {tbl}: {e}", file=sys.stderr)

        pks = []
        fks = []

        tables.append({
            "table": tbl,
            "columns": cols,
            "primary_key": pks,
            "foreign_keys": fks
        })
    
    conn.close()
    return tables

def main(path):
    """Main function - uses DAO if available, falls back to pyodbc"""
    if HAS_COM:
        print("Usando DAO para extracción de metadatos...", file=sys.stderr)
        tables = main_with_dao(path)
    else:
        print("DAO no disponible. Usando pyodbc (sin soporte para claves primarias/foráneas)...", file=sys.stderr)
        tables = main_with_pyodbc(path)
    
    # Generate dbdiagram.io format
    output = []
    
    for table_info in tables:
        table_name = table_info['table']
        columns = table_info['columns']
        primary_keys = table_info['primary_key']
        foreign_keys = table_info['foreign_keys']
        
        # Format table name with quotes if it contains spaces
        table_name_formatted = f'"{table_name}"' if ' ' in table_name else table_name
        output.append(f"Table {table_name_formatted} " + "{")
        
        for col in columns:
            col_name = col['name']
            col_type = map_access_to_dbdiagram_type(col['type'])
            
            # Format column name with quotes if it contains spaces
            col_name_formatted = f'"{col_name}"' if ' ' in col_name else col_name
            
            attributes = []
            
            # Check if primary key
            if col_name in primary_keys:
                attributes.append('pk')
            
            # Check if not nullable (required)
            if not col['nullable']:
                attributes.append('not null')
            
            # Check if foreign key
            for fk in foreign_keys:
                if fk['fk_column'] == col_name:
                    ref_table = fk['pk_table']
                    ref_column = fk['pk_column']
                    # Format reference names with quotes if they contain spaces
                    ref_table_formatted = f'"{ref_table}"' if ' ' in ref_table else ref_table
                    ref_column_formatted = f'"{ref_column}"' if ' ' in ref_column else ref_column
                    attributes.append(f"ref: > {ref_table_formatted}.{ref_column_formatted}")
            
            # Build column line
            attr_str = f" [{', '.join(attributes)}]" if attributes else ""
            output.append(f"  {col_name_formatted} {col_type}{attr_str}")
        
        output.append("}")
        output.append("")
    
    # Print dbdiagram.io format
    print("\n".join(output))

if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("accdb", help="SQL_TC2.accdb")
    args = p.parse_args()
    try:
        main(args.accdb)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)