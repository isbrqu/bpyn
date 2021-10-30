# Notas

## carateristicas de documentos pdf

- extracto:
    - registros incompletos.
    - mucho texto innecesarios.
- ComprobantePagoRealizado
    - a veces tiene título.
    - tiene fecha.
    - puede estar muy incompleto si es muy antiguo.
- transferencia
    - no es estandar el formato de fecha.  ­ algunos campos pueden estar vacios
      (identificar por qué pasa).
- DetalleCredin

## caracterisiticas de documentos xls

- prestamos
    - se descargan por partes.
    - el formato de la fecha es dd/mm/yyyy.
    - el formato de moneda es 1.000,00.
- compras
    - no posee la hora, minutos ni segundo.
    - tiene solo 3 campos (fecha, descripción y monto).
- compras Comercios
- consultaPagosRealizados
- movimentosHistoricos
- resumenTransferencias
- cuotasCanceladas
- cuotasPendientes
- detallePrestamos
- consumosMensuales
- ultimoResumen
- tarjetasDeCredito
- ultimosMovimientos
- movimientosDia
- PosicionConsolidada
- sleccionCuentaAderidasExtractos
- cuentasDestinoTransferenciasTerceros
- cuentasDestinoTransferenciasPropias

## notas de documentos y consultas

- identificar cual es el formato que da más información en cada caso.
- algunos documentos descargados tienen más datos que algunos json. Ejemplo: en
  comprasComercios la descripción es más detallada.
 - algunos pdfs cambian según donde se lo descarguen. Si se descarga el
   comprobante justo después de realizar la operación, este pude ser diferente
   al comprobante que se obtiene del historico, incluso puede variar datos tan
   distintivos como lo es la fecha referido a la realizción deun mismo
   comprobante.

## notas de el scraping

- existen state en etiquetas a.
- existen state en variables javascript (vars).
- existen state en etiquetas input tipo hidden.
- algunos state de etiquetas a con state de variables javascript colisionan en
  el proposito.
- hasta ahora todas las opciones tienen el formato de `id="_menu_operacion"`
- requests -> query url.
- request data -> body request.
- beautiful soup text elimina las tag
- separa diagrama de secuencia de HTTP del diagrama de secuencia de objetos.
- observación: `__fisrtLogin` no requiere el mismo usuario para
  `__second_login`, con que el `username` exista, es suficiente para que
  devuelva el html.
- separa los state temporales de los state perpetuos de la sesión.
- ¿pueden haber diferentes state con un mismo nombre pero para cosas distintas?
  es probable que haya colisiones entre las variables javascript y alguna
  etiqueta a con similar nombre de operación.
- existe colisión en bienvenida de las variables javascript.
- los diccionarios en python se quedan con el último valor de una clave
  repetidas.
- diferentes state pueden realizar lo mismo, casualidad encontrada con
  `self.soup_home.text` en el que una variable js tenía una state diferente al
  del atributo realmente de un hipervinculo.  # salud

