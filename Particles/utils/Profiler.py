from Particles.utils import Logger


PROFILER_DATA = dict()


def make_profiler_category(c):

    PROFILER_DATA[c] = list()


def add_profiler_data(category, value):

    try:
        PROFILER_DATA[category].append(value)
    except KeyError:
        Logger.log_warning("No profiler category '{}'.".format(category))


def get_profiler_category(category):

    try:
        return PROFILER_DATA[category]
    except KeyError:
        Logger.log_warning("No profiler category '{}'.".format(category))


def get_numeric_category_avg(category):
    
    try:
        avg = 0
        for i in PROFILER_DATA[category]:
            avg += i
        avg /= len(PROFILER_DATA[category])
        return avg
    except KeyError:
        Logger.log_warning("No profiler category '{}'.".format(category))
    except ZeroDivisionError:
        Logger.log_warning("Empty profiler category '{}'. Cannot compute average.".format(category))
    return None
