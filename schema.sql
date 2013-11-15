PRAGMA foreign_keys = ON;

drop table if exists categorias;
create table categorias (
  id integer primary key autoincrement,
  nombre text not null,
  unique (nombre)
);

drop table if exists proveedores;
create table proveedores (
  id integer primary key autoincrement,
  categoria_id integer,
  nombre text not null,
  foreign key(categoria_id) references categorias(id),
  unique (nombre)
);

drop table if exists movimientos;
create table movimientos (
  id integer primary key autoincrement,
  proveedor_id integer,
  fecha integer not null,
  importe real not null,
  saldo real not null,
  foreign key(proveedor_id) references proveedores(id)
);

