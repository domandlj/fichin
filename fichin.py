import requests
import pandas as pd
from datetime import date
import re

def post_token(username: str, password: str) -> dict:
    url = "https://api.invertironline.com/token"
    headers = {
        "Content-Type": "application/x-www-form-urlencoded"
    }
    data = {
        "username": username,
        "password": password,
        "grant_type": "password"
    }

    response = requests.post(url, headers=headers, data=data)

    if response.status_code == 200:
        return response.json()  # contiene el access_token y más info
    else:
        raise Exception(f"Error {response.status_code}: {response.text}")


def get_estadocuenta(token: str) -> dict:
    """
    Llama al endpoint GET api/v2/estadocuenta de IOL
    y devuelve la respuesta como un dict (JSON).

    Parámetros:
        token (str): Bearer token obtenido previamente.

    Retorna:
        dict: Datos del portafolio.
    """
    url = "https://api.invertironline.com/api/v2/estadocuenta"
    headers = {
        "Authorization": f"Bearer {token}"
    }

    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(f"Error {response.status_code}: {response.text}")

def mostrar_estado_cuenta(token):
    data = get_estadocuenta(token)
    cuentas = data["cuentas"]
    estadisticas = data["estadisticas"]
    total_en_pesos = data["totalEnPesos"]

    # Procesar resumen de cuentas
    df_cuentas = pd.DataFrame([{
        "Número": c["numero"],
        "Tipo": c["tipo"],
        "Moneda": c["moneda"],
        "Disponible": c["disponible"],
        "Comprometido": c["comprometido"],
        "Saldo": c["saldo"],
        "Títulos Valorizados": c["titulosValorizados"],
        "Total": c["total"],
        "Margen Descubierto": c["margenDescubierto"],
        "Estado": c["estado"]
    } for c in cuentas])

    # Detalle por liquidación de cada cuenta
    detalles_saldos = []
    for cuenta in cuentas:
        for saldo in cuenta["saldos"]:
            detalles_saldos.append({
                "Número": cuenta["numero"],
                "Tipo": cuenta["tipo"],
                "Liquidación": saldo["liquidacion"],
                "Saldo": saldo["saldo"],
                "Comprometido": saldo["comprometido"],
                "Disponible": saldo["disponible"],
                "Disponible Operar": saldo["disponibleOperar"]
            })
    df_saldos = pd.DataFrame(detalles_saldos)

    # Estadísticas
    df_estadisticas = pd.DataFrame(estadisticas)

    # Mostrar todo
    print("Resumen de cuentas:")
    #display(df_cuentas)
    print("\nDetalle de saldos por tipo de liquidación:")
    #display(df_saldos)
    print("\nEstadísticas:")
    #display(df_estadisticas)
    print(f"\nTotal en pesos: {total_en_pesos}")

    return df_cuentas, df_saldos, df_estadisticas


def get_portafolio_ars(token: str) -> dict:
    """
    Llama al endpoint GET api/v2/portafolio/argentina de IOL
    y devuelve la respuesta como un dict (JSON).

    Parámetros:
        token (str): Bearer token obtenido previamente.

    Retorna:
        dict: Datos del portafolio.
    """
    url = "https://api.invertironline.com/api/v2/portafolio/argentina"
    headers = {
        "Authorization": f"Bearer {token}"
    }

    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(f"Error {response.status_code}: {response.text}")
    


def get_valores(token):
    portfolio = get_portafolio_ars(token)
    
    valores = list(map(lambda item : {
        "ticker":item["titulo"]["simbolo"] , 
        "monto":item["cantidad"]*item["ultimoPrecio"]/100}, 
        portfolio["activos"]))

    total = sum(list(map(lambda item:item["monto"], valores)))

    for item in valores:
        item["peso"]=item["monto"]/total
    return valores


