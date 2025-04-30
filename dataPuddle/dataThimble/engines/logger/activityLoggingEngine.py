# Last modified: 2025-03-31 22:57:38
# Version: 0.0.8
from datetime import datetime
from dataclasses import dataclass, field, asdict

from engines.db.arangoBaseEngine import arangoAction
from engines.util.zTextEngine import count_words


def logActivity(dbContentPayload, sesh):

    personaConfObj = sesh["personaStyleConf"]
    personaConfDict = {
        key: value if value else None for key, value in asdict(personaConfObj).items()
    }

    copyThatObj = sesh["copyThatObj"]
    copyThatData = {
        key: value if value else None for key, value in asdict(copyThatObj).items()
    }

    timeStamp = datetime.now()
    dbContentPayload["timeStamp"] = str(timeStamp)
    dbContentPayload["personaConfDict"] = personaConfDict
    dbContentPayload["copyThatData"] = copyThatData
    contentCollection = sesh["copyThatObj"].contentCollection

    funcStatus, funcMsg, sesh = arangoAction(
        arangoHost, arangoDb, arangoUser, arangoUserPwd, dbContentPayload, sesh
    )
    return funcStatus, funcMsg, sesh
