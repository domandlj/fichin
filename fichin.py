import requests
import pandas as pd

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