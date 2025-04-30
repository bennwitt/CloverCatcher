# Last modified: 2025-04-02 14:12:53
# Version: 0.0.64


def appendToWorkLedger(workLedgerLog, workItemsList):
    with open(workLedgerLog, "a", encoding="utf-8") as wll:
        for item in workItemsList:
            wll.write(item.strip() + "\n")
