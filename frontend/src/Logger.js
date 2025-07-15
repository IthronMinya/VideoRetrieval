import { get } from "svelte/store";
import { username } from "./stores.js";


export const loggingInterval = 30;
const logCountToTriggerSend = 300;
let logging = true;
let user = get(username);
const serverUrl = `${window.location.origin}/append_user_log`;


username.subscribe((value) => { user = value; });


function getServerFormattedTimestamp() {
  const now = new Date();

  const year = now.getFullYear();
  const month = String(now.getMonth() + 1).padStart(2, "0"); // Months are zero-based
  const day = String(now.getDate()).padStart(2, "0");
  const hours = String(now.getHours()).padStart(2, "0");
  const minutes = String(now.getMinutes()).padStart(2, "0");
  const seconds = String(now.getSeconds()).padStart(2, "0");
  const milliseconds = String(now.getMilliseconds()).padStart(3, "0");

  return `${year}${month}${day}${hours}${minutes}${seconds}${milliseconds}000`;
}


window.addEventListener("beforeunload", (event) => { submitLogs(); });


class Mutex {
    constructor() {
        this.locked = false;
	this.queue = [];
    }

    async lock() {
	while (this.locked) {
	    await new Promise((resolve) => this.queue.push(resolve));
	}
	this.locked = true;
    }

    unlock() {
	this.locked = false;
	if (this.queue.length > 0) {
	    const nextResolve = this.queue.shift();
	    nextResolve();
	}
    }
}


let logs = [];
const mutex = new Mutex();


export function preventLogging() {
    logging = false;
}


export function logEvent(action, value = null, additionalArgs = null) {
    if (!logging) { return; }

    const baseLog = {
        "action": action,
        "timestamp": getServerFormattedTimestamp(),
    }
    let logEntry;

    if (value === null) {
        logEntry = baseLog;
    } else {
        if (additionalArgs === null) {
            logEntry = { ...baseLog, "value": value }
        } else {
            logEntry = { ...baseLog, "value": value, ...additionalArgs }
        }
    }

    logs.push(logEntry);
    console.log(logEntry);

    if (logs.length >= logCountToTriggerSend) {
	submitLogs();
    }
}


export async function submitLogs() {
    if (!logging) { return; }

    // Aquire lock for sending the data
    await mutex.lock();

    // Get the logs then were not sent yet
    const logsToSend = logs.slice();
    if (logsToSend.length === 0) {
	mutex.unlock();
	return;
    }

    try {
        // Submit the logs to the server
        const response = await fetch(serverUrl, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({"username": user, "log": logsToSend }),
        });
        const responseText = await response.text();

        // Check for success (checking the text is needed as the server responds with 200 even in case of some errors)
        if (response.ok && responseText.includes("Success")) {
            logs = logs.slice(logsToSend.length);
        } else {
            console.error("Failed to submit logs:", responseText);
        }
    } catch (error) {
        console.error("Error submitting logs:", error);
    } finally {
        mutex.unlock();
    }
}