def get_cotizaciones(token: str, ticker : str) -> dict:
    """
    Llama al endpoint GET /api/v2/{Mercado}/Titulos/{Simbolo}/Cotizacion de IOL
    y devuelve la respuesta como un dataframe.

    Parámetros:
        token (str): Bearer token obtenido previamente.
        ticker (str) : ticekr del activo

    Retorna:
        dict. cotizaciones 
    """
    
    url = f"https://api.invertironline.com/api/v2/bCBA/Titulos/{ticker}/Cotizacion"
    headers = {
        "Authorization": f"Bearer {token}"
    }

    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        df = pd.DataFrame([response.json()])
        df = df[["descripcionTitulo","ultimoPrecio","apertura","maximo","minimo","cierreAnterior","plazo"]]
        return df
    else:
        raise Exception(f"Error {response.status_code}: {response.text}")





def descargar_serie_historica(token : str, mercado: str, simbolo: str, fecha_desde: date, fecha_hasta: date, ajustada: str) -> dict:
    """
    Descarga la serie histórica de cotizaciones desde la API.

    Parámetros:
    - mercado: 'bCBA' o 'rOFX'
    - simbolo: símbolo del título (por ejemplo, 'GGAL')
    - fecha_desde: objeto datetime.date
    - fecha_hasta: objeto datetime.date
    - ajustada: 'ajustada' o 'sinAjustar'

    Devuelve:
    - Diccionario con los datos de la serie histórica
    """
    # Validación simple
    if mercado not in ('bCBA', 'rOFX'):
        raise ValueError("El mercado debe ser 'bCBA' o 'rOFX'")
    if ajustada not in ('ajustada', 'sinAjustar'):
        raise ValueError("El valor de 'ajustada' debe ser 'ajustada' o 'sinAjustar'")

    fecha_desde_str = fecha_desde.strftime('%Y-%m-%d')
    fecha_hasta_str = fecha_hasta.strftime('%Y-%m-%d')

    url = f"https://api.invertironline.com/api/v2/{mercado}/Titulos/{simbolo}/Cotizacion/seriehistorica/{fecha_desde_str}/{fecha_hasta_str}/{ajustada}"

    headers = {
        "Accept": "application/json",
        "Authorization": f"Bearer {token}"
    }

    response = requests.get(url, headers=headers)

    if response.status_code != 200:
        raise Exception(f"Error {response.status_code}: {response.text}")

    data = response.json()
    
    # Convertir a DataFrame
    df = pd.DataFrame(data)

    # Convertir 'fechaHora' a datetime (y renombrar a 'fecha')
    if 'fechaHora' in df.columns:
        df['fecha'] = pd.to_datetime(df['fechaHora'], format='mixed').dt.date
        df = df.drop(columns=['fechaHora'])

    # Reordenar columnas (fecha primero si existe)
    cols = ['fecha'] + [col for col in df.columns if col != 'fecha']
    df = df[cols]

    return df



"""
    Operar.
"""


def get_cotizacion(token: str, ticker : str) -> dict:
    """
    Llama al endpoint GET /api/v2/{Mercado}/Titulos/{Simbolo}/Cotizacion de IOL
    y devuelve la respuesta como un dict (JSON).

    Parámetros:
        token (str): Bearer token obtenido previamente.
        ticker (str) : ticekr del activo

    Retorna:
        dict. cotizaciones 
    """
    
    url = f"https://api.invertironline.com/api/v2/bCBA/Titulos/{ticker}/Cotizacion"
    headers = {
        "Authorization": f"Bearer {token}"
    }

    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(f"Error {response.status_code}: {response.text}")



def get_cotizacion_min(token, ticker):
    return get_cotizacion(token, ticker)["minimo"]


from datetime import datetime, timedelta, timezone

# Hora actual en UTC
ahora = datetime.now(timezone.utc)

# Sumarle una hora
validez = ahora + timedelta(hours=1)

# Formatear como string ISO 8601
validez_str = validez.isoformat()


