#!/usr/bin/env python
# -*- coding: utf-8 -*-
import json
import re
import time
import urllib
import datetime
import argparse
import sys

'''
List of colors for console
'''

class color:
   PURPLE = '\033[95m'
   CYAN = '\033[96m'
   DARKCYAN = '\033[36m'
   BLUE = '\033[94m'
   GREEN = '\033[92m'
   YELLOW = '\033[93m'
   RED = '\033[91m'
   BOLD = '\033[1m'
   UNDERLINE = '\033[4m'
   END = '\033[0m'


bcu_url = "http://www.bcu.gub.uy/_layouts/BCU.Cotizaciones/handler/CotizacionesHandler.ashx?op=getcotizaciones"

listaMonedas = {
    "ARG": [{"Val": "501", "Text": "PESO ARG.BILLETE"}],
    "BRA": [{"Val": "1001", "Text": "REAL BILLETE"}],
    "USDFDOBCU": [{"Val": "2223", "Text": "DLS. USA FDO BCU"}],
    "USDUSACBL": [{"Val": "2224", "Text": "DLS. USA CABLE"}],
    "USDUSABIL": [{"Val": "2225", "Text": "DLS. USA BILLETE"}],
    "USDPROFON": [{"Val": "2230", "Text": "DLS. PROM. FONDO"}],
    "UI": [{"Val": "9800", "Text": "UNIDAD INDEXADA"}],
    "UR": [{"Val": "9900", "Text": "UNIDAD REAJUSTABLE"}]
}

'''
Return yesterday's date in format DD/MM/YYYY
'''

def getYesterdayDate():
  yesterday = datetime.datetime.now() - datetime.timedelta(days=1)

  return yesterday.strftime('%d/%m/%Y')


'''
Return a JSON object to be used as POST data
'''

def createRequest(moneda, fechaDesde=getYesterdayDate(), fechaHasta=getYesterdayDate(), grupo=2):
    request = {"KeyValuePairs": {"Monedas": moneda,
                                 "FechaDesde": fechaDesde, "FechaHasta": fechaHasta, "Grupo": grupo}}

    return json.dumps(request)

'''
Verifies that the entered date is valid
'''

def validarFecha(fecha):
  try:
    fecha_valida = datetime.datetime.strptime(fecha, '%d/%m/%Y').date()
  except ValueError:
    print color.BOLD + color.RED + 'La fecha ingresada no es valida!' + color.END
    sys.exit(1)

  return fecha

def validarMoneda(moneda):
  try:
    moneda_valida = listaMonedas[moneda]
  except KeyError:
    print color.BOLD + color.RED + 'La moneda ingresada no es valida!' + color.END
    listarMonedas()
    sys.exit(1)

  return moneda

def listarMonedas():
  print "Por favor selecione una de las siguientes: \n"
  print "{: <10} | ({})".format("Código", "Descripción")
  print "--------------------------------"
  for moneda in listaMonedas:
    print "{: <9} | ({})".format(moneda, listaMonedas[moneda][0]['Text'])
  print ""

def __main__():
  parser = argparse.ArgumentParser(description='Este programa permite obtener las cotizaciones de las monedas segun el BCU.')
  parser.add_argument('--moneda', type=validarMoneda, default="USDUSABIL",
                    help='La moneda seleccionada para obtener la cotización (Por defecto es DLS. USA BILLETE)')
  parser.add_argument('--fecha', type=validarFecha, default=getYesterdayDate(),
                    help='Fecha de la cual se desea obtener la cotización')
  parser.add_argument('--verbose', action='store_true', help='Muestra mas información sobre la cotización solicitada')
  args = parser.parse_args()

  if args.moneda in listaMonedas:
    print color.BOLD + color.GREEN + "Obteniendo cotización de {} para la fecha {}...".format(args.moneda, listaMonedas[args.moneda][0]['Text']) + color.END

    request = urllib.urlopen(bcu_url, createRequest(listaMonedas[args.moneda], args.fecha, args.fecha))
    result = request.read()

    parsed_result = json.loads(result)
    status = parsed_result['cotizacionesoutlist']['RespuestaStatus']['status']

    if status == 1:
        cotizaciones = parsed_result['cotizacionesoutlist']['Cotizaciones']
        m = re.search('([0-9]+)', cotizaciones[0]['Fecha'])
        timestamp = m.group(0)
        fecha = time.strftime("%d/%m/%Y", time.gmtime(float(timestamp[:10])))

        if args.verbose:
          print color.BOLD + color.GREEN + "Fecha: " + color.END + "{}".format(fecha)
          print color.BOLD + color.GREEN + "Moneda: " + color.END + "{} ({})".format(cotizaciones[0]['Nombre'], cotizaciones[0]['CodigoISO'])
          print color.BOLD + color.GREEN + "Emisor: " + color.END + "{} ({})".format(cotizaciones[0]['Nombre'], cotizaciones[0]['Emisor'])
          print color.BOLD + color.GREEN + "Valor Compra: " + color.END + "{}".format(cotizaciones[0]['TCC'])
          print color.BOLD + color.GREEN + "Valor Venta: " + color.END + "{}".format(cotizaciones[0]['TCV'])
          print color.BOLD + color.GREEN + "Arbitraje: " + color.END + "{}".format(cotizaciones[0]['ArbAct'])
        else:
          print "Valor Compra: {}".format(cotizaciones[0]['TCC'])
          print "Valor Venta: {}".format(cotizaciones[0]['TCV'])
    elif status == 0:
      if parsed_result['cotizacionesoutlist']['RespuestaStatus']['mensaje'] == u"No existe cotización para la fecha indicada":
        print color.BOLD + color.YELLOW + "No existe cotización para la fecha indicada: {}".format(args.fecha) + color.END
        sys.exit(2)
      else:
        print color.BOLD + color.RED + "Error al obtener la cotización por favor intente nuevamente" + color.END
        sys.exit(2)
  else:
    print "Error, la moneda {} no es una moneda valida".format(args.moneda)
    listarMonedas()

__main__()