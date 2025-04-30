# Last modified: 2025-04-29 17:55:11
# Version: 0.0.119
from dataclasses import dataclass, field, asdict
from typing import List, Dict, Any, Optional, Union
import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))


@dataclass
class PersonaData:
    personaToggle: bool = False
    assistantName: str = "CopyWriterClaudeHopkins"
    assistantTaskDirective: str = (
        "Generate a variation based on the provided source content"
    )
    numberOfVariations: int = 2
    levelOfVariation: str = "Faithful Rewrite"
    lengthOfVariation: str = "Same Length"
    knowledgeScope: bool = True
    personaToggle: bool = False
    rolePersona: str = "empathetic storyteller emotional influencer and humanist"
    targetAudience: str = "one time donors who may convert to repeat supporters"
    responsePurpose: str = (
        "use storytelling that evokes emotional responses forging personal connections that bypass rational filtering"
    )
    domainTopic: str = (
        "neuroscience of motivation behavioral psychology with the principles of reciprocity"
    )
    responseLength: str = "about the same as the source content provided"
    responseTone: str = (
        "In-depth domain coverage referencing significant acronyms historical context while ensuring inclusive person-first language"
    )
    responseFormat: str = (
        "exactly as the provided template, mirror the layout, copy the composition of the provided example structure"
    )
    energyLevel: str = "purpose-driven emphasizing urgent reciprocity"
    modelTemp: float = 0.3
    modelChoice: str = "gpt-4o"
    maxTokens: int = 500
    promptContentDict: Optional[Dict[str, Any]] = field(default_factory=lambda: {})

    def update(self, **kwargs):
        """Update multiple fields dynamically"""
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)

    def reset(self):
        """Reset all fields to their default values"""
        self.__dict__.update(PersonaData().__dict__)


@dataclass
class UserData:
    authToken: str = None
    userID: str = None
    userEmailAddress: str = None
    authStatus: bool = None
    orgID: str = None
    clientName: str = None
    clientStorage: Optional[str] = None
    appName: str = None
    appStorage: Optional[str] = None
    mediaLibraryRoot: Optional[str] = None
    contentStorageRoot: Optional[str] = None
    contentType: Optional[str] = None
    contentStatus: Optional[str] = None
    contentData: Optional[Dict[str, Any]] = field(default_factory=lambda: {})
    aiDojoContentList: List[Any] = field(default_factory=list)
    aiDojoData: Optional[Dict[str, Any]] = field(default_factory=lambda: {})
    contentText: Optional[str] = None
    contentTextEmbeddings: Optional[List[float]] = field(default_factory=list)
    dataBag: Optional[Union[List[Any], Dict[str, Any]]] = None
    mediaId: Optional[str] = None
    externalId: Optional[str] = None
    txtList: List[Any] = field(default_factory=list)
    userContentInput: Optional[str] = None
    userContentGenOutput: Optional[str] = None
    fullPrompt: Optional[str] = None
    logger: List[Any] = field(default_factory=list)
    activityType: Optional[str] = None
    appDb: Optional[str] = None
    clientDb: Optional[str] = None
    userDirectory: Optional[str] = None
    accessLogs: Optional[str] = None
    activityLogs: Optional[str] = None
    contentCollection: Optional[str] = None
