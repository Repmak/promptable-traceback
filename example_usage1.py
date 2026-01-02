import promptable_traceback


@promptable_traceback.catch(context_window=5, mask_secrets=True)
def useless_func(var1, var2):
    print(var1, var2)
    var1 = int(var1)  # trigger some error


useless_func("frfr", "ong")
