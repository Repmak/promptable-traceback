from promptable_log import catch


@catch(context_window=5, mask_secrets=True)
def useless_func(var1, var2):
    print(var1, var2)
    var1 = int(var1)  # trigger some error
    var2 = var1
    return var1, var2


useless_func("frfr", "ong")
