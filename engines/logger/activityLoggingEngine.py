# Last modified: 2025-03-01 04:53:01
# Version: 0.0.9
from datetime import datetime
from dataclasses import dataclass, field, asdict
from typing import List, Optional, Dict, Tuple, Any, Union
from engines.arango.arangoBaseEngine import arangoAction
from engines.util.zTimeEngine import getNowDateTime


def logActivity(dbContentPayload, sesh):

    personaConfObj = sesh["personaStyleConf"]
    personaConfDict = {
        key: value if value else None for key, value in asdict(personaConfObj).items()
    }

    copyThatObj = sesh["copyThatObj"]
    copyThatData = {
        key: value if value else None for key, value in asdict(copyThatObj).items()
    }

    dbContentPayload["timeStamp"] = getNowDateTime()
    dbContentPayload["personaConfDict"] = personaConfDict
    dbContentPayload["copyThatData"] = copyThatData
    contentCollection = sesh["copyThatObj"].contentCollection
    funcStatus, funcMsg, sesh = arangoAction(
        clientDb, contentCollection, dbContentPayload, sesh
    )
    return funcStatus, funcMsg, sesh
