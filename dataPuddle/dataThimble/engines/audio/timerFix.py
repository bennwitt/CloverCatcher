# Last modified: 2025-03-31 22:24:47
# Version: 0.0.15


def fixTimeIndex(cumStart, start, cumStop, stop, captionsList):
    cumStart = 0
    cumStop = 0
    zeroIncounter = False
    timeList = []
    for indx, l in enumerate(captionsList):
        start = int(l[0])
        stop = int(l[1])
        if indx != 0 and start == 0:
            zeroIncounter = True
            cumStart = cumStop
            cumStop += stop

            timeList.append([cumStart, cumStop])
            continue

        if indx != 0 and stop == 0:
            zeroIncounter = True
            cumStop = cumStart + 1
            cumStart += start

            timeList.append([cumStart, cumStop])
            continue

        if zeroIncounter == False:
            cumStart = start
            cumStop = stop
            timeList.append([cumStart, cumStop])

        else:
            cumStart += start
            cumStop += stop
            timeList.append([cumStart, cumStop])

    return
