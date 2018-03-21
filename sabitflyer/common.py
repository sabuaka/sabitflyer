def error_parser(response):

    try:
        res_json = response.json()
    except:
        res_json = None

    if response.status_code == 200:  # OK
        return res_json
    else:
        if res_json is not None:
            raise Exception(res_json)
        else:
            errmsg = str('レスポンスを取得できませんでした。')
            raise Exception(errmsg)

    return None

