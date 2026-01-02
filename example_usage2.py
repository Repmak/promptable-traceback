from prompt_log import promptlog_global

promptlog_global(context_window=2)


def useless_func(var1, var2):
    print(var1, var2)
    var1 = int(var1)  # trigger some error
    var2 = var1
    return var1, var2


useless_func("frfr", "ong")
