# -*- coding: utf-8 -*-
"""
Snippets in Flowlauncher.

Simple plugin to save key/value snippets and copy to clipboard.
"""

from flowlauncher import FlowLauncher, FlowLauncherAPI
import sys
import ctypes
import sqlite3
import pyperclip

def getValue(dbName, key) -> []:
    conn = sqlite3.connect(dbName)
    cursor = conn.cursor()

    result = cursor.execute("SELECT key,value FROM snippets WHERE key LIKE concat(?, ? , ?)", ('%', key, '%'))
    value = []
    for row in result:
        value.append(([row[0],row[1]]))
    return value

def saveValue(dbName, key, value):
    conn = sqlite3.connect(dbName)
    cursor = conn.cursor()
    cursor.execute("INSERT OR REPLACE INTO snippets (key, value) VALUES (?, ?)", (key, value))
    conn.commit()
    conn.close()
    copy2clip(dbName, value)

def deleteValue(dbName, key):
    conn = sqlite3.connect(dbName)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM  snippets WHERE key=?", (key,))
    conn.commit()
    conn.close()

def copy2clip(dbName, value):
    """Put snippets into clipboard."""
    pyperclip.copy(value)

class Snippets(FlowLauncher):

    def __init__(self, dbName):
        self.dbName = dbName
        super().__init__()
 
    def query(self, query):
        results = []
        try:
            query = query.strip()
            if len(query) == 0:
                return results

            if ':' in query:
                (key, value) = query.strip().split(':', 1)
                results.append({
                    "Title": "Save Code Snippet",
                    "SubTitle": "Key=" + key + ", Value=" + value,
                    "IcoPath": "assets/snippets.png",
                    "ContextData": [key, value],
                    "JsonRPCAction": {"method": "save", "parameters": [key.strip(), value.strip()], }})
                return results

            list = getValue(self.dbName, query.strip())
            if len(list) == 0:
                clipboard_value = pyperclip.paste()
                display_value = (clipboard_value[:16] + "...") if len(clipboard_value) > 16 else clipboard_value
                if len(clipboard_value) != 0:
                    results.append({
                        "Title": "Save from clipboard",
                        "SubTitle": "Key=" + query.strip() + ", Value=" + display_value,
                        "IcoPath": "assets/snippets.png",
                        "ContextData": [query.strip(), clipboard_value],
                        "JsonRPCAction": {"method": "save", "parameters": [query.strip(), clipboard_value], }})
                return results

            for item in list:
                key = item[0]
                text = item[1]
                results.append({
                    "Title": "⭐ " + key,
                    "SubTitle": "[Snippet] Copy to clipboard with value: " + text,
                    "IcoPath": "assets/snippets.png",
                    "ContextData": [query.strip(), text],
                    "JsonRPCAction": {"method": "copy", "parameters": [text], }})
        except:
            exec_info = sys.exc_info()
            print("Exception: ", exec_info[0], exec_info[1])
            results.append({
                "Title": "Code Snippets Error",
                "SubTitle": "Please, Verify and try again",
                "IcoPath": "assets/snippets.png", "ContextData": "ctxData"})

        return results
    
    def context_menu(self, data):
        results = []
        results.append({
                        "Title": "Delete Code Snippet",
                        "SubTitle": "Key=" + data[0] + ", Value=" + data[1],
                        "IcoPath": "assets/snippets.png",
                        "JsonRPCAction": {"method": "delete", "parameters": [data[0]], }})
        results.append({
                "Title": "Save/Update Code Snippet",
                "SubTitle": "Key=" + data[0] + ", Value=" + data[1],
                "IcoPath": "assets/snippets.png", 
                "JsonRPCAction": {"method": "save", "parameters": [data[0], data[1]], }})
        return results

    def copy(self, value):
        """Copy Snippets to clipboard."""
        copy2clip(self.dbName, value)

    def save(self, key, value):
        """Save Snippets into sqlite"""
        saveValue(self.dbName, key.strip(), value.strip())

    def delete(self, key):
        """Delete Snippets from sqlite"""
        deleteValue(self.dbName, key.strip())

if __name__ == "__main__":
    Snippets()
