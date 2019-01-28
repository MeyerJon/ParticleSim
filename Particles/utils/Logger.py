

V_SYS_LEVEL = 1
V_WARNING_LEVEL = 2
V_INFO_LEVEL = 2
V_ERROR_LEVEL = 3
V_EXCEPT_LEVEL = 4

verbose_level = 3
output_file = "./logs"


def set_verbose_level(lvl):
    if (lvl > 0):
        verbose_level = lvl

def set_output_file(file):
    output_file = file

def clear_logfile():
    with open(output_file, 'w') as logfile:
        logfile.write('')


def log(msg):
    with open(output_file, 'a') as logfile:
        logfile.write(msg)
        logfile.write('\n')


def log_info(msg):
    message = "[INFO] " + msg
    log(message)

    if (verbose_level >= V_INFO_LEVEL):
        print(message)

def log_system(msg):
	message = "[SYSTEM] " + msg
	log(message)

	if (verbose_level >= V_SYS_LEVEL):
		print(message)

def log_warning(msg):
    message = "[WARNING] " + msg
    log(message)

    if (verbose_level >= V_WARNING_LEVEL):
        print(message)

def log_error(msg):
    message = "[ERROR] " + msg
    log(message)

    if (verbose_level >= V_ERROR_LEVEL):
        print(message)

def log_exception(e):
    message = " + [EXCEPTION] " + str(e)
    log(message)

    if (verbose_level >= V_EXCEPT_LEVEL):
        print(message)


def log_custom(tag, msg):
    message = "[" + tag.upper() + "]" + " " + msg
    log(message)

    if verbose_level >= V_SYS_LEVEL:
            print(message)
