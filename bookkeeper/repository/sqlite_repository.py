from itertools import count
from typing import Any
import sqlite3

from bookkeeper.repository.abstract_repository import AbstractRepository, T

from inspect import get_annotations
    

class SQLiteRepository(AbstractRepository[T]):
    """
    Репозиторий, работающий c базой данных SQLite.
    """
    db_file: str
    obj_cls: type
    table_name: str
    fields: dict[str, Any]
    
    
    def __init__(self, db_file: str, cls: type) -> None:
        self.db_file = db_file
        self.table_name = cls.__name__.lower()
        self.fields = get_annotations(cls, eval_str=True)
        self.fields.pop('pk')
        self.new_obj = cls

    
    def add(self, obj: T) -> int:
        names = ', '.join(self.fields.keys())
        p = ', '.join("?" * len(self.fields))
        values = [getattr(obj, x) for x in self.fields]
        with sqlite3.connect(self.db_file) as con:
            cur = con.cursor()
            cur.execute('PRAGMA foreign_keys = ON')
            cur.execute(f'INSERT INTO {self.table_name} ({names}) VALUES ({p})',
                        values )
            obj.pk = cur.lastrowid
        con.close()
        return obj.pk
    
    def _row2obj(self, row: tuple[Any], pk: int ) -> T:
        '''Преобразование строки БД в obj'''
        obj = self.new_obj(**dict(zip(self.fields, row)))
        obj.pk = pk
        return obj

    def get(self, pk: int) -> T | None:
        names = ', '.join(self.fields.keys())
        with sqlite3.connect(self.db_file) as con:
            cur = con.cursor()
            cur.execute('PRAGMA foreign_keys = ON')
            row = cur.execute(
                f'SELECT * FROM {self.table_name} WHERE ROWID = {pk}'
                              ).fetchone()
        con.close
        if row is None: return(None)
        return self._row2obj(row, pk)

            


    def get_all(self, where: dict[str, Any] | None = None) -> list[T]:
        with sqlite3.connect(self.db_file) as con:
            cur = con.cursor()
            if where is None:
                rows = cur.execute(
                    f'SELECT ROWID, * FROM {self.table_name} '
                ).fetchall()
            else:
                fields = " AND ".join([f"{f} LIKE ?" for f in where.keys()])
                rows = cur.execute(
                    f'SELECT ROWID, * FROM {self.table_name} '
                    + f'WHERE {fields}',
                    list(where.values())
                ).fetchall()
        con.close()
        return [self._row2obj(r[0], r[1:]) for r in rows]
    
    
    
    def get_all_like(self, like: dict[str, str]) -> list[T]:
        values = [f"%{v}%" for v in like.values()]
        where = dict(zip(like.keys(), values))
        return self.get_all(where=where)
    
    
    def update(self, obj: T) -> None:
        if obj.pk == 0:
            raise ValueError('attempt to update object with unknown primary key')
        
        names = ', '.join(f'{i} = ?' for i in self.fields.keys())
        values = [getattr(obj, x) for x in self.fields]
        with sqlite3.connect(self.db_file) as con:
            cur = con.cursor()
            cur.execute('PRAGMA foreign_keys = ON') 
            cur.execute(f'UPDATE {self.table_name} SET ({names}) WHERE ROWID = {obj.pk}',
                         values)   
        con.close()   

    def delete(self, pk: int) -> None:
        with sqlite3.connect(self.db_file) as con:
            cur = con.cursor()
            cur.execute('PRAGMA foreign_keys = ON') 
            cur.execute(f'DELETE FROM {self.table_name} WHERE ROWID = {pk}')
        cur.close()