def post_comprar_monto_px_mercado(token, monto, ticker):
    url = "https://api.invertironline.com/api/v2/operar/Comprar"
  
    
    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "Authorization": f"Bearer {token}"
    }
    
    data = {
        "mercado": "bCBA",
        "simbolo": ticker,
        "validez": validez_str,
        "monto": monto,
        "plazo":"t1",
        "precio": get_cotizacion_min(token, ticker),
        "tipoOrden": "precioMercado",
    }

    response = requests.post(url, headers=headers, data=data)

    if 200 <= response.status_code < 300:
        return response.json() 
    else:
        raise Exception(f"Error {response.status_code}: {response.text}")




def parse_ticker(ticker):
    # Caso con punto separador
    if '.' in ticker:
        subyacente_strike, mes_tipo = ticker.split('.')
        match = re.match(r"([A-Z]+)(\d+(?:\.\d+)?)", subyacente_strike)
        if match:
            subyacente, strike = match.groups()
        else:
            return None
    else:
        # Sin punto: buscar subyacente + strike + sufijo de 1 o 2 letras
        match = re.match(r"([A-Z]+)(\d+(?:\.\d+)?)([A-Z]{1,2})$", ticker)
        if match:
            subyacente, strike, mes_tipo = match.groups()
        else:
            return None

    # Decodificar mes solo si se puede
    letra_mes = mes_tipo[0]
    meses_call = {
        'A': 'Enero', 'B': 'Febrero', 'C': 'Marzo', 'D': 'Abril',
        'E': 'Mayo', 'F': 'Junio', 'G': 'Julio', 'H': 'Agosto',
        'I': 'Septiembre', 'J': 'Octubre', 'K': 'Noviembre', 'L': 'Diciembre'
    }
    mes = meses_call.get(letra_mes, 'Desconocido')

    return {
        'simbolo': ticker,
        'subyacente': subyacente,
        'strike': float(strike),
        'mes': mes,
    }


def get_cotizaciones_subyacentes(df_calls):
    cots = {}
    for ticker in set(df_calls["subyacente"]):
        cots[ticker] = get_cotizacion(TOKEN, ticker)["ultimoPrecio"]
    return cots


def get_opciones_call(token: str):
    """
    Llama al endpoint GET api/v2/estadocuenta de IOL
    y devuelve la respuesta como un dict (JSON).

    Parámetros:
        token (str): Bearer token obtenido previamente.

    Retorna:
        dict: Datos del portafolio.
    """
    url = "https://api.invertironline.com//api/v2/Cotizaciones/Opciones/Calls/Argentina"
    headers = {
        "Authorization": f"Bearer {token}"
    }

    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        data = response.json()
        df = pd.DataFrame(data["titulos"])
        puntas_df = df["puntas"].apply(pd.Series)
        puntas_df = puntas_df.add_prefix("puntas_")
        
        df = df.drop(columns=["puntas"]).join(puntas_df)
        df = df[df["volumen"]>0]
        
        
        # Aplicar la función y expandir el resultado como columnas
        parsed_cols = df["simbolo"].apply(parse_ticker).apply(pd.Series)
        
        # Unir las columnas parseadas al DataFrame original
        parsed_cols["prima"] = df["ultimoPrecio"]

                
        mapa_tickers = {
            "ALUC": "ALUA",
            "BHIC": "BMA",
            "BYMC": "BYMA",
            "COMC": "COME",
            "GFGC": "GGAL",
            "METC": "METR",
            "PAMC": "PAMP",
            "TXAC": "TXAR",
            "YPFC": "YPFD"
        }
        
        # Suponiendo que ya tenés el DataFrame df
        parsed_cols["subyacente"] = parsed_cols["subyacente"].replace(mapa_tickers)

        px_subyacentes = get_cotizaciones_subyacentes(parsed_cols)
        
        parsed_cols["px_subyacente"] = parsed_cols["subyacente"].map(px_subyacentes)
        return parsed_cols

        
    else:
        raise Exception(f"Error {response.status_code}: {response.text}")
